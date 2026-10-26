#!/usr/bin/env python3
"""Generate seasonal-naive submission under runs/."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aie1903.predict import main as predict_main  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="cell_217", choices=["cell_217", "cell_30"])
    args, rest = p.parse_known_args()
    predict_main(["--dataset", args.dataset, *rest])


if __name__ == "__main__":
    main()
