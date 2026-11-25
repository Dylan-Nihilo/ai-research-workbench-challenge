# 万象硅芯 · AI 信息调研工作台

这是研发实习生工程考核的起始项目。请在现有前后端框架上补齐指定功能，通过 Fork 和 PR 交付。

完整要求：[任务书 PDF](docs/TASK.pdf) · [任务说明](docs/TASK.md) · [现有接口与功能边界](docs/BASELINE.md)

## 已提供

- React + TypeScript + Vite 前端：问题输入、任务创建、任务列表、基础详情、手动刷新和 API 请求封装。
- FastAPI 后端：健康检查、任务创建/读取/编辑/删除、输入校验和统一错误格式。
- SQLite 任务存储，以及报告、来源、事件和错误的数据字段。
- Docker Compose 运行环境、基础回归测试、依赖锁定文件、GitHub Actions 和交付模板。

当前支持创建任务、后台联网调研、报告与编号来源、状态自动刷新和失败重试。后端调用真实 OpenAI Responses API 的 web_search；未配置密钥时返回 503，不生成模拟报告。取消接口仍未启用。启动前复制 `.env.example` 为 `.env`，填写 `OPENAI_API_KEY`，可设置 `OPENAI_MODEL`（默认 gpt-4.1，需要支持 web_search）。模型和检索会产生费用。当前验证状态、真实演示步骤及限制见 [交付说明](docs/DELIVERY.md)。

## 任务目标

让用户在网页输入一个调研问题，系统自行查找公开资料、调用真实模型进行分析，并展示有来源的调研结果。

完成这一目标需要打通问题理解、资料获取、模型分析和前端呈现。如何拆解步骤、选择 provider 与信息获取方式、组织页面和后端逻辑，由你决定。请使用 Claude 或 Codex 参与开发，并用真实运行结果说明完成情况。

现有代码是起点。可以按需调整页面、接口和数据结构，同时更新相关调用与验证。`docs/BASELINE.md` 仅说明已有代码，不是额外的功能验收清单。

## Docker 启动

本机只需要 Docker 和 Docker Compose 2.24+（Docker Desktop 已包含）。Node.js、Python、npm/pip 依赖和数据库都在容器内，不需要在本机安装。

在仓库根目录运行：

```sh
docker compose up -d --build --wait
```

默认打开 [前端页面](http://localhost:5173)，后端接口文档位于 [API docs](http://localhost:8000/docs)。首次构建需要联网下载基础镜像与依赖。

端口被占用时，可将 `.env.example` 复制为 `.env`，修改 `WEB_PORT` 或 `API_PORT` 后再启动。`.env` 也可用于将未来的 provider 配置传入后端；前端容器不会读取此文件。

```sh
docker compose ps
docker compose logs -f
docker compose down
```

SQLite 保存在 `research-data` 数据卷中，普通停止或重建容器不会删除任务数据。

## 开发与检查

前后端源码挂载到容器，修改代码后可自动重载。修改依赖声明、锁定文件或 Dockerfile 后，再执行 `docker compose up -d --build --wait`。

所有检查都在容器中运行：

```sh
docker compose run --rm --no-deps backend python -m unittest discover -s tests -v
docker compose run --rm --no-deps frontend npm run build
docker compose exec -T frontend node tests/smoke.mjs
```

最后一条命令需要服务已启动，会通过前端代理检查后端健康、任务 CRUD 和输入校验，并清理测试任务。后端测试也覆盖调研流程与引用解析；离线 fixture 不替代真实联网验收。当前验证状态见交付说明。

## Fork 与 PR

1. Fork 招聘邀请中的官方仓库。
2. Clone 自己的 Fork，从邀请指定的标签创建 `submission/候选人编号` 分支。
3. 完成改造，推送至自己的 Fork，向官方仓库的 `main` 发起 PR。
4. 填写 PR 模板，补齐交付文档，在 PR 中注明最终 commit SHA。

PR 标题：`[AI Intern][候选人编号] 信息调研工作台`。允许先开 Draft PR；完成后再转为 Ready for review。提交截止时刻以招聘邀请为准。

可使用 `docs/DELIVERY.md` 与 `docs/AI_COLLABORATION.md` 简要说明交付和协作过程，也可在 PR 中直接说明。不得提交真实凭据、私人账号信息或未脱敏聊天。公开 Fork 和 PR 对外可见；无法接受公开提交时，请在开始前通过招聘沟通渠道说明。

官方仓库保持统一起点，作业 PR 只用于评审，不合入题目主分支。外部 PR 的 Actions 可能等待招聘方批准，这不视为候选人失败。

操作参考：[从 Fork 创建 PR](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork)、[Fork 的可见性](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-permissions-and-visibility-of-forks)。
