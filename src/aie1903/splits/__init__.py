"""Splits area: validation protocol, folds, forecast origins, time-boundary guards.

Responsibility:
    Load configs/validation-plan.json (expanding_289_v1), yield folds, and provide
    guards that reject supervised targets or feature sources beyond the boundary.

Allowed internal imports: config (data types only from data).

Invariants:
    - Zero-based, half-open index ranges; every forecast window has 289 steps.
    - The heldout fold is excluded unless explicitly requested and recorded.
    - Every supervised target index < fit_end; every feature source index < origin.

Status: not implemented (roadmap M3). Contract: docs/architecture.md section 4.3.
"""
