# 规则文件说明

Cursor 只识别带 frontmatter 的 `.mdc` 规则，所以这份 `.md` 说明不会被当成规则加载。

| 文件 | 适用范围 | Cursor | Claude Code |
|---|---|---|---|
| `00-project.mdc` | 全局硬约束、开工顺序 | 始终加载（`alwaysApply: true`） | 不链接；同样的内容通过 CLAUDE.md 导入 AGENTS.md 获得 |
| `10-forecasting.mdc` | 时间边界、数据语义、指标 | 匹配 `globs` 时加载 | `.claude/rules/10-forecasting.md`（符号链接，按 `paths` 加载） |
| `20-records.mdc` | 任务、提交、运行与记录 | 始终加载 | 不链接；记录要求已写在 AGENTS.md 中 |
| `30-server.mdc` | 资源、持久化、进程 | 匹配 `globs` 时加载 | `.claude/rules/30-server.md`（符号链接） |
| `40-code-structure.mdc` | 功能区边界与写法 | 匹配 `globs` 时加载 | `.claude/rules/40-code-structure.md`（符号链接） |

## 维护约定

- **单一源文件。** Claude Code 只读取 frontmatter 里的 `paths` 字段，会忽略其他字段；Cursor 读取 `description`、`globs` 和 `alwaysApply`。所以按路径生效的规则同时写 `globs` 和 `paths`，两者的值必须**保持一致**。
- **新增按路径生效的规则时**，要在 `.claude/rules/` 下建一个同名的 `.md` 符号链接：`ln -s ../../.cursor/rules/<name>.mdc .claude/rules/<name>.md`。
- **控制篇幅。** 每条规则大约 50 行以内；细则放在 docs/，用路径引用。注意：Cursor 不会把被引用文件的内容内联进来，必须常驻上下文的内容要直接写进规则正文。
- **修改后要检查**：frontmatter 能被 YAML 解析；globs 能匹配到真实文件；规则里引用的路径都存在。M7 的 `verify-records` 会把这些检查自动化。
