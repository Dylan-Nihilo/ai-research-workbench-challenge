import os
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .schemas import Task, TaskInput, Event, ErrorDetail
from .research import configured, research, ResearchError
from .storage import TaskStore


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def create_app(database_path: Path | None = None) -> FastAPI:
    default_path = Path(__file__).resolve().parents[1] / ".data" / "tasks.sqlite3"
    store = TaskStore(database_path or Path(os.environ.get("RESEARCH_DB_PATH", default_path)))
    app = FastAPI(title="Research Workbench", version="0.1.0")
    app.state.store = store

    def event(task, stage, message):
        task.stage = stage
        task.events.append(Event(id=str(uuid4()), stage=stage, message=message,
                                 created_at=datetime.now(timezone.utc)))
        store.save(task)

    # A development server reload cannot resume an in-flight external request.
    for interrupted in store.list():
        if interrupted.status in {"queued", "running"}:
            interrupted.status = "failed"
            interrupted.error = ErrorDetail(code="interrupted", message="服务重启中断了调研，请重试。")
            event(interrupted, "已中断", interrupted.error.message)

    def execute(task_id):
        task = store.get(task_id)
        try:
            event(task, "联网检索与分析", "模型正在检索公开资料并整理有引用的报告。")
            task.report, task.sources = research(task.question)
            task.status = "completed"
            event(task, "完成", f"报告已保存，包含 {len(task.sources)} 个引用来源。")
        except Exception as exc:
            task.status = "failed"
            task.error = ErrorDetail(code=exc.code if isinstance(exc, ResearchError) else "research_failed",
                                     message=exc.message if isinstance(exc, ResearchError) else "调研处理失败，请重试。")
            event(task, "失败", task.error.message)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError):
        return error(422, "invalid_input", "请输入 1 至 2000 字的调研问题。")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/tasks", response_model=Task, status_code=201)
    def create_task(body: TaskInput):
        return store.create(body.question)

    @app.get("/api/tasks", response_model=list[Task])
    def list_tasks():
        return store.list()

    @app.get("/api/tasks/{task_id}", response_model=Task)
    def get_task(task_id: str):
        task = store.get(task_id)
        return task if task else error(404, "not_found", "未找到该任务。")

    @app.patch("/api/tasks/{task_id}", response_model=Task)
    async def update_task(task_id: str, body: TaskInput):
        task = store.get(task_id)
        if task is None:
            return error(404, "not_found", "未找到该任务。")
        if task.status != "draft":
            return error(409, "task_locked", "任务已经开始，请创建新任务。")
        task.question = body.question
        store.save(task)
        return task

    @app.delete("/api/tasks/{task_id}", status_code=204)
    async def delete_task(task_id: str):
        task = store.get(task_id)
        if task is None:
            return error(404, "not_found", "未找到该任务。")
        if task.status in {"queued", "running"}:
            return error(409, "task_active", "请先结束任务再删除。")
        store.delete(task_id)
        return Response(status_code=204)

    @app.post("/api/tasks/{task_id}/run")
    async def run_task(task_id: str, background: BackgroundTasks):
        task = store.get(task_id)
        if task is None:
            return error(404, "not_found", "未找到该任务。")
        if task.status not in {"draft", "failed"}:
            return error(409, "task_locked", "任务已经开始或完成，请创建新任务。")
        if not configured():
            return error(503, "provider_not_configured", "请在后端配置 OPENAI_API_KEY 后重新启动服务。")
        if sum(t.status in {"running", "queued"} for t in store.list()) >= 3:
            return error(429, "capacity_reached", "同时最多执行三个调研，请稍后重试。")
        task.status, task.error, task.report, task.sources, task.events = "running", None, None, [], []
        event(task, "理解问题", "已提交问题，将使用真实模型和公开网络资料。")
        background.add_task(execute, task.id)
        return JSONResponse(task.model_dump(mode="json"), status_code=202)

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel_task(task_id: str):
        if store.get(task_id) is None:
            return error(404, "not_found", "未找到该任务。")
        # Reserved extension point; cancellation is optional for this assessment.
        return error(501, "cancellation_not_implemented", "当前无法取消任务。")

    return app
