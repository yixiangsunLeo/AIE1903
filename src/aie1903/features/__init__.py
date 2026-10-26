"""Features area: origin-aware feature construction and fold-fitted transforms.

Responsibility:
    Build calendar, lag, rolling and cross-series features relative to a forecast
    origin, and provide transforms (scaling, log1p, ...) that are fitted on the
    fold's training segment and invert predictions back to the raw count scale.

Allowed internal imports: config, data (types), splits.

Invariants:
    - Each feature declares its source offsets; all sources precede the origin.
    - Lag 288 for step 289 lies inside the forecast window and is rejected.
    - Statistics come from the fold's training segment only, never from heldout/test.

Status: not implemented (roadmap M3/M5). Contract: docs/architecture.md section 4.4.
"""
