"""Project-relative path definitions."""

from dataclasses import dataclass
from pathlib import Path


def project_root() -> Path:
    """Prefer /ai/workspace/AIE1903 on school disk; else repo root from this file."""
    sun = Path("/ai/workspace/AIE1903")
    if sun.is_dir():
        return sun
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    raw_data: Path
    interim_data: Path
    processed_data: Path
    models: Path
    outputs: Path
    figures: Path
    tables: Path

    @classmethod
    def from_root(cls, root: Path | None = None) -> "ProjectPaths":
        base = (root or project_root()).resolve()
        return cls(
            root=base,
            raw_data=base / "data" / "raw",
            interim_data=base / "data" / "interim",
            processed_data=base / "data" / "processed",
            models=base / "artifacts" / "models",
            outputs=base / "artifacts" / "outputs",
            figures=base / "reports" / "figures",
            tables=base / "reports" / "tables",
        )


PATHS = ProjectPaths.from_root()
