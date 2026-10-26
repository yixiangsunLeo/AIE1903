---
description: 时序数据合同、无泄漏预测与官方指标
globs: src/**/*.py,tests/**/*.py,configs/**,notebooks/**
paths: src/**/*.py,tests/**/*.py,configs/**,notebooks/**
alwaysApply: false
---

# 预测与评估规则

依据：docs/project-context.md（数据合同）、configs/datasets.yaml、configs/validation-plan.json、ADR-0002、ADR-0003、ADR-0005。

**时间边界**
- 只做前向回测。fold 由 configs/validation-plan.json 定义，索引从 0 开始、区间左闭右开；默认只用 dev_a 和 dev_b，heldout 需要用户批准。
- 预测 289 步的过程中，不注入任何真实中间值；predict 接口只接收步数，不接收任何未来数据。
- 标准化、阈值、聚类、相关矩阵、特征选择、融合权重，都只在当前 fold 的训练段上拟合。
- 监督样本按"目标窗口"切分：全部目标都要落在训练段内，不能只看输入窗口的起点。
- 每个特征都要声明源时刻偏移，只能使用起点之前的值。第 289 步的 lag-288 已经越界，应改用周期延拓 train[-288 + h % 288]。
- 预测窗口的时间戳本身是公开的，可以用来构造日历特征，但不得按服务器时区转换。

**数据语义**
- 使用原始计数尺度，单位是匿名的。cell 的训练值都 ≥1，没有 0；grid 的 0 既有补零也有真实零，不要断言某个 0 的来源。
- 父小区与子网格的流量不要求加总相等；序列编号不代表地理上相邻。
- 一个运行只用一个数据集。cell_30 的时间标签比 cell_217 晚 50 分钟，禁止跨目录对齐或拼接（唯一例外：grid_273 与 cell_30 的层级关系，见 ADR-0005）。
- 任何 sample_submission 的数值都不读取；格式校验以 test.csv 为模板。

**指标**（ADR-0003，provisional-v1）
- 五项指标：MAE、RMSE、MAPE(%)、两项 Masked MAPE。都在原始尺度上计算，并在全部保留位置上整体平均。
- cell：MAPE 计全部位置，阈值为 3e5 和 1e6。grid：MAPE 只计 y>0 的位置，阈值为 1e4 和 1e5。
- mask 只看真实值；每项都报告计数；空 mask 输出 value=null、count=0；不加 epsilon。
- 在变换尺度上算的损失（log、MSE），不能与官方指标混称。
