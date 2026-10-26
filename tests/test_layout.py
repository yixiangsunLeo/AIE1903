"""Framework smoke test: every functional area exists, is documented, and is registered."""

import importlib
import re
import tomllib
from pathlib import Path

import pytest

import aie1903

ROOT = Path(__file__).resolve().parents[1]
AREAS = (
    "config",
    "data",
    "splits",
    "features",
    "models",
    "evaluation",
    "tracking",
    "pipelines",
    "viz",
)


@pytest.mark.parametrize("area", AREAS)
def test_area_is_importable_and_documented(area: str) -> None:
    module = importlib.import_module(f"aie1903.{area}")
    assert module.__doc__ and "Status:" in module.__doc__


@pytest.mark.parametrize("area", AREAS)
def test_area_has_contract_section(area: str) -> None:
    text = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    assert re.search(rf"^### 4\.\d+ {area}\b", text, flags=re.MULTILINE)


def test_version_matches_pyproject() -> None:
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert aie1903.__version__ == meta["project"]["version"]
