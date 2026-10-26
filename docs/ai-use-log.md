# AI 使用与贡献记录

课程要求如实记录 AI 的贡献，以及学生对 AI 失败的识别与修正。

- 只记录**重要**的产出：方法、结构、关键代码、结论，以及人工的修正和否决。
- 不记录账号、口令或大段私密对话。
- 人工尚未复核的，状态写 `pending`；代理不能替学生签"已复核"。

| 日期 | 执行者（工具/模型） | task_id | AI 的贡献 | 人工修正或否决 | 证据 | 人工复核 |
|---|---|---|---|---|---|---|
| 2026-09-15 | human/Yixiang Sun + Cursor | — | 可复用的小组项目骨架（`aie1903_project` 布局） | — | 提交 cf8bdad（已归档到 `archive/legacy-scaffold`） | 由作者本人完成 |
| 2026-10-26 | 操作者 + Claude Code（CC Switch） | — | 学校盘上的初始脚手架：指标、季节朴素基线、旧验证协议、cell_30 回测；并与 GitHub 骨架合并 | — | 提交 80122a8、146a5f0、6c2d40e、203a73b；`reports/legacy/` | pending |
| 2026-10-26 | cursor/claude-opus-5.5 | T-20261026-01 | 审计项目、数据与环境；补齐 grid_273；发现 cell_30 与 cell_217 的 50 分钟时钟偏移，以及 sample 末行疑似含真值；重建框架，包括 SOUL、AGENTS、CLAUDE、规则、记录体系、功能区契约、配置、hooks 和 venv；移除旧代码；推送到 GitHub | 待学生复核 ADR-0002 和 ADR-0003（验证协议与指标口径为暂行采用） | `docs/tasks/T-20261026-01-framework-rebuild.md`；`reports/audit/A-20261026-framework/` | pending |
