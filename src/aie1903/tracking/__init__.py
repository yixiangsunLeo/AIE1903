"""Tracking area: run ids, run metadata, artifact hashing, experiment index.

Responsibility:
    Create runs/<run_id>/run.json at start (status=running) and finalise it at the
    end; snapshot config, environment and data hashes; hash artifacts; append
    reports/experiments.csv; verify that records and artifacts are consistent.

Allowed internal imports: config.

Invariants:
    - Strict JSON only: null for unknown or not applicable, never NaN or zero.
    - Failures, cancellations and timeouts are recorded and never marked succeeded.
    - Uncommitted code sets git_dirty=true and stores the diff hash.

Status: not implemented (roadmap M4/M7). Contract: docs/architecture.md section 4.7;
record fields: docs/standards/records.md and docs/templates/run-record.json.
"""
