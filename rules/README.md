# rules/：全部强制规则的唯一源

这里的规则必须能被 **Cursor、Claude Code 以及其他任何代理**完整读到（用户要求，ADR-0006）。因此：

- 规则只写在这里，用纯 Markdown 加 YAML frontmatter；
- 各工具专用的位置只放由脚本生成的副本或符号链接。

## 规则清单

| 文件 | 适用范围 | 内容 |
|---|---|---|
| `00-project.md` | 全局 | 开工顺序、红线、需要授权的事项、规则维护方式 |
| `10-forecasting.md` | src、tests、configs、notebooks | 时间边界、数据语义、官方指标口径 |
| `20-records.md` | 全局 | 任务卡、分支与提交、运行记录、收尾 |
| `30-server.md` | 全局 | 学校服务器的事实、资源上限、持久化、网络、软件、进程 |
| `35-training.md` | 全局 | 训练与运行：预算、线程、精度、确定性、启动、监控、记录 |
| `40-code-structure.md` | src、tests、scripts、notebooks | 功能区边界、依赖方向、写法 |

此外，`SOUL.md` 与 `AGENTS.md` 也属于必读内容，但它们放在项目根目录，不在本目录。

## 各代理如何读到这些规则

| 代理 | 自动加载的内容 | 怎么拿到全部规则 |
|---|---|---|
| **Cursor** | `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/*.mdc` | `.cursor/rules/` 是 `scripts/sync-rules.sh` 生成的**真实副本**（Cursor 要求规则是真实的 `.mdc` 文件）。另外生成一条 `05-soul.mdc`，内容就是 SOUL.md，所以 Cursor 也始终带着项目之魂 |
| **Claude Code** | `CLAUDE.md`（用 `@` 导入 AGENTS.md 和 SOUL.md）、`.claude/rules/*.md` | `.claude/rules/` 下是指向本目录的**符号链接**。没有 `paths` 字段的规则在启动时加载；有 `paths` 的规则在读写匹配文件时加载 |
| **其他代理**（Grokbot、Codex、Gemini CLI 等） | 多数会自动读取 `AGENTS.md` | `AGENTS.md` 要求开工时读完 `rules/` 下的全部文件。如果某个代理不会自动读 AGENTS.md，就在它的启动提示词里写明："先读 AGENTS.md、SOUL.md 和 rules/ 下全部规则" |

## 维护规则的流程

1. 只改 `rules/*.md`（或 SOUL.md），而且要走任务流程（任务卡 + 分支）。
2. 运行 `scripts/sync-rules.sh`，重新生成 `.cursor/rules/` 和 `.claude/rules/`。
3. 把 `rules/`、`.cursor/rules/`、`.claude/rules/` 一起提交。pre-commit 会执行 `scripts/sync-rules.sh --check`：副本不一致、符号链接损坏，或者有改动没暂存，都会拦下这次提交。

不要直接编辑 `.cursor/rules/` 或 `.claude/rules/`，下一次同步会覆盖这些改动。

## 写规则的要求

- **自包含**：必须知道的约束要直接写进正文。Cursor 不会把规则中引用的文件内容展开到上下文里，其他代理也未必会去读引用的文件。
- **frontmatter 的写法**：
  - 全局规则：`alwaysApply: true`，不写 globs 和 paths；
  - 按路径生效的规则：`alwaysApply: false`，`globs`（给 Cursor）与 `paths`（给 Claude Code）写**完全相同的值**；
  - 每条规则都要写 `description`。
- **长度**：每条大约 60 行以内，细节放到 docs/ 中，再在规则里写明路径。
- **证据**：规则里引用的事实，要写明出处，比如审计 ID 或文档路径。事实发生变化时，先更新审计和文档，再改规则。
