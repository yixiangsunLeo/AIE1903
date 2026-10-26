"""Models area: forecaster interface, registry, baselines and model families.

Responsibility:
    Define the Forecaster protocol (fit(history, context) -> self;
    predict(horizon) -> array[horizon, n_series] on the raw scale), a registry,
    the seasonal-naive baseline (pred[h] = history[-288 + h % 288]) and later models.

Allowed internal imports: config, data (types), features. Never evaluation.

Invariants:
    - predict() receives only the number of steps, never future values.
    - Outputs are finite and on the raw count scale; any clipping is configured.
    - Randomness comes only from the seed in the fit context.

Status: not implemented (roadmap M5). Contract: docs/architecture.md section 4.5.
"""
