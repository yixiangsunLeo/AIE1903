"""Generic tabular data input and output helpers."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd


def load_table(
    path: str | Path,
    *,
    parse_dates: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Load a CSV or Parquet table based on its file extension."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Data file does not exist: {source}")
    if source.suffix.lower() == ".csv":
        return pd.read_csv(source, parse_dates=list(parse_dates or []))
    if source.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(source)
    raise ValueError(f"Unsupported table format: {source.suffix}")


def save_table(frame: pd.DataFrame, path: str | Path) -> Path:
    """Save a table and create its parent directory when needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".csv":
        frame.to_csv(target, index=False)
    elif target.suffix.lower() in {".parquet", ".pq"}:
        frame.to_parquet(target, index=False)
    else:
        raise ValueError(f"Unsupported table format: {target.suffix}")
    return target
