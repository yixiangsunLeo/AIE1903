"""Task-neutral model interfaces."""

from typing import Any, Protocol

import numpy as np


class Estimator(Protocol):
    """Minimal interface expected by project pipelines."""

    def fit(self, features: Any, targets: Any) -> "Estimator":
        """Fit the estimator and return itself."""

    def predict(self, features: Any) -> np.ndarray:
        """Return predictions for the supplied features."""


def build_model(config: dict[str, Any]) -> Estimator:
    """Construct the selected model after the final task has been defined."""
    raise NotImplementedError(
        "Select the final project task and implement its model factory first."
    )
