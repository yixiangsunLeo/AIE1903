# AIE1903 — Wireless Network Traffic Forecasting

Competition / course project: forecast multi-cell wireless **uplink** traffic.
**Mainline dataset: cell_217** (217 cells). Use **cell_30** for pipeline dry-runs.

This repository merges the prior group engineering skeleton (`aie1903_project` layout)
with the competition baseline (metrics, seasonal-naive, validation backtest).

## Persistent path (school AI platform)

```text
/ai/workspace/AIE1903
```

Mount volume **`sun`** at `/ai/workspace`. Do **not** keep durable state only on the
ephemeral container disk (`/workspace`, `/root`, `/tmp`).

## Layout

```text
AIE1903/
├── configs/                 # default.yaml + validation-plan.json
├── data/{raw,interim,processed}
├── src/aie1903_project/     # canonical package
├── src/aie1903/             # thin re-export for compatibility
├── scripts/                 # train / evaluate / predict + audit / backtest / smoke
├── artifacts/{models,outputs}
├── reports/{figures,tables}
├── tests/
├── docs/SYNC.md
├── CLAUDE.md
└── .cursor/rules/
```

Raw CSVs under `data/raw/**` are gitignored; they stay on the school disk.

## Quick start (on school env)

```bash
cd /ai/workspace/AIE1903
PYTHONPATH=src python3 scripts/smoke_import.py
PYTHONPATH=src python3 scripts/audit_data.py --dataset cell_30
PYTHONPATH=src python3 scripts/run_backtest.py --dataset cell_30 --out reports/backtest_metrics_cell30.json
PYTHONPATH=src python3 scripts/run_baseline.py --dataset cell_30
# aliases:
PYTHONPATH=src python3 scripts/evaluate.py --dataset cell_30
PYTHONPATH=src python3 scripts/predict.py --dataset cell_217
```

## Metrics (lower is better)

MAE, RMSE, MAPE (%), Masked MAPE @ 3e5, Masked MAPE @ 1e6.

## Baseline

Seasonal-naive daily cycle (`day_cycle=288`, forecast horizon `289`).

## School env SOP

1. VPN up → create env `111` with image `jr/jr1903`, mount `sun` → `/ai/workspace`
2. Work only under `/ai/workspace/AIE1903`
3. After meaningful progress: commit + push allowed artifacts to GitHub
4. Before release: save image, disk sync, GitHub sync, then release env

## Credits

- GitHub skeleton: pre-existing group project layout (`aie1903_project`, pyproject, artifacts/…)
- Competition scaffold / baseline: operator + Claude Code (CC Switch → gpt-6.1-sol) on school disk
