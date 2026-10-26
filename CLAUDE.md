@AGENTS.md
@SOUL.md

# Claude Code 入口（AIE1903）

上面导入的两个文件分别是共享约定和项目之魂。本文件只补充 Claude Code 专属的事项，保持简短，不另写一套项目事实。

## 开工

- 先运行 `/context`，确认 Memory files 里有本文件、AGENTS.md 和 SOUL.md；缺任何一个就停下并报告，不要继续修改。
- 读完 `docs/current-status.md` 和当前任务卡再动手，不凭聊天记忆判断版本。
- 规则的唯一源是 `rules/`。`.claude/rules/` 中是指向它的符号链接，由 `scripts/sync-rules.sh` 生成：全局规则（00、20、30、35）在启动时加载，路径规则（10、40）在读写匹配的文件时加载。如果 `/context` 里看不到规则，就直接读 `rules/` 下的全部文件。
- 要改规则时，只改 `rules/*.md`，再运行 `scripts/sync-rules.sh`。不要直接编辑 `.claude/rules/` 或 `.cursor/rules/`。
- 同一工作树只允许一个写入者：开工前检查并写入 `.agent-lock`，结束时删除（docs/agent-contract.md §1）。

## 运行方式

- 访问方式和运行模式见 `docs/runbooks/environment.md`。现行模式是：Claude Code 跑在管理端 box 上，经 CC Switch 调用模型；学校环境没有 node 和 claude，通过 `aie1903-ssh` 在学校环境执行命令。
- 项目命令一律在学校环境的项目根执行：`cd /ai/workspace/AIE1903 && …`；Python 用 `.venv/bin/python`。
- 训练和长时间运行一律按 `docs/runbooks/training.md` §4 的模板启动：`setsid nohup`、显式设置线程数、`timeout` 预算、记录 PID。通过 ssh 执行时同样如此，否则 ssh 一断开，任务就会被结束。
- 绝不打印 `aie1903-env.env` 中的密码。

## 非交互调用（Grokbot）

- 用 `claude -p` 调用时，提示词里必须写明 task_id、预算和验收标准；执行结果要回写到任务卡和 worklog。
- 不使用会跳过权限检查或绕过项目指令的启动参数。

## 收尾

按 AGENTS.md 的"每项任务的必做事项"更新记录。提交时 hooks 会检查提交信息和禁止入库的文件；推送需要用户授权。
