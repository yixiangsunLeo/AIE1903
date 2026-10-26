# ADR-0006 规则唯一源与多代理适配

- 状态：accepted（用户的明确要求是"以后所有规则必须是 Cursor 以及 Claude 或者其他 agent 都能通读的"；具体实现方案待学生复核）
- 日期：2026-10-26
- 提出与执行：cursor/claude-opus-5.5（T-20261026-02）
- 学生复核：pending

## 背景

T-20261026-01 时，规则的源文件放在 `.cursor/rules/*.mdc`，Claude Code 通过 `.claude/rules/` 的符号链接读取其中 3 条。这样有三个问题：

1. **源文件藏在工具专用的隐藏目录里。** Grokbot、Codex、Gemini CLI 等代理既不会自动加载它，AGENTS.md 也没有要求它们去读。
2. **Claude Code 只拿到 3 条按路径生效的规则。** 两条全局规则没有链接过去。
3. **Cursor 不会自动加载 SOUL.md。**

已核实的工具行为：

- Cursor 要求规则是带 frontmatter 的 `.mdc` 文件；规则里引用的文件内容不会展开到上下文里；Cursor 会自动加载 AGENTS.md。
- Claude Code 只读取规则 frontmatter 里的 `paths` 字段；`.claude/rules` 支持符号链接；同时存在 CLAUDE.md 和 AGENTS.md 时，只读 CLAUDE.md。
- 很多代理都会自动读取 AGENTS.md。

## 决策

1. **唯一源**：`rules/*.md`，纯 Markdown 加 YAML frontmatter（description、alwaysApply；按路径生效的规则再写 globs 和 paths，两者取值相同），任何代理都能直接读。
2. **Cursor 适配**：`scripts/sync-rules.sh` 生成 `.cursor/rules/*.mdc`，是**真实的文件副本**。另外把 SOUL.md 生成为 `05-soul.mdc`（alwaysApply），让 Cursor 始终带着项目之魂。
3. **Claude Code 适配**：`.claude/rules/*.md` 是指向 `../../rules/*.md` 的符号链接，覆盖全部 6 条规则。CLAUDE.md 继续导入 AGENTS.md 和 SOUL.md。
4. **其他代理**：AGENTS.md 作为通用入口，列出全部规则，并要求开工时读完 `rules/`。不会自动读 AGENTS.md 的代理，要在启动提示词里写明这一要求。
5. **一致性强制**：
   - pre-commit 在提交涉及规则文件时，要求没有漏暂存的改动，并执行 `scripts/sync-rules.sh --check`；
   - `scripts/check-framework.py` 检查 frontmatter、globs 与 paths 是否一致、规则是否已列入 AGENTS.md，以及适配副本是否同步。
6. 新增 `30-server.md` 的实测事实，以及 `35-training.md` 训练规则。二者都是全局规则，因为运行命令时不一定会碰到任何源码文件，按路径生效的规则未必会被加载。

## 备选方案

- **继续把源文件放在 `.cursor/rules/`**：其他代理读不到，不满足用户的要求。
- **把 `.cursor/rules/*.mdc` 也做成符号链接**：无法在本会话中验证 Cursor 是否会跟随符号链接。万一不支持，规则会在不报错的情况下没有加载，风险太大，所以改用生成真实副本，再加一致性检查。
- **把所有规则都塞进 AGENTS.md**：文件会过长，失去按路径加载的能力，规则与入口说明也会混在一起。

## 后果

- 必须同时维护两个生成目录。直接编辑它们会被下一次同步覆盖，hook 会拦下不一致的提交。
- Claude Code 启动时会加载 00、20、30、35 四条全局规则，再加上 AGENTS.md 和 SOUL.md。其中红线部分有少量重复，这是有意为之，作为安全冗余。
- 新规则要在**新会话**中才会生效。本会话实测显示，Cursor 和子代理用的都是会话开始时缓存的规则。

## 证据

- `rules/README.md`
- `scripts/sync-rules.sh`
- `.githooks/pre-commit`
- `scripts/check-framework.py` 的输出：`reports/audit/A-20261026-server/framework-check.json`
- 任务卡 T-20261026-02 中的规则加载实测
