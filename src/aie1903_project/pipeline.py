"""Shared configuration and run-context helpers."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    if not isinstance(config, dict):
        raise ValueError("The top level of a configuration must be a mapping.")
    return config


@dataclass(frozen=True)
class RunContext:
    """Small immutable record passed between pipeline stages."""

    config_path: Path
    config: dict[str, Any]

    @classmethod
    def from_file(cls, path: str | Path) -> "RunContext":
        """Create a context from a YAML file."""
        source = Path(path).resolve()
        return cls(config_path=source, config=load_config(source))
