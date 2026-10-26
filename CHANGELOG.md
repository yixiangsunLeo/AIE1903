# CHANGELOG

按任务记录：为什么改、改了什么、怎么验证的。逐行差异见 Git，任务细节见对应的任务卡。

## [0.2.1] — 2026-10-26 · T-20261026-02 服务器摸底与多代理规则

### 为什么

- 用户要求摸清本机服务器"怎么运作、怎么训练"并写入规则；
- 同时要求"所有规则必须是 Cursor、Claude 或者其他代理都能读完的"。

### 新增

- **审计 `A-20261026-server`**：
  - 三个脚本：只读探测、性能基准、随机数据训练冒烟；
  - 对应的 JSON 证据。
- **手册**：
  - `docs/runbooks/environment.md` 扩写为完整的服务器手册；
  - 新增 `docs/runbooks/training.md`（训练流程）。
- **规则**：
  - 新增 `rules/` 作为唯一源；
  - 新增 `35-training.md`；
  - 重写 `30-server.md`，写入实测事实：24 核配额、torch 默认 128 线程导致的过度订阅、默认 TF32、Cursor 断开 300 秒后自动关闭、`setsid nohup`、DNS 偶发失败、没有 IPv6、NFS 小文件慢、pip 不得替换镜像 torch、wandb 只能离线。
- **规则工具**：
  - `scripts/sync-rules.sh`：生成 `.cursor/rules` 的真实副本（加上由 SOUL.md 生成的 `05-soul.mdc`）和 `.claude/rules` 的符号链接；
  - pre-commit 增加规则一致性检查；
  - `scripts/check-framework.py`：175 项框架检查。
- ADR-0006。

### 变更

- AGENTS.md：新增"规则"一节（所有代理必须读完）和"服务器与训练要点"。
- CLAUDE.md、README、grokbot、agent-contract、git-workflow 同步更新。
- `configs/runtime.yaml` 升到 v2：线程上限 24、精度 `fp32_strict`、确定性、默认环境变量。
- 修正版本规则与 roadmap 之间的矛盾：框架调整升 patch，里程碑组完成升 minor。
- **更正（v0.2.1 之后的补充合并）**："GitHub SSH 改用 FQDN 可以规避 DNS 失败"被推送实测证伪，SSH 配置已恢复原样。environment.md、current-status、Q10 和审计 README 都已更正；DNS 失败的唯一缓解办法是重试。

### 验证

详见 `docs/tasks/T-20261026-02-server-survey-and-rules.md` 的"真实验证"一节：

- 三个探测脚本的退出码都是 0；
- `sync-rules --check` 的正例、反例都符合预期；
- pre-commit 规则检查的 5 种情况都符合预期；
- check-framework 175/175；
- pytest 19 项通过；
- ruff 检查通过。

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
