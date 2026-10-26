# runs/

每次运行的**完整产物**都放在 `runs/<run_id>/`。这个目录只保存在持久盘上，不进 Git（本 README 除外）。

```text
runs/<run_id>/
├── run.json             运行元数据（开始时创建，结束时补全；模板见 docs/templates/run-record.json）
├── config.resolved.yaml 解析后的配置快照
├── environment.json     环境快照
├── stdout.log           日志
├── predictions/         各 fold 的预测（以及最终预测）
└── figures/             图
```

- run_id 的格式与字段要求见 `docs/standards/records.md`。
- 每次运行的小型摘要另写到 `reports/runs/<run_id>.json`，并在 `reports/experiments.csv` 中加一行，这两者进 Git。
- 备份方式见 `docs/runbooks/sync-backup-release.md` §2。
