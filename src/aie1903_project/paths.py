"""Project-relative path definitions."""

from dataclasses import dataclass
from pathlib import Path


def project_root() -> Path:
    """Return the repository root, independent of the current working directory."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    """Canonical locations used by project code."""

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
        """Build all paths from a project root."""
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
