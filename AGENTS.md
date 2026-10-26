# AGENTS.md — AIE1903 代理共享约定

本文件是 Cursor、Claude Code、Grokbot 以及其他任何代理的统一入口：Cursor 和多数代理会自动加载它，Claude Code 通过 CLAUDE.md 导入。价值观见 `SOUL.md`，强制规则见 `rules/`（下方"规则"一节），流程细则见 `docs/agent-contract.md`。

如果指令之间有冲突，按以下顺序取舍，并把冲突写进当前任务卡：用户当次的明确指令 > 本文件的红线 > SOUL.md > docs/ 中的细则。

## 项目一句话

CUHK-SZ AIE1903 课程项目：无线网络上行流量预测。用 6 天历史（1728 个 5 分钟点）一次性预测接下来的 289 个点。主线是 **cell_217**；**cell_30** 只用于流程演练；**grid_273** 等主线完成后再扩展。

当前阶段：框架 v0.2.1 已搭好（服务器已摸底，规则以 `rules/` 为唯一源），功能代码尚未实现；按 `docs/roadmap.md` 的里程碑依次开发。真实状态以 `docs/current-status.md` 为准。

## 开工（每个会话）

1. 确认项目根：同时含本文件和 `pyproject.toml` 的目录（学校环境为 `/ai/workspace/AIE1903`，存储卷 sun）。
2. 查看 `git status`、当前分支、未提交改动、`.agent-lock` 和正在运行的任务。他人的改动不 stash、不 reset、不 clean、不覆盖。
3. 依次阅读：`SOUL.md` → **`rules/` 下的全部规则** → `docs/current-status.md` → 当前任务卡 `docs/tasks/<task_id>-*.md` → 与任务相关的文档（project-context、architecture、standards、runbooks）。
4. 赛道、路径、预算一律以 `configs/` 中的真实配置为准，不凭聊天记忆。

## 规则（所有代理都必须读完）

`rules/` 是全部强制规则的**唯一源**，格式是纯 Markdown，任何代理都能读（ADR-0006）。Cursor 和 Claude Code 会自动加载由 `scripts/sync-rules.sh` 生成的副本或链接；其他代理必须自己打开这些文件读完。

| 规则 | 内容 |
|---|---|
| `rules/00-project.md` | 开工顺序、红线、需要授权的事项、规则维护方式 |
| `rules/10-forecasting.md` | 时间边界、数据语义、官方指标口径 |
| `rules/20-records.md` | 任务卡、分支与提交、运行记录、收尾 |
| `rules/30-server.md` | 学校服务器的事实、资源上限、持久化、网络、软件、进程 |
| `rules/35-training.md` | 训练与运行：预算、线程、精度、确定性、启动、监控、记录 |
| `rules/40-code-structure.md` | 功能区边界、依赖方向、写法 |

新增或修改规则时，只改 `rules/*.md`，然后运行 `scripts/sync-rules.sh`，pre-commit 会检查副本是否一致。不要只在某个工具的专用配置里写规则。维护细则见 `rules/README.md`。

## 不可违反的约束

### 数据与时间

- 训练 1728 行，预测 289 步，日周期 288。时间戳是原始采集时钟，不做时区转换。
- 预测起点之后的任何真实值都不可用：测试标签、预测区间内的先前点、邻居或其他数据集的同时段数值。
- 标准化、阈值、聚类、相关矩阵、特征选择、融合权重都只能在该折的训练段上拟合；监督样本的**全部目标**必须落在训练段内。
- 第 289 步的 lag-288 已经落入预测区间。日周期基线要用最后 288 点做周期延拓（`train[-288 + h % 288]`），或者用更早的同刻历史。
- 一个运行只加载一个数据集。cell_30 与 cell_217 是同一批测量，但时间标签相差 50 分钟（审计 A-20261026-framework），严禁跨目录拼接或对齐。唯一的例外是 grid_273 与 cell_30 的官方层级关系，使用前必须在任务卡中声明（ADR-0005）。
- `*_sample_submission.csv` 只能当格式模板，数值不是答案；cell_30/grid_273 的 sample 末行疑似含测试期真值。任何 sample 数值都不得读取。
- 不编辑 `data/raw/` 和课程原件；原始数据的完整性用 `data/checksums.sha256` 校验。

### 评估

- 官方五指标，越低越好：MAE、RMSE、MAPE、Masked MAPE ×2。cell 的阈值是 3e5/1e6；grid 的阈值是 1e4/1e5，且 grid 的 MAPE 只计真实值大于 0 的位置。
- 一律在原始计数尺度计算：mask 只由真实值决定，在全部保留位置上整体平均，并报告每项计数。空 mask 输出 `null` 和 `count=0`，不得输出 0 或 NaN；不私自加 epsilon。口径定义见 ADR-0003。
- 验证协议见 `configs/validation-plan.json`（expanding_289_v1）。常规开发只用 dev_a、dev_b；动用 heldout 必须经用户批准并记录。

### 安全与边界

- **绝不使用研究用 SSH 主机 10.27.126.205。**
- 不打印、不提交密码、密钥或令牌。SSH 密钥在 `/ai/workspace/.ssh/`，只读使用。
- 以下操作需要用户明确授权：推送 GitHub；修改 SOUL.md、验证协议或指标口径；动用 heldout；使用 GPU 或执行超出预算的任务；删除项目根之外的文件；公开发布或正式提交。
- 持久状态只放在 `/ai/workspace`；忽略 NFS 垃圾文件 `.!!!*`。不改系统 Python、CUDA 或全局配置；不结束归属不明的进程。

### 服务器与训练（要点，完整内容见 rules/30-server.md、rules/35-training.md）

- 容器的 CPU 配额只有 **24 核**，`nproc` 显示的 256 不可信；内存 32 GiB，没有 swap；1 张 RTX 5090。每次运行都要**显式设置线程数**（默认 8，不超过 24）。
- 只有 `/ai/workspace` 是持久的；`/root`、`/tmp` 和缓存都会随环境释放而消失。
- 长任务必须用 `setsid nohup … &` 启动并记录 PID。Cursor 断开 300 秒后服务端会自动关闭，普通方式启动的任务可能被一起结束。
- GPU 默认使用 TF32，会改变计算结果。默认精度是 `fp32_strict`，并且打开确定性设置。
- DNS 偶尔解析失败，重试即可。没有 IPv6；wandb 只能设为 disabled 或 offline；pip 不得替换镜像自带的 torch。

## 代码功能区（详见 docs/architecture.md）

`src/aie1903/` 下有 config、data、splits、features、models、evaluation、tracking、pipelines、viz 九个功能区，另计划一个 `cli.py`。

依赖只能沿既定方向，`evaluation` 与 `models` 互不导入。路径、设备、线程、种子全部来自配置。新功能先确定归属的功能区，不新建 utils 这类杂物间。

## 每项任务的必做事项

1. 建任务卡（模板 `docs/templates/task-card.md`），写明目标、范围、执行者、基准提交、预算和验收标准。
2. 在 `task/<task_id>-<slug>` 分支上工作。提交信息遵循 `docs/standards/git-workflow.md`，须带 `Task:` 和 `Actor:` 尾注，hooks 会检查。
3. 每次运行都有 run_id，完整产物放 `runs/<run_id>/`，摘要放 `reports/runs/`。失败和中断同样记录；测不到的值写 null。
4. 验证与本次改动直接相关的关键风险，写下真实命令、退出码和证据路径。
5. 收尾时更新任务卡、`CHANGELOG.md`、`docs/current-status.md`、`docs/worklog/<YYYY-MM>.md`。重要的 AI 贡献记入 `docs/ai-use-log.md`；人工尚未复核的写 pending。

## 结束汇报

用中文说明四件事：改了什么；验证证据（命令、结果、路径）；风险与未决事项；下一步。没验证的写"未验证"。
