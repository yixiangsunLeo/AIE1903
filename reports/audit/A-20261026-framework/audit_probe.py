#!/usr/bin/env python3
"""One-off audit probe for task T-20261026-01 (framework rebuild).

Evidence only: verifies the official data files against the data contract and
records the runtime environment. It is NOT the project's data layer; the
reusable implementation belongs to ``aie1903.data`` (docs/roadmap.md, M1).

Reads public train/test/sample/membership files only and never writes into
``data/``. Results are summaries; no cross-dataset column mapping is stored.

Usage (from project root):
    python3 reports/audit/A-20261026-framework/audit_probe.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
OUT = Path(__file__).resolve().parent
TS_FORMAT = "%Y-%m-%d %H:%M:%S"
STEP = pd.Timedelta(minutes=5)
TRAIN_ROWS, TEST_ROWS, DAY = 1728, 289, 288

CONTRACT = {
    "cell_217": {
        "prefix": "Cell",
        "n": 217,
        "files": {
            "train": "cell_217_train.csv",
            "test": "cell_217_test.csv",
            "sample": "cell_217_sample_submission.csv",
            "description": "data_description_for_cell_217.pdf",
        },
        "train_start": "2024-11-30 23:00:00",
        "train_end": "2024-12-06 22:55:00",
        "test_start": "2024-12-06 23:00:00",
        "test_end": "2024-12-07 23:00:00",
        "min_value": 1,
    },
    "cell_30": {
        "prefix": "Cell",
        "n": 30,
        "files": {
            "train": "cell_30_train.csv",
            "test": "cell_30_test.csv",
            "sample": "cell_30_sample_submission.csv",
            "description": "data_description_for_cell_grid.pdf",
        },
        "train_start": "2024-11-30 23:50:00",
        "train_end": "2024-12-06 23:45:00",
        "test_start": "2024-12-06 23:50:00",
        "test_end": "2024-12-07 23:50:00",
        "min_value": 2088,
    },
    "grid_273": {
        "prefix": "Grid",
        "n": 273,
        "files": {
            "train": "grid_train.csv",
            "test": "grid_test.csv",
            "sample": "grid_sample_submission.csv",
            "description": "data_description_for_cell_grid.pdf",
            "membership": "grid_cell_membership.csv",
        },
        "train_start": "2024-11-30 23:50:00",
        "train_end": "2024-12-06 23:45:00",
        "test_start": "2024-12-06 23:50:00",
        "test_end": "2024-12-07 23:50:00",
        "min_value": 0,
    },
}


def jsonable(obj):
    """Convert to strict JSON: numpy scalars to Python, NaN/Inf to None."""
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        value = float(obj)
        return value if math.isfinite(value) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime(TS_FORMAT)
    return obj


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class Checks:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, name: str, ok: bool, detail=None, level_if_false: str = "FAIL") -> bool:
        self.items.append({"check": name, "status": "PASS" if ok else level_if_false, "detail": detail})
        return ok

    def info(self, name: str, detail) -> None:
        self.items.append({"check": name, "status": "INFO", "detail": detail})


def parse_timestamps(frame: pd.DataFrame, checks: Checks, label: str) -> pd.DatetimeIndex | None:
    try:
        ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], format=TS_FORMAT))
    except (ValueError, TypeError) as exc:
        checks.add(f"{label}.timestamp_format", False, str(exc))
        return None
    checks.add(f"{label}.timestamp_format", True, TS_FORMAT)
    checks.add(f"{label}.timestamp_tz_naive", ts.tz is None)
    checks.add(f"{label}.timestamp_unique", ts.is_unique)
    checks.add(f"{label}.timestamp_increasing", ts.is_monotonic_increasing)
    diffs = ts[1:] - ts[:-1]
    checks.add(f"{label}.timestamp_regular_5min", bool((diffs == STEP).all()), f"distinct_steps={sorted({str(d) for d in diffs})}")
    return ts


def audit_dataset(dataset_id: str, spec: dict) -> tuple[dict, dict]:
    checks = Checks()
    folder = RAW / dataset_id
    files = {}
    for role, name in spec["files"].items():
        path = folder / name
        exists = path.is_file()
        checks.add(f"file.{role}.exists", exists, str(path.relative_to(ROOT)))
        if exists:
            files[role] = {
                "name": name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "git_blob_sha1": git_blob_sha1(path),
            }
    extra = sorted(p.name for p in folder.iterdir() if p.name not in spec["files"].values()) if folder.is_dir() else []
    checks.add("folder.no_unexpected_files", not extra, extra, level_if_false="WARN")
    if not all(role in files for role in ("train", "test", "sample")):
        return {"files": files, "checks": checks.items}, {}

    expected_cols = ["timestamp"] + [f"{spec['prefix']}_{i:03d}" for i in range(1, spec["n"] + 1)]
    frames = {role: pd.read_csv(folder / spec["files"][role]) for role in ("train", "test", "sample")}
    stats: dict = {}
    for role, frame in frames.items():
        checks.add(f"{role}.columns_exact_order", list(frame.columns) == expected_cols,
                   f"n_columns={frame.shape[1]} expected={len(expected_cols)}")
    checks.add("train.rows", len(frames["train"]) == TRAIN_ROWS, len(frames["train"]))
    checks.add("test.rows", len(frames["test"]) == TEST_ROWS, len(frames["test"]))
    checks.add("sample.rows", len(frames["sample"]) == TEST_ROWS, len(frames["sample"]))

    ts = {role: parse_timestamps(frame, checks, role) for role, frame in frames.items()}
    if ts["train"] is not None and ts["test"] is not None:
        checks.add("train.start", ts["train"][0] == pd.Timestamp(spec["train_start"]), str(ts["train"][0]))
        checks.add("train.end", ts["train"][-1] == pd.Timestamp(spec["train_end"]), str(ts["train"][-1]))
        checks.add("test.start", ts["test"][0] == pd.Timestamp(spec["test_start"]), str(ts["test"][0]))
        checks.add("test.end", ts["test"][-1] == pd.Timestamp(spec["test_end"]), str(ts["test"][-1]))
        checks.add("train_test.contiguous", ts["test"][0] - ts["train"][-1] == STEP, str(ts["test"][0] - ts["train"][-1]))
    if ts["sample"] is not None and ts["test"] is not None:
        checks.add("sample.timestamps_equal_test", ts["sample"].equals(ts["test"]))

    value_cols = expected_cols[1:]
    train_vals = frames["train"][value_cols]
    numeric = all(pd.api.types.is_numeric_dtype(train_vals[c]) for c in value_cols)
    checks.add("train.values_numeric", numeric)
    v = train_vals.to_numpy(dtype=np.float64)
    n_nan = int(np.isnan(v).sum())
    finite = bool(np.isfinite(v).all())
    checks.add("train.values_no_nan", n_nan == 0, n_nan)
    checks.add("train.values_finite", finite)
    checks.add("train.values_integer", bool(np.equal(np.floor(v), v).all()))
    checks.add("train.values_non_negative", bool((v >= 0).all()))
    checks.add("train.values_min_contract", float(np.nanmin(v)) >= spec["min_value"],
               f"min={np.nanmin(v):.0f} contract_min={spec['min_value']}")
    zeros = int((v == 0).sum())
    if spec["prefix"] == "Cell":
        checks.add("train.no_zero_values_for_cells", zeros == 0, zeros)
    else:
        checks.info("train.zero_values_grid", {"count": zeros, "fraction": zeros / v.size})
    stats["train"] = {
        "shape": list(frames["train"].shape),
        "n_values": int(v.size),
        "min": float(np.nanmin(v)),
        "max": float(np.nanmax(v)),
        "median": float(np.nanmedian(v)),
        "mean": float(np.nanmean(v)),
        "zero_count": zeros,
        "count_ge_thresholds": {str(t): int((v >= t).sum()) for t in (1e4, 1e5, 3e5, 1e6)},
    }

    test_vals = frames["test"][value_cols]
    checks.add("test.values_all_empty", bool(test_vals.isna().all().all()),
               f"non_empty_cells={int(test_vals.notna().sum().sum())}")

    s = frames["sample"][value_cols].to_numpy(dtype=np.float64)
    checks.add("sample.values_finite", bool(np.isfinite(s).all()))
    checks.add("sample.values_non_negative", bool((s >= 0).all()))
    cyclic = v[TRAIN_ROWS - DAY + (np.arange(TEST_ROWS) % DAY)]
    eq_rows = np.all(np.isclose(s, cyclic, rtol=0.0, atol=1e-6), axis=1)
    last_row_matches = np.where(np.all(np.isclose(v, s[-1], rtol=0.0, atol=1e-6), axis=1))[0].tolist()
    absent = sum(
        1 for j in range(v.shape[1]) if not np.isclose(v[:, j], s[-1, j], rtol=0.0, atol=1e-6).any()
    )

    def median_rel_pct(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.median(np.abs(a - b) / np.maximum(np.abs(b), 1.0)) * 100)

    stats["sample_vs_seasonal_naive"] = {
        "definition": "cyclic[h] = train[1728 - 288 + (h % 288)], h = 0..288",
        "rows_0_287_equal": bool(eq_rows[:DAY].all()),
        "row_288_equal_cyclic": bool(eq_rows[DAY]),
        "train_row_indices_equal_to_sample_row_288": last_row_matches,
        "row_288_columns_whose_value_never_occurs_in_train_column": absent,
        "row_288_median_rel_diff_pct_vs_train_1727": median_rel_pct(s[-1], v[TRAIN_ROWS - 1]),
        "row_288_median_rel_diff_pct_vs_train_1440": median_rel_pct(s[-1], v[TRAIN_ROWS - DAY]),
        "train_typical_adjacent_step_rel_change_pct": median_rel_pct(v[1:], v[:-1]),
    }
    checks.info("sample.is_seasonal_naive_reference_not_labels", stats["sample_vs_seasonal_naive"])

    if "membership" in files:
        m = pd.read_csv(folder / spec["files"]["membership"])
        checks.add("membership.columns", list(m.columns) == ["grid_id", "cell_id", "grid_index_within_cell"], list(m.columns))
        checks.add("membership.rows", len(m) == spec["n"], len(m))
        checks.add("membership.grid_ids_match_train_columns", sorted(m["grid_id"]) == sorted(value_cols))
        checks.add("membership.grid_id_unique", m["grid_id"].is_unique)
        sizes = m.groupby("cell_id").size()
        dist = {str(k): int(c) for k, c in sizes.value_counts().sort_index().items()}
        checks.add("membership.parent_size_distribution", dist == {"1": 3, "10": 27}, dist)
        checks.add("membership.parent_ids_within_cell_30",
                   set(m["cell_id"]).issubset({f"Cell_{i:03d}" for i in range(1, 31)}),
                   f"n_parents={m['cell_id'].nunique()}")
    return {"files": files, "checks": checks.items, "stats": stats}, {"train_ts": ts["train"], "train_vals": v}


def cross_dataset(loaded: dict) -> dict:
    """Quantify the time overlap that makes cell_30/grid_273 data a leak for cell_217."""
    out: dict = {}
    if "cell_217" not in loaded:
        return out
    test_start = pd.Timestamp(CONTRACT["cell_217"]["test_start"])
    test_end = pd.Timestamp(CONTRACT["cell_217"]["test_end"])
    for other in ("cell_30", "grid_273"):
        if other not in loaded:
            continue
        ts = loaded[other]["train_ts"]
        inside = ts[(ts >= test_start) & (ts <= test_end)]
        out[f"{other}_train_rows_inside_cell_217_test_window"] = {
            "count": len(inside),
            "first": str(inside[0]) if len(inside) else None,
            "last": str(inside[-1]) if len(inside) else None,
        }
    if "cell_30" in loaded:
        a = loaded["cell_217"]["train_vals"]
        b = loaded["cell_30"]["train_vals"]

        def matched_columns(offset: int) -> int:
            """Columns j of cell_30 with a cell_217 column equal (>99% of rows) to b[i] vs a[i + offset]."""
            lo, hi = max(0, -offset), min(len(b), len(a) - offset)
            aa, bb = a[lo + offset : hi + offset], b[lo:hi]
            count = 0
            for j in range(bb.shape[1]):
                rel = np.abs(aa - bb[:, [j]]) / np.maximum(np.abs(bb[:, [j]]), 1.0)
                if np.any(np.mean(rel <= 1e-6, axis=0) > 0.99):
                    count += 1
            return count

        out["cell_30_vs_cell_217_value_alignment"] = {
            "same_row_index_offset_0_matched_columns": matched_columns(0),
            "same_clock_label_offset_10_matched_columns": matched_columns(10),
            "of": b.shape[1],
            "interpretation": "matches at equal row index, not at equal clock label: same measurements, "
            "cell_30 timestamps labelled 50 min later than cell_217",
            "note": "counts only; mapping deliberately not stored (cross-dataset use is forbidden)",
        }
    return out


def run(cmd: list[str]) -> str | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def environment() -> dict:
    versions = {}
    for mod in ("numpy", "pandas", "scipy", "matplotlib", "yaml", "torch", "sklearn", "statsmodels", "pytest", "ruff"):
        try:
            versions[mod] = getattr(__import__(mod), "__version__", "unknown")
        except ImportError:
            versions[mod] = None
    cuda = None
    if versions.get("torch"):
        import torch

        cuda = {"available": torch.cuda.is_available(), "torch_cuda": torch.version.cuda}
    cpu_max = Path("/sys/fs/cgroup/cpu.max")
    mem_max = Path("/sys/fs/cgroup/memory.max")
    quota = None
    if cpu_max.is_file():
        q, period = cpu_max.read_text().split()
        quota = None if q == "max" else int(q) / int(period)
    mem = mem_max.read_text().strip() if mem_max.is_file() else None
    disk = shutil.disk_usage(ROOT)
    return {
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "hostname": platform.node(),
        "os": run(["sh", "-c", ". /etc/os-release && echo $PRETTY_NAME"]),
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "packages": versions,
        "torch_cuda": cuda,
        "cpu": {"os_cpu_count": os.cpu_count(), "cgroup_cpu_quota_cores": quota},
        "memory_limit_bytes": None if mem in (None, "max") else int(mem),
        "gpu": run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "project_disk": {"path": str(ROOT), "total_bytes": disk.total, "free_bytes": disk.free},
        "git": {
            "branch": run(["git", "-C", str(ROOT), "branch", "--show-current"]),
            "head": run(["git", "-C", str(ROOT), "rev-parse", "HEAD"]),
            "dirty": bool(run(["git", "-C", str(ROOT), "status", "--porcelain"])),
        },
    }


def main() -> int:
    report = {
        "audit_id": "A-20261026-framework",
        "task_id": "T-20261026-01",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "official_source": {
            "repository": "https://github.com/AIE1903-DataCompetition-26AY/competition-data",
            "commit": "49822d82552c980bb83eb445548268f3565882ef",
        },
        "datasets": {},
    }
    loaded = {}
    for dataset_id, spec in CONTRACT.items():
        result, arrays = audit_dataset(dataset_id, spec)
        report["datasets"][dataset_id] = result
        if arrays:
            loaded[dataset_id] = arrays
    report["cross_dataset"] = cross_dataset(loaded)
    statuses = [c["status"] for d in report["datasets"].values() for c in d["checks"]]
    report["summary"] = {s: statuses.count(s) for s in ("PASS", "FAIL", "WARN", "INFO")}

    (OUT / "data-audit.json").write_text(json.dumps(jsonable(report), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "environment.json").write_text(json.dumps(jsonable(environment()), indent=2, allow_nan=False) + "\n", encoding="utf-8")

    for dataset_id, result in report["datasets"].items():
        bad = [c for c in result["checks"] if c["status"] in ("FAIL", "WARN")]
        print(f"{dataset_id}: {len(result['checks'])} checks, problems={bad if bad else 'none'}")
    print("cross_dataset:", json.dumps(jsonable(report["cross_dataset"]), indent=1))
    print("summary:", report["summary"])
    return 1 if report["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
