# reports/

这个目录存放可以进 Git 的小型脱敏证据和报告素材。

| 路径 | 内容 |
|---|---|
| `audit/<audit_id>/` | 审计报告与证据，例如 `A-20261026-framework`（数据、环境与框架审计） |
| `runs/<run_id>.json` | 每次运行的摘要；完整产物在 `runs/<run_id>/`，不进 Git |
| `experiments.csv` | 实验索引，一次运行一行，列定义见 `docs/standards/records.md` §4 |
| `figures/`、`tables/` | 选入最终报告的图表，必须能由记录的运行重新生成 |
| `legacy/` | 重建之前的旧结果，**未经验证**，只作参考 |

不要把任何测试真值、原始数据或大文件放进这里。
