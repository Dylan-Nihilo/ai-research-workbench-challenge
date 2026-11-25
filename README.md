# 万象硅芯 · AI 信息调研工作台

这是研发实习生工程考核的起始项目。请在现有前后端框架上补齐指定功能，通过 Fork 和 PR 交付。

完整要求：[任务书 PDF](docs/TASK.pdf) · [任务说明](docs/TASK.md) · [现有接口与功能边界](docs/BASELINE.md)

## 已提供

- React + TypeScript + Vite 前端：问题输入、任务创建、任务列表、基础详情、手动刷新和 API 请求封装。
- FastAPI 后端：健康检查、任务创建/读取/编辑/删除、输入校验和统一错误格式。
- SQLite 任务存储，以及报告、来源、事件和错误的数据字段。
- 基础回归测试、依赖锁定文件、GitHub Actions 和交付模板。

当前可以完成“创建任务 → 保存 → 列表/详情查看 → 刷新后继续查看”。运行与取消接口暂时返回明确的 `501`；项目不会生成模拟的成功调研报告，也不会调用任何外部模型或检索服务。

## 任务目标

让用户在网页输入一个调研问题，系统自行查找公开资料、调用真实模型进行分析，并展示有来源的调研结果。

完成这一目标需要打通问题理解、资料获取、模型分析和前端呈现。如何拆解步骤、选择 provider 与信息获取方式、组织页面和后端逻辑，由你决定。请使用 Claude 或 Codex 参与开发，并用真实运行结果说明完成情况。

现有代码是起点。可以按需调整页面、接口和数据结构，同时更新相关调用与验证。`docs/BASELINE.md` 仅说明已有代码，不是额外的功能验收清单。

## 本地启动

需要 Python 3.11+、Node.js 22.12+。所有命令从仓库根目录开始，后端和前端分别在两个终端运行。

后端（macOS / Linux）：

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Windows 可使用 `.venv\Scripts\Activate.ps1` 激活环境。默认数据库位于 `backend/.data/tasks.sqlite3`；可通过后端环境变量 `RESEARCH_DB_PATH` 指定其他路径。

前端：

```sh
cd frontend
npm ci
npm run dev
```

访问终端显示的地址，默认是 `http://127.0.0.1:5173`。Vite 会把 `/api` 代理到 `http://127.0.0.1:8000`，不需要在浏览器中保存后端地址或密钥。后端端口不同时，可以在启动 Vite 前设置 `BACKEND_URL` 环境变量。

后端接口文档：`http://127.0.0.1:8000/docs`。`npm run build` 检查并生成前端静态产物；本任务使用上述开发启动流程验收，不要求部署线上服务。

## 基础检查

```sh
cd backend
source .venv/bin/activate
python -m unittest discover -s tests -v
```

```sh
cd frontend
npm run build
```

现有测试只保证起始框架的基础能力。请对自己的实现做适当验证，并说明验证方法。最终交付需要展示真实资料获取和模型调用。

## Fork 与 PR

1. Fork 招聘邀请中的官方仓库。
2. Clone 自己的 Fork，从邀请指定的标签创建 `submission/候选人编号` 分支。
3. 完成改造，推送至自己的 Fork，向官方仓库的 `main` 发起 PR。
4. 填写 PR 模板，补齐交付文档，在 PR 中注明最终 commit SHA。

PR 标题：`[AI Intern][候选人编号] 信息调研工作台`。允许先开 Draft PR；完成后再转为 Ready for review。提交截止时刻以招聘邀请为准。

可使用 `docs/DELIVERY.md` 与 `docs/AI_COLLABORATION.md` 简要说明交付和协作过程，也可在 PR 中直接说明。不得提交真实凭据、私人账号信息或未脱敏聊天。公开 Fork 和 PR 对外可见；无法接受公开提交时，请在开始前通过招聘沟通渠道说明。

官方仓库保持统一起点，作业 PR 只用于评审，不合入题目主分支。外部 PR 的 Actions 可能等待招聘方批准，这不视为候选人失败。

操作参考：[从 Fork 创建 PR](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork)、[Fork 的可见性](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-permissions-and-visibility-of-forks)。
