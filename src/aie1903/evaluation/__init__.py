"""Evaluation area: official metrics and submission validation.

Responsibility:
    Compute MAE, RMSE, MAPE and two masked MAPEs on the raw count scale with
    per-track rules (cell: thresholds 3e5/1e6; grid: MAPE on y > 0, thresholds
    1e4/1e5), report counts, and validate submission files against test templates.

Allowed internal imports: config, data (contract and types). Never models.

Invariants (metric definition provisional-v1, ADR-0003):
    - Masks depend on ground truth only; averages pool all retained entries.
    - Empty mask -> value None and count 0; no epsilon is added.
    - Submission checks separate invalid (missing, non-numeric, wrong rows or
      columns) from warnings (negative values).

Status: not implemented (roadmap M2/M6). Contract: docs/architecture.md section 4.6.
"""
