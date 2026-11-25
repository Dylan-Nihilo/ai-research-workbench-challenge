import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .schemas import Task, TaskInput
from .storage import TaskStore


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def create_app(database_path: Path | None = None) -> FastAPI:
    default_path = Path(__file__).resolve().parents[1] / ".data" / "tasks.sqlite3"
    store = TaskStore(database_path or Path(os.environ.get("RESEARCH_DB_PATH", default_path)))
    app = FastAPI(title="Research Workbench", version="0.1.0")
    app.state.store = store

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
    def update_task(task_id: str, body: TaskInput):
        task = store.get(task_id)
        if task is None:
            return error(404, "not_found", "未找到该任务。")
        if task.status != "draft":
            return error(409, "task_locked", "任务已经开始，请创建新任务。")
        task.question = body.question
        store.save(task)
        return task

    @app.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: str):
        task = store.get(task_id)
        if task is None:
            return error(404, "not_found", "未找到该任务。")
        if task.status in {"queued", "running"}:
            return error(409, "task_active", "请先结束任务再删除。")
        store.delete(task_id)
        return Response(status_code=204)

    @app.post("/api/tasks/{task_id}/run")
    def run_task(task_id: str):
        if store.get(task_id) is None:
            return error(404, "not_found", "未找到该任务。")
        # The research pipeline is an explicit candidate task, not a simulated success.
        return error(501, "research_not_implemented", "调研服务暂不可用。")

    @app.post("/api/tasks/{task_id}/cancel")
    def cancel_task(task_id: str):
        if store.get(task_id) is None:
            return error(404, "not_found", "未找到该任务。")
        # Reserved extension point; cancellation is optional for this assessment.
        return error(501, "cancellation_not_implemented", "当前无法取消任务。")

    return app
