"""Pipelines area: orchestration of backtest and final prediction.

Responsibility:
    backtest: for each fold, slice history -> fit -> predict 289 -> score -> record.
    predict: fit on all 1728 rows -> predict 289 -> write the submission from the
    test template -> validate it -> record.

Allowed internal imports: all areas except cli.

Invariants:
    - Development folds only by default; heldout requires an explicit, recorded flag.
    - Every entry point runs inside tracking.start_run.

Status: not implemented (roadmap M5/M6). Contract: docs/architecture.md section 4.8.
"""
