# legacy/（未验证的旧结果）

## backtest_metrics_cell30.json

- **来源**：重建前的旧代码，在提交 6c2d40e 和 203a73b 中生成，代码保存在标签 `archive/legacy-scaffold`。它是 cell_30 上季节朴素基线的回测结果，使用的是旧验证协议 `aie1903-chronological-289`：fold_day4、fold_day5（截断为 288 步）、fold_last289。
- **缺失的元数据**：没有 run_id、代码提交号、数据哈希、环境信息、指标计数，也没有记录耗时和内存。
- **状态**：`legacy_unverified`。它所用的 fold 与现行协议 expanding_289_v1 不一样，不能和新结果直接比较。
- **用途**：只用来粗略了解演练数据集上基线指标的量级。正式基线结果以 M5 的运行记录为准。
