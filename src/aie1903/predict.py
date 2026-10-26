"""CLI: write seasonal-naive (or future models) submission CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from .baseline import seasonal_naive_predict
from .data import load_dataset, project_root


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="AIE1903 predict / submission writer")
    p.add_argument("--dataset", default="cell_217", choices=["cell_217", "cell_30"])
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)
    data = load_dataset(args.dataset)  # type: ignore[arg-type]
    test = data["test"]
    pred = seasonal_naive_predict(data["train"], test_timestamps=test["timestamp"], horizon=len(test))
    out = args.out or (project_root() / "runs" / f"{args.dataset}_seasonal_naive_submission.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pred.to_csv(out, index=False)
    print(f"wrote {out} shape={pred.shape}")


if __name__ == "__main__":
    main()
