# 运行手册：Grokbot 接手开发

Grokbot 负责任务管理与实验协同，用 Claude Code 编程。目标是做出**可复现、经公平验证、学生能讲清楚**的课程项目，并如实记录 AI 与组员的贡献。

本文件取代旧的 `WORK_INSTRUCTIONS.md`，旧版内容已全部并入。

## 1. 开工指令（每次接手都要执行）

1. 进入项目根 `/ai/workspace/AIE1903`，检查分支、`git status`、`.agent-lock` 和正在运行的作业，确认没有别的写入者（docs/agent-contract.md §1）。
2. 读取 `SOUL.md`、`AGENTS.md`、**`rules/` 下的全部规则**、`docs/current-status.md`，以及当前任务卡或 `docs/roadmap.md` 中的下一个里程碑。Grokbot 自己也要读规则，不能只靠 Claude Code 去读。
3. 确认 Claude Code 已加载 CLAUDE.md、AGENTS.md、SOUL.md 以及 `.claude/rules/` 中的规则：交互模式下运行 `/context`；非交互模式下先问一句"当前赛道、预测步长、日周期、禁用信息、记录位置、运行预算、CPU 线程上限分别是什么"，答案必须和仓库文件一致（线程上限是 24）。
4. 跑环境自检：`.venv/bin/python -m pytest` 和 `(cd data && sha256sum -c checksums.sha256)`。如果 grid_273 等可选部分有缺失，不要因此重装环境。
5. **领取一个有预算的任务**：建任务卡，写明 task_id、目标、基线、主要改动、验证窗口、验收标准和预算。
6. 调用 Claude Code 实现并运行。每次执行都保留 run_id、代码版本、配置、数据哈希、结果和失败记录。
7. 只依据真实产物分析结果，然后更新任务卡、CHANGELOG、实验索引、current-status 和 worklog。
8. 给学生一页中文汇报：改了什么、证据、成本、问题、下一步。人工尚未复核的，不替学生写"已审核"。

## 2. 运行预算与启动方式（默认值见 configs/runtime.yaml，流程见 docs/runbooks/training.md）

- 默认：CPU、8 线程、单任务、每个运行最长 30 分钟、内存不超过 8 GiB、精度 `fp32_strict`、打开确定性。
- 学校容器的配额是 24 核、32 GiB、一张 RTX 5090，不要占满。线程数永远不超过 24。
- 通过 ssh 下发运行命令时，一律用 training.md §4 的 `setsid nohup … timeout …` 模板，并记录 PID。否则 ssh 一断开，任务就会被结束。断线重连后，先查 PID 和 run.json，再决定下一步。
- 使用 GPU、长时间训练或批量调参，必须先在任务卡里写好预算，并得到学生同意。
- 每批实验只跑少量配置；如果资源不够、同类失败重复出现、或者看不到可解释的改进，就保留诊断记录并停下，不要无休止地重跑。

## 3. 必须遵守

- 不改动 Cursor 或其他代理正在写的工作树（单写入者）。
- 断线后先恢复已有任务的状态，不要重复启动。
- 不自动大规模调参，不增加付费资源，不正式提交榜单，不公开仓库。
- 绝不使用 10.27.126.205；不打印密码；不把原始数据发给外部模型或服务。
- 模型按学生现有的配置使用（现行是 `--model claude-opus-5`，由 CC Switch 映射）。Claude Code 派生的子代理继承同一套模型配置，不擅自换模型；确实需要例外时，先问学生。
- 动用 heldout 窗口前，必须得到学生批准并记录。

## 4. 第一阶段计划（来自原工作指令，已映射到 roadmap）

依次完成：环境与数据审计（已完成，A-20261026-framework）→ 日周期基线 → 五指标 → 按验证协议回测 → 运行记录 → 两张核心图 → 下一步任务卡。

对应 `docs/roadmap.md` 的 M1–M8，从 M1 开始。

## 5. 已验证的命令（截至 v0.2.1）

```bash
cd /ai/workspace/AIE1903
(cd data && sha256sum -c checksums.sha256)          # 13 个官方文件完整性校验
.venv/bin/python -m pytest                           # 框架结构冒烟测试
.venv/bin/ruff check .                               # 代码检查
python3 reports/audit/A-20261026-framework/audit_probe.py   # 复现数据审计（只读）
scripts/sync-rules.sh --check                        # 规则副本是否与唯一源一致
.venv/bin/python reports/audit/A-20261026-server/server_probe.py   # 复测服务器事实（约 20 秒，只读）
```

`python -m aie1903.cli …` 一类的命令**尚未实现**（roadmap M7），不要调用。
