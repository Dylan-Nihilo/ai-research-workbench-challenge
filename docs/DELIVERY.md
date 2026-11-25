# 交付说明

## 启动与配置

仅需 Docker Engine 和 Docker Compose 2.24+。复制 `.env.example` 为 `.env`，填写自己的 `OPENAI_API_KEY`；可选设置支持 Responses API `web_search` 的 `OPENAI_MODEL`（默认 gpt-4.1）。密钥仅传入后端，不提交到 Git。模型与联网工具会产生费用，问题会发送给 OpenAI。

运行 `docker compose up -d --build --wait`，打开 http://localhost:5173。创建问题后点击“开始调研”，页面每两秒刷新状态；完成后查看结论及编号来源链接。失败时查看错误并重试。修改配置后用 `docker compose up -d --force-recreate` 重建容器。

## 实现

复用原 React、FastAPI 和 SQLite。POST run 返回 202，后台调用 OpenAI Responses API 并强制使用 web_search。模型承担问题理解、公开资料检索与整理；后端只接受完成的联网调用和包含有效 URL 引用的报告，将工具引用转换为编号，保存可点击来源和事件。报告按纯文本展示，不执行模型生成的 HTML。来源时间是处理检索结果的时间，不是网页发布日期；没有声称已自行抓取或存档原文。

参考官方接口：https://developers.openai.com/api/docs/guides/tools-web-search 。没有额外运行依赖。未配置密钥返回 503 且保留草稿；外部错误、超时和无引用输出均明确失败。重启后在途任务标记为中断，允许手动重试。

## 检查与实际结果（2026-11-25）

用户启动 Docker 后，已通过 Docker Compose 完成镜像构建和服务启动，前后端健康检查通过。容器内后端 unittest、前端 TypeScript 检查及生产构建均通过；前端代理、任务 CRUD 和输入校验冒烟检查也通过。用户配置密钥后，已从网页启动真实模型联网调研并得到完成报告，刷新页面后结果仍存在。离线测试 fixture 仅用于契约验证，不是调研成果。

复现检查：

```sh
docker compose up -d --build --wait
docker compose run --rm --no-deps backend python -m unittest discover -s tests -v
docker compose run --rm --no-deps frontend npm run build
docker compose exec -T frontend node tests/smoke.mjs
```

真实验收：配置有权限与余额的密钥，从网页输入“比较 Notion 与 Obsidian 对五人团队知识库的适用性，依据官方公开资料说明限制”，开始调研，确认状态完成、报告引用编号与可打开来源对应、页面刷新后仍存在结果。记录实际任务 ID、模型、时间、结果及脱敏截图；失败时记录真实错误，不以 fixture 替代。本次已执行网页创建、启动调研和刷新持久化验证。任务 ID：d6fe814c-e12a-4d91-81c1-fe82fa2f583f；模型 gpt-4.1；完成时间 2026-11-25 17:54（Asia/Shanghai）；共 5 个引用，完整真实结果见 [demo-result.json](demo-result.json)。来源包含 Notion、Obsidian 官方站点以及 Reddit 和 StackFYI，未完全遵从问题中依据官方资料的要求，也未逐条人工打开核验事实。演示证明真实链路完成，不代表报告所有结论正确。

## 已知限制

后台任务在单进程内运行，不支持多 worker 分布式部署，最多同时三个调研；无持久化队列、自动重试或取消功能。部署面向本地开发，未增加登录与计费控制。模型引用只能验证 URL 和结构，不能保证事实正确或资料完备，应人工核对原文。报告是纯文本，Markdown 表格不做富文本排版。没有提供网页快照或检索全过程流式事件；执行阶段只记录应用可观察到的提交、检索分析和最终结果。Fork、推送及 PR 仍需按招聘邀请提供候选人信息后完成。
