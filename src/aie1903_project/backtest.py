"""Chronological backtest using configs/validation-plan.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .baseline import seasonal_naive_predict
from .data import load_dataset, project_root, value_columns
from .metrics import evaluate_all


def load_plan(path: Path | None = None) -> dict[str, Any]:
    path = path or (project_root() / "configs" / "validation-plan.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_backtest(
    dataset: str | None = None,
    plan_path: Path | None = None,
) -> dict[str, Any]:
    plan = load_plan(plan_path)
    dataset = dataset or plan.get("primary_dataset", "cell_217")
    data = load_dataset(dataset)  # type: ignore[arg-type]
    train = data["train"]
    cols = value_columns(train)
    fold_results = []
    for fold in plan.get("folds", []):
        h_end = int(fold["history_end"])
        s = int(fold["holdout_start"])
        e = int(fold["holdout_end"])
        history = train.iloc[:h_end].copy()
        holdout = train.iloc[s:e].copy()
        horizon = len(holdout)
        if horizon == 0:
            continue
        pred = seasonal_naive_predict(
            history,
            test_timestamps=holdout["timestamp"],
            horizon=horizon,
            day_cycle=int(plan.get("day_cycle", 288)),
        )
        # align columns
        y_true = holdout[cols]
        y_pred = pred[cols]
        metrics = evaluate_all(y_true, y_pred)
        fold_results.append(
            {
                "id": fold.get("id"),
                "history_end": h_end,
                "holdout_start": s,
                "holdout_end": e,
                "horizon": horizon,
                "metrics": metrics,
            }
        )
    return {
        "dataset": dataset,
        "baseline": plan.get("baseline"),
        "folds": fold_results,
    }


def main(argv: list[str] | None = None) -> None:
    import argparse

    p = argparse.ArgumentParser(description="AIE1903 backtest")
    p.add_argument("--dataset", default=None)
    p.add_argument("--plan", type=Path, default=None)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)
    result = run_backtest(dataset=args.dataset, plan_path=args.plan)
    text = json.dumps(result, indent=2)
    print(text)
    out = args.out or (project_root() / "reports" / "backtest_metrics.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
