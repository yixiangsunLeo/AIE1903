# 决策记录（ADR）

这里只记录**会影响后续工作**的决定，包括协议、口径、结构、环境和数据使用规则。日常实现细节写在任务卡里。

- 模板：`docs/templates/adr.md`。编号按顺序递增，从不复用。
- 状态取值：`proposed`、`accepted`、`accepted-provisional`（暂行采用，待学生复核）、`superseded by ADR-XXXX`。
- 代理可以提出决定，也可以暂行采用；学生复核后，在 ADR 里改状态并签上名字。
- 已经采用的 ADR 不要改写原文；需要变更时，新建一条 ADR 并标明它取代了哪一条。

| 编号 | 标题 | 状态 | 日期 |
|---|---|---|---|
| [ADR-0001](ADR-0001-single-package-functional-areas.md) | 单一包 `aie1903` 与九个功能区 | accepted | 2026-10-26 |
| [ADR-0002](ADR-0002-validation-protocol-expanding-289-v1.md) | 验证协议采用 expanding_289_v1 | accepted-provisional | 2026-10-26 |
| [ADR-0003](ADR-0003-provisional-metric-definitions.md) | 指标口径 provisional-v1 | accepted-provisional | 2026-10-26 |
| [ADR-0004](ADR-0004-environment-venv-system-site-packages.md) | 项目 venv 复用镜像包 | accepted | 2026-10-26 |
| [ADR-0005](ADR-0005-dataset-isolation-and-sample-files.md) | 数据集隔离与 sample 文件禁用 | accepted | 2026-10-26 |
