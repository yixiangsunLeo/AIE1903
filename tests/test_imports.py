"""Smoke tests for the reusable project package."""


def test_core_modules_import() -> None:
    from aie1903_project import data
    from aie1903_project import evaluation
    from aie1903_project import features
    from aie1903_project import models
    from aie1903_project import paths
    from aie1903_project import pipeline
    from aie1903_project import visualization

    assert all(
        module is not None
        for module in (data, evaluation, features, models, paths, pipeline, visualization)
    )
