"""Seasonal-naive daily-cycle baseline (288-step day, 289-step forecast)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .data import value_columns


DAY_CYCLE = 288
HORIZON = 289


def seasonal_naive_predict(
    train: pd.DataFrame,
    test_timestamps: pd.Series | pd.DatetimeIndex | None = None,
    horizon: int = HORIZON,
    day_cycle: int = DAY_CYCLE,
) -> pd.DataFrame:
    """Predict `horizon` steps using last full day in train (TOD via h % day_cycle).

    For horizon h in 0..horizon-1, use train values at index -(day_cycle) + (h % day_cycle)
    relative to end of train (i.e. last `day_cycle` rows, wrapped).
    """
    cols = value_columns(train)
    values = train[cols].to_numpy(dtype=np.float64)
    if values.shape[0] < day_cycle:
        raise ValueError(f"train has {values.shape[0]} rows; need >= {day_cycle}")
    last_day = values[-day_cycle:]
    idx = np.arange(horizon) % day_cycle
    pred = last_day[idx]

    if test_timestamps is None:
        # synthesize from last train timestamp + 5 minutes
        last_ts = pd.Timestamp(train["timestamp"].iloc[-1])
        stamps = pd.date_range(last_ts + pd.Timedelta(minutes=5), periods=horizon, freq="5min")
    else:
        stamps = pd.to_datetime(pd.Series(test_timestamps)).iloc[:horizon]
        if len(stamps) != horizon:
            # allow shorter for truncated backtest folds
            pred = pred[: len(stamps)]
    out = pd.DataFrame(pred, columns=cols)
    out.insert(0, "timestamp", stamps.to_numpy())
    return out
