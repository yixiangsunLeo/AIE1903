# 记录规范（任务、运行、决策、执行记录与备份）

原则：Git 保存逐行差异；这里规定的记录负责说明**为什么改、是谁做的、凭什么认为它是对的**。

## 1. ID 格式

| 对象 | 格式 | 示例 |
|---|---|---|
| 任务 | `T-YYYYMMDD-NN`（建卡日期 + 当日序号） | `T-20261027-01` |
| 运行 | `R-YYYYMMDD-HHMMSS-<dataset_id>-<kind>[-<model>]`，时间取服务器本地时间（Asia/Shanghai） | `R-20261027-101500-cell_217-backtest-snaive` |
| 审计 | `A-YYYYMMDD-<slug>` | `A-20261026-framework` |
| 决策 | `ADR-NNNN-<slug>` | `ADR-0002-validation-protocol` |

运行的 kind 取值：`smoke`、`audit`、`backtest`、`train`、`predict`、`eval-heldout`。

## 2. 记录在哪里

| 记录 | 位置 | 进 Git | 什么时候写 |
|---|---|---|---|
| 任务卡 | `docs/tasks/<task_id>-<slug>.md`，索引在 `docs/tasks/README.md` | 是 | 开工前建，收尾时补全 |
| 变更日志 | `CHANGELOG.md` | 是 | 每个任务收尾时 |
| 执行记录 | `docs/worklog/<YYYY-MM>.md`，只追加 | 是 | 每个会话或执行批次结束时 |
| 当前状态 | `docs/current-status.md` | 是 | 每个任务收尾时 |
| 决策 | `docs/decisions/ADR-*.md` | 是 | 做出影响后续的决定时 |
| AI 贡献 | `docs/ai-use-log.md` | 是 | 有重要的 AI 产出或人工修正时 |
| 运行完整记录 | `runs/<run_id>/`（run.json、配置快照、日志、预测、图） | 否，只在持久盘 | 运行开始时创建，结束时补全 |
| 运行摘要 | `reports/runs/<run_id>.json` | 是 | 运行结束时 |
| 实验索引 | `reports/experiments.csv`，一次运行一行 | 是 | 运行结束时 |
| 审计 | `reports/audit/<audit_id>/` | 是 | 审计时 |

## 3. 运行记录 `run.json` 的必需字段

模板在 `docs/templates/run-record.json`，主要字段如下：

- **身份**：run_id、task_id、actor、kind、status（`running`、`succeeded`、`failed`、`cancelled`、`timeout`）、started_at、finished_at、exit_code。
- **代码**：code_commit、git_dirty，以及代码未提交时的 diff 的 sha256。
- **数据**：dataset_id、各文件的 sha256（与 `data/checksums.sha256` 比对）、数据合同版本。
- **配置**：解析后配置的快照路径和 config_sha256、seed、validation_protocol_id、使用的 fold、是否动用 heldout。
- **环境**：Python 版本和关键包版本（或环境快照路径）、设备、线程数。
- **结果**：每个 fold 的五项指标及计数、指标口径版本、尺度说明（原始尺度或变换尺度）、训练损失（注明尺度）。
- **成本**：墙钟秒数、峰值 RSS、峰值显存。测不到时写 `null`，并在 measurement_notes 里说明原因。
- **产物**：路径和 sha256。
- **结论**：conclusion、failure_reason、next_action、ai_contribution、human_review_status（默认 `pending`）。

格式规则：

- **严格 JSON**：不出现 NaN 或 Infinity；不适用的字段写 `null`；**不要用 0 冒充缺失**。
- 状态必须如实填写：未执行的不写 PASS，失败的不写 succeeded。

## 4. 实验索引 `reports/experiments.csv`

列为：`run_id,task_id,date,actor,dataset,kind,model,protocol,folds,status,mae,rmse,mape,mmape_t1,mmape_t2,code_commit,git_dirty,summary_path,notes`。

- t1、t2 是该数据集的两个阈值（cell 为 3e5 和 1e6，grid 为 1e4 和 1e5）。
- 指标列填所列 fold 的指标**均值**，各 fold 的明细在摘要 JSON 里。
- 没有分数的运行（失败、审计等）对应列留空。

## 5. 执行记录（worklog）格式

每个会话或执行批次追加一条，**不改已有条目**；如需更正，追加一条"更正"条目。

```markdown
## 2026-10-27 10:00–11:30 · claude-code/claude-opus-5 · T-20261027-01
- 目标：……
- 执行：……（关键命令与退出码）
- 产出：提交 <sha>；运行 <run_id>；文件 ……
- 推送：已推送 / 未推送（原因）
- 未完成 / 下一步：……
```

## 6. 备份

| 层级 | 内容 | 方式 | 频率 |
|---|---|---|---|
| 1 | 受 Git 跟踪的全部记录 | `git push`（需授权）到 GitHub | 每个任务收尾时 |
| 2 | `runs/`、`logs/`、原始数据 | 只保存在持久盘 `/ai/workspace` | 实时 |
| 3 | `runs/` 和 `logs/` 的快照 | 打包到 `backups/`，并生成 sha256（命令见 sync-backup-release runbook） | 释放环境前，或大批运行之后 |
| 4 | Cursor 会话记录（位于容器的 `/root`，会随环境消失） | 复制到 `logs/agent-sessions/cursor/` | 释放环境前 |

注意：第 2、3 层都在同一个存储卷上，只能防误删，防不了存储卷本身丢失。如果需要异地备份，由学生另行决定存放位置，不要放进公开仓库。
