"""Evaluation entry — runs validation-plan backtest."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aie1903_project.backtest import main


if __name__ == "__main__":
    main()
