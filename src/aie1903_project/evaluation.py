"""Small, task-neutral regression metrics."""

import numpy as np
from numpy.typing import ArrayLike


def _paired_arrays(actual: ArrayLike, predicted: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    truth = np.asarray(actual, dtype=float)
    estimate = np.asarray(predicted, dtype=float)
    if truth.shape != estimate.shape:
        raise ValueError(f"Shape mismatch: {truth.shape} != {estimate.shape}")
    if truth.size == 0:
        raise ValueError("Metrics require at least one observation.")
    if not np.isfinite(truth).all() or not np.isfinite(estimate).all():
        raise ValueError("Metrics require finite values.")
    return truth, estimate


def mean_absolute_error(actual: ArrayLike, predicted: ArrayLike) -> float:
    """Return mean absolute error."""
    truth, estimate = _paired_arrays(actual, predicted)
    return float(np.mean(np.abs(truth - estimate)))


def root_mean_squared_error(actual: ArrayLike, predicted: ArrayLike) -> float:
    """Return root mean squared error."""
    truth, estimate = _paired_arrays(actual, predicted)
    return float(np.sqrt(np.mean(np.square(truth - estimate))))
