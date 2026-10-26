"""Data loading helpers for cell_217 / cell_30 wide tables."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

DatasetName = Literal["cell_217", "cell_30"]


def project_root() -> Path:
    """Return /ai/workspace/AIE1903 when present, else repo root inferred from this file."""
    sun = Path("/ai/workspace/AIE1903")
    if sun.is_dir():
        return sun
    # src/aie1903/data.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def raw_dir(dataset: DatasetName = "cell_217", root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "data" / "raw" / dataset


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise ValueError(f"missing timestamp column in {path}")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_dataset(
    dataset: DatasetName = "cell_217",
    root: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Load train / test / sample_submission for a dataset folder."""
    d = raw_dir(dataset, root)
    prefix = dataset  # cell_217 / cell_30
    paths = {
        "train": d / f"{prefix}_train.csv",
        "test": d / f"{prefix}_test.csv",
        "sample": d / f"{prefix}_sample_submission.csv",
    }
    missing = [k for k, p in paths.items() if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"{dataset} missing files {missing} under {d}")
    out = {k: load_csv(p) for k, p in paths.items()}
    return out


def value_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "timestamp"]


def values_matrix(df: pd.DataFrame):
    import numpy as np

    cols = value_columns(df)
    return df[cols].to_numpy(dtype=np.float64), cols
