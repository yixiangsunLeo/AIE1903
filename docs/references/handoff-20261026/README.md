# AIE1903 Cursor 交接包使用说明

先将 `CURSOR_HANDOFF.md` 提供给已经连接学校服务器、打开实际项目的 Cursor。主文档本身包含课程背景、赛道、文件合同、代理规则、改动与实验记录、服务器审计、实施顺序和验收要求，不依赖此前聊天。

如果方便传整个包，解压到项目中的一个明确交接资料目录，再让 Cursor 阅读主文档。解压出来的是交接材料，不是一个已经搭好的预测项目；不要让 Cursor 在交接目录另建平行项目。

## 文件用途

- `CURSOR_HANDOFF.md`：核心执行文档，优先完整阅读。
- `official-data-inventory.json`：2026年10月26日核对的官方文件清单、字节数、Git blob标识和预期数据合同；不是服务器本地数据检查结果。
- `validation-plan.json`：建议的289步前向开发切分；已有经用户确认的合法协议优先。
- `templates/AGENTS.md.template`：跨工具的项目入口参考。
- `templates/CLAUDE.md.template`：通过`@AGENTS.md`共享约定的Claude Code入口参考。
- `templates/cursor-rules/*.mdc.template`：Cursor规则参考，待合并到实际项目的`.cursor/rules/*.mdc`。
- `templates/gitignore.template`、`templates/cursorignore.template`：按真实路径合并的忽略规则参考。
- 其余模板：任务卡、运行元数据和Grokbot接手流程。

## 使用边界

所有`.template`文件都是参考材料，需由Cursor审计后合并、去掉模板后缀并放到正式路径；不要批量覆盖现有文件。先创建规则要引用的共享文档，再检查规则实际加载。

本包不包含原始课程PDF、真实训练CSV、账号密码或学校服务器路径。课程材料中影响本轮的要求已经转写在主文档中；实际缺项由Cursor在服务器核实。官方公开数据可按主文档补齐，课程原件如已在服务器应保留只读。

编写者未登录学校服务器，未执行远程项目重构或训练。本包的本地检查只验证文档、模板与参考清单的一致性，不代表服务器已经通过验收。
