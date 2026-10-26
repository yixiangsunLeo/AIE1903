# 代理执行约定（细则）

适用对象：Cursor、Claude Code、Grokbot 以及任何自动化代理。组员手工开发时也建议遵循。

- 入口与红线见 `AGENTS.md`，价值观见 `SOUL.md`，本文件只讲流程。
- 文件、ID 与记录格式见 `docs/standards/records.md`。
- Git 规范见 `docs/standards/git-workflow.md`。

## 1. 开工检查（每个会话都要做）

1. **确认项目根。** 项目根是同时含 `AGENTS.md` 和 `pyproject.toml` 的目录，学校环境为 `/ai/workspace/AIE1903`。不要把 home 目录、`/ai/workspace` 或交接资料目录当成项目根。
2. **确认 Git 现状。** 依次运行 `git status`、`git branch --show-current`、`git log --oneline -5`。如果有未提交的改动，先识别它属于谁；不要 stash、reset、clean，也不要覆盖。
3. **检查写入锁 `.agent-lock`**（位于项目根，不进 Git）：
   - 锁不存在：写入自己的锁（格式见下方）。
   - 锁属于别人且仍有效：只读，或者等待；不要写入。
   - 锁已过期（超过 12 小时，且找不到对应进程或会话）：在 worklog 记一笔后再接管。
4. **检查运行中的任务。** 用 `ps -eo pid,etime,cmd`、`nvidia-smi`，并查看 `runs/*/run.json` 中是否有 `"status": "running"`。不认识的进程不要结束。
5. **按顺序阅读**：`SOUL.md` → `docs/current-status.md` → 当前任务卡 → 与任务相关的 `docs/project-context.md`、`docs/architecture.md`、`docs/standards/*`。

写入锁的格式（一行 JSON）：

```json
{"actor": "claude-code/claude-opus-5", "task_id": "T-20261027-01", "started_at": "2026-10-27T10:00:00+08:00", "host": "ai", "note": "M1 data layer"}
```

会话结束时，删除自己的锁：`rm -f .agent-lock`。

## 2. 任务生命周期

任务状态依次流转：`planned → running → completed`，中途也可能进入 `blocked`、`failed` 或 `cancelled`。

1. **建卡**：从 `docs/templates/task-card.md` 复制一份到 `docs/tasks/<task_id>-<slug>.md`，并在 `docs/tasks/README.md` 的索引里加一行。
2. **开工前**写清楚：目标、范围（包括不做的事）、执行者、基准提交、依赖、预算（时间、内存、GPU、运行次数）和**预先定好的验收标准**。
3. **建分支**：`git switch -c task/<task_id>-<slug>`，基于最新的 `main`。
4. **实施**：遵循 `docs/architecture.md` 的功能区边界和 `docs/standards/coding.md`。如果需要改接口，先改 architecture.md。
5. **验证**：按第 5 节执行，把真实命令、退出码和证据路径写进任务卡。
6. **记录与收尾**：按第 6 节的清单逐项完成。
7. **提交**：按 git-workflow 的格式提交，可以拆成多个提交。推送前要确认已获授权（第 7 节）。

小的关联修改合并在同一个任务里，不必每改一行都另开任务。只修错别字级别的改动，可以在提交尾注里写 `Task: trivial`。

## 3. 运行与实验

- **每次执行都有 run_id**，包括 smoke 测试、回测、训练和最终预测（格式见 records.md）。
- **开始时**就创建 `runs/<run_id>/run.json`，写明 `status=running`，并保存配置快照。**结束时**补全状态、退出码、指标、产物哈希、墙钟时间和峰值内存。
- 中断、OOM、取消、超时和异常同样要落盘，不能只保留好看的结果。
- 预算来自 `configs/runtime.yaml`，任务卡可以在授权范围内调整。默认是 CPU、8 线程、单任务、30 分钟。
- **长任务**要记录 PID、启动命令和日志路径。断线重连后，先查看状态再决定下一步，不要重复启动。
- **heldout 窗口**只有在模型和选择规则都冻结、且经用户批准后才能评估；评估过要记录下来，此后不能再称它是 untouched。
- 跑完以后，只依据真实产物下结论；指标好得反常时，先查泄漏。

## 4. 授权边界

| 类别 | 内容 |
|---|---|
| **可以自主进行** | 在项目内读写代码、文档和配置；建任务卡、分支，做本地提交；在预算内运行 CPU 检查和短实验；从官方仓库补齐公开数据（校验后放入，不覆盖已有文件）；在项目 `.venv` 中增删依赖（同步更新 pyproject 和 lock，并写明原因） |
| **需要用户明确授权** | 推送 GitHub（除非本会话已明确要求，或 current-status 中记有常设授权）；修改 SOUL.md、验证协议、指标口径或赛道选择；评估 heldout；使用 GPU 或执行超出预算的任务；删除项目根之外的文件；修改仓库可见性或协作者；添加 SSH key；公开发布；正式提交榜单；在项目 `.venv` 之外安装软件 |
| **禁止** | 使用 10.27.126.205；打印或提交任何秘密；读取或推断测试真值；读取 sample 文件的数值；跨数据集拼接或对齐（ADR-0005 的例外除外）；编辑原始数据；伪造结果或记录；结束归属不明的进程；修改系统 Python、CUDA 或全局配置；force push 或改写已推送的历史；用 `--no-verify` 绕过 hooks 且不留记录 |

遇到需要授权的事项时，只暂停依赖它的那部分工作，其余可做的照常推进，最后集中请示。请示时给出选项和推荐。

## 5. 验证要求

验证要针对改动的风险，不必为无关的格式变化编造大量测试。

| 改动类型 | 至少要做的验证 |
|---|---|
| 指标、评估 | 手算用例、mask 计数、空 mask、grid 的 0 值规则 |
| 切分、特征、模型 | 泄漏测试：改动未来值，特征和预测都不变；第 289 步不越界；监督目标不跨界 |
| 数据层 | 在真实数据上跑合同测试；校验 checksum；跨数据集读取被拒绝 |
| 最终预测 | `validate-submission` 与 test.csv 逐项一致 |
| 记录、tracking | 失败运行不会被标为成功；输出严格 JSON；`verify-records` |
| 文档、规则 | 引用的路径真实存在；规则 frontmatter 能解析；globs 匹配真实文件 |

每次提交前都要执行：`.venv/bin/python -m pytest` 和 `.venv/bin/ruff check .`。静态检查通过，不等于程序真的运行过，两者要分开写。

## 6. 收尾清单

- [ ] 任务卡：实际改动、真实验证（命令、退出码、run_id、路径）、风险、回退办法、下一步
- [ ] `CHANGELOG.md`：按任务写为什么改、改了什么、怎么验证的
- [ ] `docs/current-status.md`：可用命令、最近的任务与运行、阻塞、下一步
- [ ] `docs/worklog/<YYYY-MM>.md`：追加本次执行记录
- [ ] `docs/ai-use-log.md`：记录重要的 AI 贡献与人工修正；尚未复核的写 pending
- [ ] 有运行时：更新 `reports/runs/` 摘要和 `reports/experiments.csv` 索引
- [ ] 删除 `.agent-lock`；确认 `git status` 干净，或者已说明哪些改动有意不提交

## 7. 提交、推送与同步

- 提交格式和 hooks 见 `docs/standards/git-workflow.md`。
- 推送前确认：已获授权、hooks 通过、没有秘密、没有原始数据或大文件。
- 合并方式：`main` 只接收来自 `task/*` 分支的合并，可以走 PR，也可以由学生授权做本地 `--no-ff` 合并。
- 学校环境与管理端 box 之间只用 Git 同步，不允许两边同时写同一个工作树（见 `docs/runbooks/environment.md`）。

## 8. 汇报格式（中文）

1. **结论**：一句话说清做成了什么、没做成什么。
2. **改动**：涉及的文件或模块，以及原因。
3. **证据**：命令、退出码、run_id、指标、文件路径。
4. **风险与未决事项**：未验证的、需要授权的、存在疑问的。
5. **下一步**：建议，并给出可选方案。

## 9. 交接

下一位接手者只靠仓库就能继续工作，不需要聊天记录。交接前，`docs/current-status.md` 中的"下一步"必须具体到可以直接开工，例如"按 docs/roadmap.md 的 M1 建任务卡并实现 data.load_train"。
