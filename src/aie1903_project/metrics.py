"""Official AIE1903 metrics (lower is better)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _to_1d(y: Any) -> np.ndarray:
    if isinstance(y, pd.DataFrame):
        cols = [c for c in y.columns if c != "timestamp"]
        arr = y[cols].to_numpy(dtype=np.float64)
    else:
        arr = np.asarray(y, dtype=np.float64)
    return arr.reshape(-1)


def mae(y_true: Any, y_pred: Any) -> float:
    yt, yp = _to_1d(y_true), _to_1d(y_pred)
    if yt.shape != yp.shape:
        raise ValueError(f"shape mismatch {yt.shape} vs {yp.shape}")
    return float(np.mean(np.abs(yp - yt)))


def rmse(y_true: Any, y_pred: Any) -> float:
    yt, yp = _to_1d(y_true), _to_1d(y_pred)
    if yt.shape != yp.shape:
        raise ValueError(f"shape mismatch {yt.shape} vs {yp.shape}")
    return float(np.sqrt(np.mean((yp - yt) ** 2)))


def mape(y_true: Any, y_pred: Any) -> float:
    yt, yp = _to_1d(y_true), _to_1d(y_pred)
    if yt.shape != yp.shape:
        raise ValueError(f"shape mismatch {yt.shape} vs {yp.shape}")
    # competition: yi >= 1 in released data; still guard zeros
    denom = np.where(yt == 0, np.nan, yt)
    return float(100.0 * np.nanmean(np.abs(yp - yt) / denom))


def masked_mape(y_true: Any, y_pred: Any, threshold: float) -> float:
    yt, yp = _to_1d(y_true), _to_1d(y_pred)
    if yt.shape != yp.shape:
        raise ValueError(f"shape mismatch {yt.shape} vs {yp.shape}")
    mask = yt >= threshold
    if not np.any(mask):
        return float("nan")
    yt_m, yp_m = yt[mask], yp[mask]
    return float(100.0 * np.mean(np.abs(yp_m - yt_m) / yt_m))


def evaluate_all(y_true: Any, y_pred: Any) -> dict[str, float]:
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mape": mape(y_true, y_pred),
        "masked_mape_3e5": masked_mape(y_true, y_pred, 3e5),
        "masked_mape_1e6": masked_mape(y_true, y_pred, 1e6),
    }
