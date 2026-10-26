"""Training entry — baseline seasonal-naive currently; extend with models later."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aie1903_project.predict import main as predict_main


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    p.add_argument("--dataset", default="cell_217", choices=["cell_217", "cell_30"])
    args = p.parse_args()
    print(f"config={args.config} (baseline train == write seasonal-naive submission)")
    predict_main(["--dataset", args.dataset])


if __name__ == "__main__":
    main()
