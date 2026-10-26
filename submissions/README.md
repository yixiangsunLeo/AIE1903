# submissions/

```text
submissions/<dataset_id>/<run_id>.csv    提交文件（不进 Git）
submissions/<dataset_id>/<run_id>.json   对应的元数据，记录 run_id、代码版本、校验结果、sha256（进 Git）
```

- 只能由 `predict` 流程生成（roadmap M6），并且必须先通过 `validate-submission`。
- 正式提交到竞赛平台需要学生授权，提交时间和结果要记在任务卡里。
- 不能用 sample 文件、随机数或手工编辑过的数值冒充预测。
