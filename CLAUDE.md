# CLAUDE.md — AIE1903 operator instructions

You are assisting on the CUHK-SZ School of AI **AIE1903** course project (wireless uplink traffic forecasting). Drive work so the student can reproduce, validate fairly, and explain results. Record AI vs teammate contributions honestly.

## Environment & access

1. Campus VPN on the shared box: `~/.local/bin/cuhksz-vpn-{up,status,down}` (flaky — restart then retry SSH).
2. AI platform UI proxy: `http://127.0.0.1:18080/` → cluster.
3. SSH helper: `/home/box/.local/bin/aie1903-ssh` (password from private `aie1903-env.env` — **never print the password**).
4. Current pattern: `root@10.27.126.1 -p <dynamic>` via the helper.
5. **NEVER** use research SSH host `10.27.126.205` for this course.
6. Claude Code runs on the **box** with CC Switch: `ANTHROPIC_BASE_URL=http://127.0.0.1:15721`. Prefer `--model claude-opus-5` (maps to gpt-6.1-sol). Remote has no Claude/node — edit remote via `aie1903-ssh` / scp.
7. Env name `111`, image `jr1903:0.0.1`, mount volume **sun** at `/ai/workspace`.

## Persistence (non-negotiable)

- Project root: **`/ai/workspace/AIE1903`**.
- All durable state (code, data, `.git`, `.cursor`, `CLAUDE.md`, keys, meaningful runs) **only** under `/ai/workspace`.
- Ignore NFS junk files named `.!!!*`. Do not delete the whole disk; work inside `AIE1903`.

## Problem constraints

- Mainline: **cell_217**. Dry-run: **cell_30**. Extend to **grid_273** only after mainline.
- Train 1728 rows (6 days); test **289** steps; day cycle **288**.
- **No future leakage**: no test labels; features only from information available before each timestamp.
- Official metrics (lower better): MAE, RMSE, MAPE, Masked MAPE @ 3e5, Masked MAPE @ 1e6.
- Baseline: seasonal-naive daily cycle — `train[-288 + (h % 288)]` for horizon `h`.
- Validation: `configs/validation-plan.json` (chronological holdouts inside train).

## GitHub

- Key path: `/ai/workspace/.ssh/id_ed25519_github` (+ `config` Host github.com).
- **Ask the user** before adding the public key to GitHub or pushing.
- Do not commit secrets, private keys, or large raw CSVs (see `.gitignore`).

## After each batch / before release

1. Commit on persistent disk.
2. Sync GitHub when allowed.
3. Before **释放** env: save image (**保存镜像**) + confirm disk sync (+ GitHub), then release.

## Useful commands

```bash
/home/box/.local/bin/aie1903-ssh 'cd /ai/workspace/AIE1903 && python3 scripts/smoke_import.py'
/home/box/.local/bin/aie1903-ssh 'cd /ai/workspace/AIE1903 && PYTHONPATH=src python3 scripts/audit_data.py'
```

See `README.md` and `docs/SYNC.md`.
