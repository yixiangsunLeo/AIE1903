"""Configuration area.

Responsibility:
    Load configs/*.yaml|json, validate required keys, resolve paths against the
    discovered project root, and compute canonical config hashes for run records.

Allowed internal imports: none.

Invariants:
    - No hard-coded absolute paths. The project root is the nearest ancestor that
      contains both AGENTS.md and pyproject.toml; AIE1903_PROJECT_ROOT,
      AIE1903_DATA_ROOT and AIE1903_RUNS_ROOT may override it and are recorded.
    - A resolved config is immutable and serialisable to strict JSON.

Status: not implemented (roadmap M1). Contract: docs/architecture.md section 4.1.
"""
