# Sync checklist — school disk + GitHub

## Persistent storage (mandatory)
- Project root: `/ai/workspace/AIE1903` on volume **sun**.
- Durable artifacts only under `/ai/workspace` (code, data, `.git`, `.cursor`, keys, runs worth keeping).
- Never rely on the container ephemeral root disk.

## After each meaningful work batch
1. Confirm files under `/ai/workspace/AIE1903` are written (NFS flush: `sync` if unsure).
2. `git -C /ai/workspace/AIE1903 status` → commit allowed artifacts.
3. Sync GitHub when SSH key is registered (ask user first):
   - Key: `/ai/workspace/.ssh/id_ed25519_github`
   - Config: `/ai/workspace/.ssh/config`
4. Do **not** commit: `.env`, private keys, raw large CSVs (ignored), weights.

## Before releasing the development environment
1. Save platform image if offered (**保存镜像** → reuse `jr/jr1903`).
2. Disk sync complete (this checklist).
3. GitHub sync of allowed code/docs (or explicitly deferred with user OK).
4. Only then **释放/删除** env `111` to stop billing.

## Raw data
- Official: https://github.com/AIE1903-DataCompetition-26AY/competition-data
- Local: `data/raw/cell_217/`, `data/raw/cell_30/`
- Prefer re-download over committing CSVs.

## Never
- Research SSH `10.27.126.205` for this course.
- Push secrets or register GitHub keys without user approval.
