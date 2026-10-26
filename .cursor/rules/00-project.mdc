---
description: AIE1903 项目入口、红线与规则维护（全局，始终加载）
alwaysApply: true
---

# AIE1903 · 项目规则

- 完整的共享约定在 AGENTS.md，价值观在 SOUL.md。
- `rules/` 是全部强制规则的**唯一源**，说明见 rules/README.md。
- 任何代理（Cursor、Claude Code、Grokbot 或其他代理）开工时都要读完 `rules/` 下的全部规则。

**开工**
1. 确认项目根是 /ai/workspace/AIE1903。
2. 查看 git status、当前分支、.agent-lock 和运行中的任务。
3. 依次阅读 SOUL.md、docs/current-status.md、当前任务卡。

**红线**（与 AGENTS.md 一致；如有冲突以 AGENTS.md 为准，并报告冲突）
- 历史 1728 点，预测 289 步，日周期 288。主线 cell_217；cell_30 只用于演练；grid_273 在主线完成后再做。
- 不使用任何预测起点之后的真实值；不读取 sample_submission 的数值；一个运行只用一个数据集。cell_30 的时间标签比 cell_217 晚 50 分钟，严禁跨目录对齐。
- 不编辑 data/raw/ 和课程原件；不伪造数据、分数、记录或完成状态。
- 绝不使用 SSH 主机 10.27.126.205；不打印、不提交任何秘密。
- 以下事项需要用户授权：推送 GitHub；修改验证协议、指标口径或 SOUL.md；动用 heldout；使用 GPU（要在任务卡中写明预算并获批准）；超出预算的运行；删除项目外文件；公开发布或正式提交。
- 持久状态只放在 /ai/workspace；不改系统 Python、CUDA 或全局配置。

**规则维护**
- 规则只写在 `rules/*.md` 里，用纯 Markdown，任何代理都能读。
- 改完后运行 `scripts/sync-rules.sh`，生成 Cursor 和 Claude Code 的适配副本，pre-commit 会检查两者是否一致。
- 不要在 .cursor/rules/ 或 .claude/rules/ 里直接写规则。
- 必须知道的约束要直接写进规则正文，不要只放一个文件引用（引用的内容不会被自动展开）。
