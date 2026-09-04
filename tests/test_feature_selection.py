"""Phase 2 selector must be fit on train rows only and keep k columns."""

from __future__ import annotations

import numpy as np

from src.data_loader import load_breast_cancer_dataset
from src.feature_selection import (
    DEFAULT_K,
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import stratified_train_test_split


def test_select_k_best_keeps_six_named_columns() -> None:
    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, _y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    selector = fit_select_k_best(x_train, y_train, k=DEFAULT_K)
    names = selected_feature_names(selector, list(x_train.columns))
    assert len(names) == DEFAULT_K
    assert len(set(names)) == DEFAULT_K
    reduced_test = transform_features(selector, x_test)
    assert list(reduced_test.columns) == names
    assert reduced_test.shape == (len(x_test), DEFAULT_K)


def test_selector_does_not_require_test_labels() -> None:
    """Fitting uses y_train only; transforming test must not need y_test."""
    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, _y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    selector = fit_select_k_best(x_train, y_train, k=4)
    # Mutual-info scores are finite and length 30.
    assert selector.scores_ is not None
    assert len(selector.scores_) == 30
    assert np.all(np.isfinite(selector.scores_))
    out = selector.transform(x_test)
    assert out.shape[1] == 4
