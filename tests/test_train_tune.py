"""Train-only clipping and cardio row repair."""

from __future__ import annotations

import pandas as pd

from src.tabular_datasets import CATALOG, _repair_source_errors
from src.train_tune import clip_numeric_by_train_quantiles, should_grid_search


def test_clip_uses_train_quantiles_only() -> None:
    x_train = pd.DataFrame({"a": list(range(100)), "flag": [0, 1] * 50})
    x_test = pd.DataFrame({"a": [500.0, 10.0], "flag": [0, 1]})
    train_c, test_c = clip_numeric_by_train_quantiles(x_train, x_test)
    assert float(train_c["a"].max()) <= 99.0 + 1e-6
    assert float(test_c["a"].iloc[0]) <= float(train_c["a"].max()) + 1e-6
    assert list(train_c["flag"]) == list(x_train["flag"])


def test_should_not_grid_search_huge_tables() -> None:
    assert should_grid_search(400, 10) is True
    assert should_grid_search(70_000, 11) is False


def test_cardio_repair_drops_impossible_bp() -> None:
    spec = CATALOG["cardio"]
    frame = pd.DataFrame(
        {
            "ap_hi": [120, 900, 80],
            "ap_lo": [80, 80, 90],
            "height": [170, 170, 170],
            "weight": [70, 70, 70],
        }
    )
    out = _repair_source_errors(frame, spec)
    assert len(out) == 1
    assert int(out["ap_hi"].iloc[0]) == 120
