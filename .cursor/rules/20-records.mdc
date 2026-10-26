---
description: 任务、提交、运行与状态记录（全局，始终加载）
alwaysApply: true
---

# 记录与版本规则

细则见 docs/standards/records.md 和 docs/standards/git-workflow.md。

**任务与分支**
- 每个有意义的改动都属于一个 task_id（格式 T-YYYYMMDD-NN），任务卡放在 docs/tasks/；小的关联修改并入同一个任务。
- 在 task/<task_id>-<slug> 分支上工作。

**提交**
- 提交信息格式为 `<type>(<scope>): <summary>`，尾注必须包含 `Task:` 和 `Actor:`，hooks 会检查。
- 不要 force push，不要改写已推送的历史；不要用 --no-verify 绕过 hooks（确实需要时，在任务卡里说明原因）。

**运行记录**
- 每次运行都有 run_id（格式 R-YYYYMMDD-HHMMSS-<dataset>-<kind>[-<model>]）。
- 运行一开始就写 runs/<run_id>/run.json（status=running），结束时补全状态；失败、中断、取消同样要记录。
- 一律使用严格 JSON：缺测或不适用的字段写 null 并说明原因，不填 0；没有执行的不写成 PASS。
- 完整产物留在 runs/（持久盘，不进 Git）；小型摘要写入 reports/runs/ 和 reports/experiments.csv（进 Git）。

**收尾**
- 更新任务卡、CHANGELOG.md、docs/current-status.md 和 docs/worklog/<YYYY-MM>.md。
- 重要的 AI 贡献记入 docs/ai-use-log.md；人工尚未复核的写 pending。
- README 只写真实存在并验证过的命令；计划中的命令必须标注"计划"。
