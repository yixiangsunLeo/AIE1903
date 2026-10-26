# 参考资料（只读）

这里存放的是**输入材料**，不是生效的规则。请不要修改原文。

## handoff-20261026/

2026-10-26 交接包 `aie1903-cursor-handoff.zip` 的完整内容。原 zip 已删除，其中内容全部保存在这里，没有任何损失。

| 文件 | 用途 | 现在合并到了哪里 |
|---|---|---|
| `CURSOR_HANDOFF.md` | 本轮框架建设的需求与验收要求 | 已落实到 AGENTS.md、docs/、configs/；需求逐项的落实情况见任务卡 T-20261026-01 |
| `official-data-inventory.json` | 官方文件清单快照（git blob SHA-1） | `configs/datasets.yaml` 中的 `files` 部分 |
| `validation-plan.json` | 建议的验证协议 | `configs/validation-plan.json`（ADR-0002） |
| `templates/*.template` | 规则与模板的参考写法 | 已合并为正式文件（`.cursor/rules/`、`docs/templates/`、`.gitignore`、`.cursorignore`、`docs/runbooks/grokbot.md`）。**模板本身不生效** |
