# T-20261026-01 项目框架重建

- task_id：T-20261026-01
- 状态：completed（附带待用户处理的事项，见"收尾与交接"）
- 执行者：cursor/claude-opus-5.5（Cursor 经 Remote SSH 连到学校环境）
- 工作区与分支：/ai/workspace/AIE1903 · task/T-20261026-01-framework-rebuild，完成后以 --no-ff 合并到 main
- 开始时间与基准提交：2026-10-26 21:20 +08:00 · 203a73b（origin/main）
- 关联：交接文档 `docs/references/handoff-20261026/CURSOR_HANDOFF.md`；ADR-0001 至 ADR-0005

## 目标与范围

- **目标**（用户原话的要点）：
  - 依据交接包重新搭建项目，建好全部基础规范；
  - 写好 Cursor 指令文件、CLAUDE.md 和灵魂文件；
  - 建立执行记录与备份；
  - 规定好所有代码功能区，让以后的每次修改都有规范；
  - 做好 Git 管理；
  - 确认数据集是否齐全、项目是否完整；
  - 清理不需要的文件；
  - 推送到 GitHub。
- **本轮做**：上述全部内容。
- **本轮不做**：用户明确要求"暂时不开始训练，先不写代码"。因此交接文档 §11 中的可运行流程（doctor、audit-data、backtest、predict、validate-submission、verify-records）不在本轮实现。它们被拆成 roadmap 的 M1–M8，各功能区的契约已经写好。
- **指令冲突的处理**：交接文档 §11 要求"至少跑一次真实回测与预测"，而用户当次的指令是"先不写代码"。按照"用户当次的明确指令优先"的原则处理，并在此记录。

## 现状与必须保留的内容（初始审计，21:20–21:45）

- **Git**：main 与 origin/main 都在 203a73b，工作树干净，只有一个未跟踪的交接 zip。远端 origin 走 SSH（yixiangsunLeo/AIE1903），可以认证。仓库是**公开**的：匿名 `git ls-remote` 也能成功。
- **旧代码**：`src/aie1903_project/`（12 个模块）、`src/aie1903/`（re-export）、scripts/ 下 7 个入口、一个测试。已归档到标签 `archive/legacy-scaffold`。
- **旧结果**：`reports/backtest_metrics_cell30.json`（cell_30，旧协议），已保留到 `reports/legacy/`。
- **数据**：
  - cell_217 与 cell_30 共 8 个文件齐全，与官方逐字节一致；
  - grid_273 缺失；
  - `data_description_for_cell_217.pdf.fixed` 是冗余副本；
  - 根目录 `cell_217_data.tgz` 与 raw 完全相同；
  - 3 份 PDF 和 tgz 曾进入 Git 历史。
- **环境**：
  - 容器配额 24 核、32 GiB，一张 RTX 5090；
  - Python 3.12.3；镜像自带 numpy、pandas、torch；
  - 缺少 pytest、ruff、sklearn；
  - 学校环境没有 node 和 claude；
  - 没有正在运行的作业。
- **项目外**：`/ai/workspace/_gh_AIE1903/`、`_merge_stage/` 和两个 tgz 都是合并时留下的暂存件，内容已核实被 Git 历史完全覆盖。按约束，先没有动它们，等用户确认。

## 依赖与授权

- 推送 GitHub：用户在本任务中明确要求推送。
- 22:12 用户通过提问表单授权两件事：
  1. 由终端创建 `.cursorignore`，并提交推送；
  2. 删除项目外的 4 个暂存件。

## 预算

CPU，短时运行（单次审计不超过 3 秒），没有使用 GPU，没有训练。

## 预先验收标准

1. 三套代理指令（AGENTS、CLAUDE、Cursor 规则）共享同一份约定，引用的文件都真实存在，规则 frontmatter 能解析，globs 能匹配到真实路径。
2. 数据完整性有可复现的证据：与官方逐字节比对，并有 checksum 文件。
3. 功能区边界、依赖方向和接口草案都有文档，代码骨架可以导入。
4. 记录体系（任务、运行、决策、执行记录、AI 贡献、备份）有模板、有位置、有规则。
5. Git 规范有 hooks 强制执行，并通过正反例测试。
6. 冗余文件已清理，而且没有信息损失（旧内容可从标签或 references 中找回）。
7. 已推送到 GitHub，远端 HEAD 与本地一致。

## 实际改动

| 范围 | 改了什么 | 原因 |
|---|---|---|
| 代理指令 | 新增 SOUL.md、AGENTS.md；重写 CLAUDE.md（`@AGENTS.md`、`@SOUL.md`）；新增 5 条 `.cursor/rules/*.mdc` 和说明文件；新增 `.claude/rules/` 下 3 个符号链接；删除旧的 `.cursor/rules/aie1903.mdc`（内容已合并） | 让三套工具共享一份约定；Claude 只读 `paths` 字段，Cursor 只读 `globs`，这样可以共用一份源文件 |
| 文档 | 新增 docs/ 下的 project-context、agent-contract、architecture、roadmap、current-status、sources-and-open-questions、ai-use-log；standards/ 下 3 份；runbooks/ 下 3 份；tasks、decisions（5 条 ADR）、worklog、templates 各若干；references 中保存交接包 | 让事实、约定、状态、规范和手册各有固定位置，避免互相冲突 |
| 功能区 | 新增 `src/aie1903/` 下 9 个子包的骨架（只有 docstring）；删除 `src/aie1903_project/` 和旧的 re-export | ADR-0001 |
| 配置 | 新增 `datasets.yaml`、`runtime.yaml`、`experiments/_template.yaml`；`validation-plan.json` 改为 expanding_289_v1；删除 `default.yaml` | ADR-0002；集中管理参数 |
| 数据 | 补齐 grid_273 的 5 个文件；新增 `data/checksums.sha256`；删除 `.pdf.fixed` 和 tgz；PDF 取消 Git 跟踪 | 数据齐全，并能校验 |
| Git | 新增 `.githooks/`（commit-msg、pre-commit）、`.gitmessage`、`.gitattributes`、`.editorconfig`；重写 `.gitignore`；本地配置 `core.hooksPath` 和 `commit.template`；新增标签 `archive/legacy-scaffold` | 让规范真正被强制执行 |
| 环境 | 新增 `.venv`（system-site-packages）；重写 pyproject（包名 aie1903，版本 0.2.0，Python ≥3.11，加入 ruff 与 pytest 配置）；新增 `requirements.lock`；删除 `requirements.txt` | ADR-0004 |
| 清理 | 删除 scripts/ 下 7 个入口、`tests/test_imports.py`、空的 `figures/` 和 `artifacts/outputs/`、`.cursor/mcp.json`、`WORK_INSTRUCTIONS.md`、`docs/SYNC.md`（两者已合并进 runbooks）、交接 zip（内容已存入 references） | 去掉冗余；全部可以从标签或 references 找回 |
| 其他目录 | 新增 README：`tests/`、`scripts/`、`notebooks/`、`runs/`、`submissions/`、`reports/`、`reports/legacy/`、`data/`、`configs/`；新增 `reports/experiments.csv`（含一行 legacy 记录）和 `reports/runs/` | 每个目录都写明了契约 |

## 真实验证

| 命令 | 退出码 | 结果摘要 | 证据 |
|---|---|---|---|
| 与官方提交 49822d8 做 `git hash-object` 和字节数比对（13 个文件） | 0 | 13/13 一致（其中 grid_273 的 5 个文件是先下载到临时目录、校验通过后才放入） | 本卡；`configs/datasets.yaml` |
| `(cd data && sha256sum -c checksums.sha256)` | 0 | 13/13 OK | `data/checksums.sha256` |
| `python3 reports/audit/A-20261026-framework/audit_probe.py` | 0 | 132 PASS / 0 FAIL / 0 WARN / 4 INFO；耗时 2.9 秒 | `data-audit.json`、`environment.json` |
| `python3 -m venv --system-site-packages .venv && .venv/bin/python -m pip install -e '.[dev]'` | 0 | 用时 4.6 秒 + 12.2 秒；新装 pytest 9.1.1 和 ruff 0.17.2，其余包复用镜像 | `requirements.lock`、`pip-freeze-venv.txt` |
| `.venv/bin/python -m pytest` | 0 | 19 passed（9 个功能区的导入与说明检查、9 个契约章节检查、1 个版本一致性检查） | `tests/test_layout.py` |
| `.venv/bin/ruff check . && .venv/bin/ruff format --check .` | 0 | 通过（第一次运行时 architecture.md 中的示例代码需要格式化，已修正） | — |
| 在 `/tmp/hooktest` 临时仓库里测试 hooks | — | commit-msg：3 个正例放行、5 个反例被拒、中文标题放行；pre-commit：合法组合放行，原始 CSV、runs、提交 CSV、`.env`、NFS 垃圾文件、私钥、大于 2MB 的文件共 7 类被拦截，hook 文件本身不误报 | 本卡 |
| `.venv/bin/python reports/audit/A-20261026-framework/framework_check.py` | 0 | 150/150 通过（加入 `.cursorignore` 后） | `framework-check.json` |
| 在真实仓库中用不合规的提交信息执行 `git commit --allow-empty -m "update stuff"` | 1 | 被 commit-msg 拒绝，HEAD 不变 | 本卡 |
| 第一次推送：`git push origin main` 及两个标签，再执行 `git ls-remote origin` | 0 | 第一次尝试 DNS 解析失败，重试成功；远端 main 与 `v0.2.0^{}` 都是 f91a1f5，`archive/legacy-scaffold^{}` 是 203a73b，与本地一致 | worklog |
| `.cursorignore` 语义测试：在临时仓库里把它当作 `.gitignore` 执行 check-ignore | — | 密钥、原始数据、runs、提交 CSV、venv、缓存、`.!!!*` 都被排除；规则、文档、配置、checksum、提交 JSON 都可见 | 本卡 |
| 删除项目外的 4 个暂存件（已授权），删除前再次确认 cf8bdad 在 main 的历史中 | 0 | `/ai/workspace` 下只剩 `.ssh/` 和 `AIE1903/` | worklog |
| 第二次推送（本次补充合并） | 见会话汇报 | 推送后用 `git ls-remote` 核对；下一个会话开工时用 `git status -sb` 复核 | 会话汇报 |

**规则加载的实测（本会话内）**：

- 启动了一个只读子代理 [Verify loaded project rules](23f37518-f5c9-4361-8018-453858b09974)，要求它不读任何文件，直接回答验证问题。
- 结果：它看到的是本会话**开始时**的规则快照，即旧的 `aie1903.mdc` 和旧的 CLAUDE.md；AGENTS.md 和 SOUL.md 都不在它的上下文中。
- 结论：规则在会话开始时就固定了，本会话内无法验证新规则是否生效。

**未验证（如实说明）**：

- **在新的 Cursor 会话中实际加载规则**：规则的静态检查已经通过，但实际加载必须**新开一个 Cursor 会话**，再用下面的验证提问来确认。
- **Claude Code 实际加载 CLAUDE.md**：学校环境没有 claude，box 也不在本会话的访问范围内。方法：在 Claude Code 中运行 `/context`，确认 Memory files 中有 CLAUDE.md、AGENTS.md、SOUL.md。
- **验证提问**（让工具在不修改文件的前提下回答）："当前赛道、预测步长、日周期、禁止使用的未来信息、记录写在哪里、运行边界是什么？" 预期答案：cell_217；289；288；预测起点之后的任何真实值、sample 文件的数值、跨数据集数据；docs/tasks、runs、reports、worklog；CPU、8 线程、30 分钟、单任务，以及需要授权的事项清单。

## 对照交接文档的验收分类

| 分类 | 内容 |
|---|---|
| **已有并验证可用** | GitHub SSH 认证；cell_217 与 cell_30 的原始数据（逐字节一致）；学校持久盘 |
| **本轮新增或修复，并已验证** | grid_273 数据；checksum 文件；数据合同审计；SOUL、AGENTS、CLAUDE 与规则（静态检查）；功能区骨架（pytest）；hooks（正反例）；venv（pip、pytest、ruff）；记录体系与模板；`.gitignore`（check-ignore 检查，见 framework-check）；`.cursorignore`（经授权创建，语义已测试）；GitHub 推送（ls-remote 核对一致） |
| **存在但未验证** | 新会话中规则的实际加载、Claude Code 的加载（原因见上）；Grokbot 运行手册还没有被 Grokbot 实际执行过 |
| **缺失且阻塞** | GitHub 仓库目前公开，与课程"私有仓库"的要求不符（需要学生在 GitHub 上操作） |
| **按用户指令推迟** | 交接文档 §11 的可运行流程，即真实回测与 289 步预测 → roadmap M1–M8 |
| **可选，未做** | grid_273 的建模、大模型实验、`.claude/settings.json` 的权限加固（Claude Code 无法在本环境中验证，所以暂不加入未经验证的配置） |

## `.cursorignore`（22:13 经用户授权，由终端创建；内容如下）

Cursor 的 Write 工具对这个文件返回 "Blocked by permissions configuration"，所以没有绕过，而是先请求授权，再由终端写入。

```gitignore
# Keeps secrets and bulk files out of Cursor's indexing and default context.
# It does NOT stop terminal or MCP tools from reading files; the data and secret rules still apply.
# Never ignore AGENTS.md, CLAUDE.md, SOUL.md, .cursor/rules/, docs/ or configs/.
**/.env
**/.env.*
!**/.env.example
**/*.pem
**/*.key
**/id_rsa*
**/id_ed25519*
.ssh/
.agent-lock
data/raw/
data/interim/
data/processed/
runs/
submissions/**/*.csv
artifacts/models/
logs/
backups/
.venv/
**/__pycache__/
.pytest_cache/
.ruff_cache/
**/.!!!*
```

## 收尾与交接

- **结果**：框架 v0.2.0 完成，验收标准 1–7 全部满足。第 7 项的依据是第一次推送后 `ls-remote` 核对一致；第二次推送的核对见会话汇报。
- **回退办法**：
  - 查看旧状态：`git worktree add /tmp/aie1903-legacy archive/legacy-scaffold`。**不要**在主工作树里检出旧提交，原因见 git-workflow §5.1。
  - 撤销合并：`git revert -m 1 <merge>`，不需要改写历史。
- **执行中的事故**：合并前我曾在主工作树中切换到旧的 `main`，再合并回来，导致两份取消跟踪的 PDF 被 git 从磁盘删除。`sha256sum -c` 立刻发现了问题；已从 `archive/legacy-scaffold` 恢复，blob 与官方一致，13/13 校验 OK。防范办法已写入 git-workflow §5.1 和 data/README.md 的"恢复"一节。
- **已由用户决定并完成**：`.cursorignore` 已创建；项目外的 4 个暂存件已删除。
- **待用户处理的事项**：
  1. 把仓库改为私有，并添加课程人员与组员；
  2. 复核 ADR-0002 与 ADR-0003；
  3. 决定 Claude Code 的运行模式；
  4. 决定是否向课程方反馈 sample 问题；
  5. 填写团队信息；
  6. 新开一个 Cursor 会话，验证规则是否加载。
- **下一步**：M1 数据层（见 current-status 的"下一步"）。
- **记录同步**：CHANGELOG [x] · current-status [x] · worklog [x] · ai-use-log [x] · experiments.csv [x]（已登记 legacy 行）。
- **人工复核**：pending。
