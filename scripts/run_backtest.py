#!/usr/bin/env python3
"""Run validation-plan backtest and write reports/backtest_metrics.json."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aie1903_project.backtest import main  # noqa: E402

if __name__ == "__main__":
    main()
