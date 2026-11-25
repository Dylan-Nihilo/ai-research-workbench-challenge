# 起始项目参考

这份文档只介绍当前代码，任务目标以 TASK.md 为准。已有接口和预留字段不代表必须逐项实现；可以按需要调整，并同步调用方与验证。

## 已实现的部分

前端位于 `frontend/`，后端位于 `backend/`，通过根目录的 Docker Compose 一起启动。前端能创建任务、查看列表与详情、手动刷新；后端提供 SQLite 存储和 CRUD，数据库保存在 Docker 数据卷中。页面刷新、后端重新启动后，已保存的任务仍存在。

起始项目不做网页检索、模型调用或报告生成。点击“开始调研”会收到明确的服务不可用错误，任务仍为 `draft`。这是一项公开的待完成功能，不是环境故障。

## 现有 HTTP 契约

- `GET /api/health`：返回 `{"status":"ok"}`。
- `POST /api/tasks`：输入 `{"question":"..."}`，返回 201 和新建的 `Task`。只创建草稿，不执行调研。
- `GET /api/tasks`：返回按创建时间倒序排列的 `Task[]`。
- `GET /api/tasks/{id}`：返回 `Task`；不存在时返回 404。
- `PATCH /api/tasks/{id}`：更新草稿的问题；已开始的任务返回 409。
- `DELETE /api/tasks/{id}`：删除非活动任务并返回 204；排队或执行中的任务返回 409。
- `POST /api/tasks/{id}/run`：已有路由，当前返回 501，用于接入调研能力；不存在的任务返回 404。
- `POST /api/tasks/{id}/cancel`：已有路由，当前返回 501，是未启用的扩展入口，不属于独立必做任务；不存在的任务返回 404。

输入问题为去除首尾空白后的非空字符串，起始实现限制原始输入长度不超过 2000。校验失败返回 422。

错误格式：`{"error":{"code":"...","message":"..."}}`。

## 数据结构

`Task` 包含 `id`、`question`、`status`、`stage`、`report`、`sources`、`events`、`error`、`created_at` 和 `updated_at`。

起始状态为 `draft`。已有状态还包括 `queued`、`running`、`completed`、`failed` 和 `cancelled`。可以按需要增加取消中等状态，但需同步前后端与测试，保持旧字段兼容。

- `Source`：id、title、url、excerpt、fetched_at、published_at（可空）。
- `Event`：id、stage、message、created_at。
- `error`：code、message，或 null。
- `report`：文本或 null；可扩展结构化报告，但需保持基础页面与现有字段兼容，或同时完成调用方迁移并说明。

## 从哪里继续

先运行现有前后端，再根据任务目标决定需要修改的页面、接口和数据结构。真实资料获取、模型接入和结果展示尚待完成；实现方式不预设。
