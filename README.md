# AIE1903 — 无线网络上行流量预测

这是 CUHK-SZ AIE1903 的课程项目（授课教师 Feng Yin）：用 6 天历史（1728 个 5 分钟点），一次性预测接下来的 289 个点。主线是 **cell_217**；cell_30 只用于流程演练；grid_273 在主线完成后再扩展。

> **English summary.** Course project on wireless uplink traffic forecasting. Framework v0.2.1 is in place: agent rules (single source in `rules/`, readable by any agent), server survey, record system, functional-area contracts, configs and verified data. The forecasting code is not implemented yet (see `docs/roadmap.md`).

## 当前状态

- **阶段**：框架 v0.2.1 已完成（含服务器摸底与训练手册），功能代码和训练都还没有开始。下一步是 roadmap 的 M1（数据层）。
- **数据**：三个官方数据集共 13 个文件，全部齐全，并与官方仓库提交 `49822d8` 逐字节一致（审计 `reports/audit/A-20261026-framework/`）。
- 实时状态、阻塞和下一步见 [`docs/current-status.md`](docs/current-status.md)。

## 从哪里开始读

| 你是 | 建议的阅读顺序 |
|---|---|
| 学生、组员 | 本文件 → `docs/current-status.md` → `docs/project-context.md` → `docs/roadmap.md` |
| 代理（Cursor / Claude Code / Grokbot / 其他） | `AGENTS.md`（Cursor 和多数代理自动加载）或 `CLAUDE.md`（Claude Code）→ `SOUL.md` → `rules/` 全部规则 → `docs/current-status.md` |
| 课程人员 | 本文件 → `docs/project-context.md` → `docs/ai-use-log.md` |

## 目录

```text
AIE1903/
├── AGENTS.md · CLAUDE.md · SOUL.md     代理共享约定 · Claude Code 入口 · 项目之魂
├── README.md · CHANGELOG.md            说明 · 按任务记录的变更日志
├── pyproject.toml · requirements.lock  依赖声明 · 实测版本
├── rules/                              全部强制规则的唯一源（纯 Markdown，任何代理都能读）
├── .cursor/rules/ · .claude/rules/     由 scripts/sync-rules.sh 生成的 Cursor 副本 · Claude Code 符号链接
├── .githooks/ · .gitmessage            提交规范检查 · 提交信息模板
├── configs/       数据集注册表与数据合同、验证协议、运行预算、实验配置模板
├── data/          raw/（官方原始文件，不进 Git）· checksums.sha256
├── src/aie1903/   九个功能区骨架：config data splits features models evaluation tracking pipelines viz
├── tests/         测试（目前只有框架冒烟测试）
├── scripts/ · notebooks/   薄入口与运维脚本 · 探索与展示
├── docs/          背景、架构、路线图、执行约定、规范、运行手册、任务卡、决策、执行记录、AI 贡献
├── reports/       审计、运行摘要、实验索引、报告图表、legacy
└── runs/ · submissions/ · artifacts/models/   运行产物 · 提交文件 · 模型权重（都不进 Git）
```

进 Git 的：源码、配置、文档、小型报告。不进 Git 的：原始数据、运行产物、权重、密钥、venv。

## 环境与已验证的命令（学校环境，2026-10-26）

```bash
cd /ai/workspace/AIE1903
python3 -m venv --system-site-packages .venv && .venv/bin/python -m pip install -e '.[dev]'   # 首次使用或换镜像后
(cd data && sha256sum -c checksums.sha256)                    # 原始数据完整性
.venv/bin/python -m pytest                                    # 框架冒烟测试
.venv/bin/ruff check . && .venv/bin/ruff format --check .     # 代码检查
python3 reports/audit/A-20261026-framework/audit_probe.py     # 复现数据审计（只读）
```

统一 CLI（`python -m aie1903.cli doctor / audit-data / backtest / predict / validate-submission / verify-records`）**尚未实现**，计划在 roadmap 的 M1–M7 中完成。

## 关键约束（摘要，完整版见 AGENTS.md）

- 不使用预测起点之后的任何真实值；不读取 sample 提交文件的数值；一个运行只用一个数据集。
- 五项官方指标（MAE、RMSE、MAPE、Masked MAPE ×2）都在原始尺度上计算，越低越好。
- 验证协议为 expanding_289_v1：常规开发用 dev_a 和 dev_b；heldout 需要批准才能使用。

## 协作规范

- 在 `task/<task_id>-<slug>` 分支上工作，完成后合并到 `main`。提交格式和 hooks 见 `docs/standards/git-workflow.md`。
- 新克隆的仓库要先执行一次：`git config core.hooksPath .githooks && git config commit.template .gitmessage`。
- 每个任务有一张任务卡，每次运行有一个 run_id，执行记录写在 `docs/worklog/`。

## 团队与贡献

| 成员 | GitHub | 分工 |
|---|---|---|
| Yixiang Sun | yixiangsunLeo | 待填写 |
| 待补充 | | |

AI 的贡献记录在 `docs/ai-use-log.md`。

## 数据来源

- 官方数据：<https://github.com/AIE1903-DataCompetition-26AY/competition-data>（提交 `49822d8`）
- 官方 starter：<https://github.com/AIE1903-DataCompetition-26AY/competition-starter>
