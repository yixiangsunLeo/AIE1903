#!/usr/bin/env python3
"""Import-check canonical aie1903_project package."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def main() -> None:
    t0 = time.time()
    import aie1903_project
    from aie1903_project import baseline, backtest, data, metrics, predict  # noqa: F401
    print(f"OK aie1903_project={aie1903_project.__version__} root={data.project_root()}")
    print(f"elapsed_s={time.time()-t0:.3f}")

if __name__ == "__main__":
    main()
