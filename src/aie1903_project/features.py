"""Reusable, task-neutral feature transformations."""

import pandas as pd


def add_calendar_features(
    frame: pd.DataFrame,
    timestamp_column: str,
) -> pd.DataFrame:
    """Add common calendar features without mutating the input frame."""
    if timestamp_column not in frame.columns:
        raise KeyError(f"Missing timestamp column: {timestamp_column}")

    result = frame.copy()
    timestamps = pd.to_datetime(result[timestamp_column], errors="raise")
    result["year"] = timestamps.dt.year
    result["month"] = timestamps.dt.month
    result["day"] = timestamps.dt.day
    result["day_of_week"] = timestamps.dt.dayofweek
    result["hour"] = timestamps.dt.hour
    result["minute"] = timestamps.dt.minute
    return result
