# ADR-0003 指标口径 provisional-v1

- 状态：accepted-provisional（按授权矩阵，指标口径需要学生确认；拿到官方评分代码后再冻结）
- 日期：2026-10-26
- 提出与执行：cursor/claude-opus-5.5（T-20261026-01）
- 学生复核：pending

## 背景

两份官方 PDF 对 Masked MAPE 的写法不一致：

- 217PDF §12：公式分母写的是 n，但紧接着说明"阈值之外的位置不参与该项平均"；
- CGPDF §12：分母写的是 n′，即保留下来的位置数。

目前没有拿到官方评分代码。

## 决策（版本 `provisional-v1`）

| 指标 | 定义（y 为真实值，ŷ 为预测，均为原始计数尺度） |
|---|---|
| MAE | 对全部位置求 \|ŷ−y\| 的均值 |
| RMSE | 对全部位置求 (ŷ−y)² 的均值，再开平方 |
| MAPE（cell） | 100 × 对全部位置求 \|ŷ−y\|/y 的均值（cell 的真实值都 ≥1，不会除以 0） |
| MAPE（grid） | 100 × 只对 y>0 的位置求均值 |
| Masked MAPE @t | 100 × 只对 y≥t 的位置求 \|ŷ−y\|/y 的均值；cell 的 t 为 3e5 和 1e6，grid 的 t 为 1e4 和 1e5 |

计算规则：

- mask 只由真实值决定，与预测值无关。
- 在**全部保留位置上整体平均**。不先算每条序列的平均再等权平均，因为各序列的有效数量不同，两种算法结果会不一样。
- 每个指标都输出 `{value, count}`；masked 指标还要附上 `threshold`。
- 保留位置为空时，输出 `value = null`、`count = 0`，不输出 0 或 NaN。
- 不加 epsilon，不改变官方关于 0 值的规则。
- 回测按 fold 分别计算，汇总时报告各 fold 的值和均值。用变换尺度上的损失（log、MSE）训练没有问题，但不得把它们称作官方指标。

## 后果

- 记录里要注明 `metric_definition_version: provisional-v1`；口径一旦变化，历史结果需要重算或另行标注。
- 拿到官方评分代码后，新建一条 ADR，冻结为 v1 或修订。

## 证据

- `docs/project-context.md` §5
- 217PDF 与 CGPDF 的 §12
