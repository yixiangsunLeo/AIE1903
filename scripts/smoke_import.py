#!/usr/bin/env python3
"""Import-check all AIE1903 modules."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def main() -> None:
    t0 = time.time()
    import aie1903
    from aie1903 import baseline, backtest, data, metrics, predict  # noqa: F401
    print(f"OK aie1903={aie1903.__version__} root={data.project_root()}")
    print(f"elapsed_s={time.time()-t0:.3f}")

if __name__ == "__main__":
    main()
