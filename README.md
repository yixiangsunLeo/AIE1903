# AIE1903 — Wireless uplink traffic forecasting

课程项目：无线网络上行流量预测（5 分钟粒度）。主线 **cell_217**；流程调通可用 **cell_30**。

Course project: multi-series 289-step forecasting. Persist all durable work on school volume **sun** at `/ai/workspace/AIE1903`.

## Data

| Dataset | Path | Notes |
|---------|------|-------|
| cell_217 (mainline) | `data/raw/cell_217/` | train 1728 × 217, test 289 × 217 |
| cell_30 (dry-run) | `data/raw/cell_30/` | smaller subset |
| Official repo | https://github.com/AIE1903-DataCompetition-26AY/competition-data | re-download CSVs if needed |

Day cycle = **288** steps; forecast horizon = **289**.

## Setup (on school env)

```bash
cd /ai/workspace/AIE1903
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
```

## Run

```bash
python3 scripts/smoke_import.py
python3 scripts/audit_data.py
python3 scripts/run_backtest.py --dataset cell_30    # dry-run
python3 scripts/run_backtest.py --dataset cell_217
python3 scripts/run_baseline.py --dataset cell_217   # writes runs/*_submission.csv
```

Validation plan: `configs/validation-plan.json`. Metrics: MAE, RMSE, MAPE, Masked MAPE@3e5, Masked MAPE@1e6.

## Operator / SSH (from shared box)

```bash
~/.local/bin/cuhksz-vpn-up          # if SSH fails
~/.local/bin/cuhksz-vpn-status
/home/box/.local/bin/aie1903-ssh 'echo OK'
# Claude Code on box with CC Switch:
export ANTHROPIC_BASE_URL=http://127.0.0.1:15721
claude --model claude-opus-5 -p "..." --permission-mode bypassPermissions
```

Never use research SSH `10.27.126.205`. See `CLAUDE.md` and `docs/SYNC.md`.

## Sync & release

1. Keep code/data/keys only under `/ai/workspace`.
2. Commit locally on disk; push GitHub only after user registers the pubkey.
3. Before releasing env `111`: **保存镜像** + disk sync (+ GitHub if ready), then release.
