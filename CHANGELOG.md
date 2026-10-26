# CHANGELOG

按任务记录：为什么改、改了什么、怎么验证的。逐行差异见 Git，任务细节见对应的任务卡。

## [0.2.0] — 2026-10-26 · T-20261026-01 框架重建

### 为什么

- 交接文档要求统一 Cursor、Claude Code 和 Grokbot 的工作约定，并建立记录与验证体系。
- 用户要求先搭好完整框架、暂时不写功能代码，同时清理冗余文件。

### 新增

- **代理指令**：
  - `SOUL.md`（项目之魂）；
  - `AGENTS.md`（共享约定）；
  - `CLAUDE.md`（用 `@` 导入前两者）；
  - `.cursor/rules/` 下 5 条规则，以及 `.claude/rules/` 下 3 条按路径生效的规则（符号链接，与 Cursor 共用源文件）。
- **代码功能区**：`src/aie1903/` 下 9 个子包的骨架；`docs/architecture.md` 规定了各区的职责、依赖方向、接口草案、不变量和必测项。
- **记录体系**：
  - 任务卡、ADR 和运行记录的模板；
  - `docs/tasks/`，`docs/decisions/`（ADR-0001 至 0005），`docs/worklog/`，`docs/ai-use-log.md`；
  - `reports/experiments.csv`；
  - runs/ 与 submissions/ 的目录规范；
  - 同步、备份与释放环境的运行手册。
- **配置**：
  - `configs/datasets.yaml`：数据合同与官方来源；
  - `configs/runtime.yaml`：运行预算；
  - `configs/experiments/_template.yaml`：实验配置模板；
  - `configs/validation-plan.json` 改为 expanding_289_v1。
- **Git**：
  - `.githooks/commit-msg` 和 `.githooks/pre-commit`；
  - `.gitmessage`、`.gitattributes`、`.editorconfig`；
  - 标签 `archive/legacy-scaffold`（指向 203a73b）。
- **`.cursorignore`**：把密钥、原始数据、运行产物和 venv 排除在 Cursor 的索引之外。Cursor 禁止代理直接写这个文件，所以经学生授权由终端创建。
- **环境**：
  - 项目 `.venv`（使用 system-site-packages）；
  - `pyproject.toml` 中的依赖与 ruff、pytest 配置；
  - `requirements.lock`。
- **数据**：
  - 补齐 grid_273 的 5 个官方文件（已通过 blob 与字节数校验）；
  - `data/checksums.sha256`；
  - 审计 `A-20261026-framework`。

### 移除

以下内容全部保存在标签 `archive/legacy-scaffold` 中，或者已经并入新文件。

- 旧代码与重复入口：旧包 `src/aie1903_project/`；旧的 re-export `src/aie1903/__init__.py`；scripts/ 下 7 个重复入口；`tests/test_imports.py`。
- 过时的配置与空目录：`configs/default.yaml`；`requirements.txt`；空的 `figures/` 与 `artifacts/outputs/`；空的 `.cursor/mcp.json`。
- 已合并到新文件的旧文档：`.cursor/rules/aie1903.mdc`；`WORK_INSTRUCTIONS.md`；`docs/SYNC.md`。
- 冗余文件：`data_description_for_cell_217.pdf.fixed`（与原 PDF 相同）；根目录的 `cell_217_data.tgz`（内容与 raw 相同）；交接 zip（内容已存入 `docs/references/`）。
- `data/raw/` 下的 PDF 取消 Git 跟踪，文件仍保留在磁盘上。

### 变更

- `reports/backtest_metrics_cell30.json` 移到 `reports/legacy/`，并标注为 legacy_unverified。
- 包名统一为 `aie1903`，版本 0.2.0，Python 要求不低于 3.11。

### 验证

详见 `docs/tasks/T-20261026-01-framework-rebuild.md` 的"真实验证"一节：

- 数据合同 132 项检查全部通过；
- checksum 13/13；
- pytest 19 项通过；
- ruff 检查通过；
- 规则的 frontmatter 与 globs 检查通过；
- hooks 的正例、反例都符合预期。
