"""Shared figure output helpers."""

from pathlib import Path
from typing import Any


def save_figure(figure: Any, path: str | Path, *, dpi: int = 160) -> Path:
    """Save a Matplotlib-compatible figure with consistent defaults."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=dpi, bbox_inches="tight")
    return target
