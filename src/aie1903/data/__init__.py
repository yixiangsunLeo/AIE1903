"""Data area: dataset registry, official-file IO, data contract, audit, fetch.

Responsibility:
    Read the official files of exactly one dataset (configs/datasets.yaml), validate
    them against the data contract, verify data/checksums.sha256, produce audit
    reports, and fetch missing official files from the pinned upstream commit.

Allowed internal imports: config.

Invariants:
    - data/raw/ is read-only; files are verified, never repaired or overwritten.
    - Timestamps stay naive in the recorded collection clock; no timezone conversion.
    - One dataset per call; there is no cross-dataset alignment or merge (ADR-0005).
    - Test files are templates (timestamps + columns) only; sample-submission values
      are never read.

Status: not implemented (roadmap M1). Contract: docs/architecture.md section 4.2.
"""
