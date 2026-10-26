"""Viz area: standard figures built from recorded artifacts.

Responsibility:
    Series overview, daily-cycle overlay, forecast-vs-actual per fold, and error by
    horizon step and time of day, saved under runs/<run_id>/figures/.

Allowed internal imports: config, data (types), evaluation (result types).

Invariants:
    - Figures are derived from recorded run artifacts only.
    - Axes are labelled as anonymised raw counts; no physical units or locations.

Status: not implemented (roadmap M8). Contract: docs/architecture.md section 4.9.
"""
