#!/usr/bin/env python3
"""Audit raw datasets: shape, nulls, mins, timestamp span."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aie1903.data import load_dataset, value_columns  # noqa: E402


def audit_one(name: str) -> None:
    ds = load_dataset(name)  # type: ignore[arg-type]
    for split, df in ds.items():
        cols = value_columns(df)
        vals = df[cols]
        print(f"[{name}/{split}] shape={df.shape} ts={df['timestamp'].iloc[0]} → {df['timestamp'].iloc[-1]}")
        if split == "test":
            nulls = vals.isna().sum().sum()
            print(f"  empty_cells={nulls} (expected for test)")
        else:
            print(
                f"  nulls={vals.isna().sum().sum()} min={vals.min().min()} max={vals.max().max()} "
                f"zeros={(vals == 0).sum().sum()}"
            )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", action="append", default=None)
    args = p.parse_args()
    names = args.dataset or ["cell_217", "cell_30"]
    for n in names:
        try:
            audit_one(n)
        except FileNotFoundError as e:
            print(f"SKIP {n}: {e}")


if __name__ == "__main__":
    main()
