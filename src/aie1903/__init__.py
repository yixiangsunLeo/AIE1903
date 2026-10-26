"""AIE1903 wireless uplink traffic forecasting (mainline dataset: cell_217).

Functional areas; contracts, interfaces and allowed imports live in docs/architecture.md:

    config      configuration loading, validation, path resolution, hashing
    data        dataset registry, official-file IO, data-contract checks, audit, fetch
    splits      validation protocol, folds, forecast origins, time-boundary guards
    features    origin-aware feature construction; transforms fitted on fold training only
    models      forecaster interface, registry, baselines and models
    evaluation  official metrics and submission validation on the raw count scale
    tracking    run ids, run metadata, artifact hashing, experiment index, record checks
    pipelines   orchestration of backtest and final prediction
    viz         standard figures built from recorded artifacts

Status: framework only (v0.2.1). No area is implemented yet; see docs/roadmap.md.
"""

__version__ = "0.2.1"
