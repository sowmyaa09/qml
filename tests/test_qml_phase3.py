"""Phase 3 helpers: scaling, split alignment, no assumed quantum win."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data_loader import load_breast_cancer_dataset
from src.feature_selection import DEFAULT_K, fit_select_k_best, transform_features
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.qml_models import (
    build_rbf_svm_pipeline,
    recording_cobyla,
    scale_to_unit_interval,
)
from src.train_qml import _verdict


def test_scale_to_unit_interval_fits_train_only() -> None:
    x_train = pd.DataFrame({"a": [0.0, 10.0], "b": [2.0, 4.0]})
    x_test = pd.DataFrame({"a": [5.0, 20.0], "b": [3.0, 0.0]})
    scaler, train_s, test_s = scale_to_unit_interval(x_train, x_test)
    assert train_s.min() == 0.0
    assert train_s.max() == 1.0
    # Test 20 is outside train max 10 → clipped by MinMaxScaler to > 1.
    assert test_s[0, 0] == 0.5
    assert test_s[1, 0] > 1.0
    assert list(scaler.data_min_) == [0.0, 2.0]


def test_phase3_uses_same_split_seed_as_phase1() -> None:
    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features, data.target
    )
    assert RANDOM_STATE == 42
    assert len(x_train) + len(x_test) == data.n_samples
    selector = fit_select_k_best(x_train, y_train, k=DEFAULT_K)
    reduced = transform_features(selector, x_train)
    assert reduced.shape[1] == DEFAULT_K


def test_rbf_svm_pipeline_predicts_proba() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(40, 4))
    y = (x[:, 0] > 0).astype(int)
    model = build_rbf_svm_pipeline()
    model.fit(x, y)
    scores = model.decision_function(x[:5])
    assert scores.shape == (5,)


def test_verdict_does_not_assume_quantum_win() -> None:
    metrics = {
        "Logistic Regression": {"f1": 0.95},
        "Random Forest": {"f1": 0.90},
        "RBF SVM": {"f1": 0.94},
        "VQC": {"f1": 0.80},
        "QSVC": {"f1": 0.92},
        "QNN": {"f1": 0.70},
    }
    text = _verdict(metrics)
    assert "did not beat" in text


def test_recording_cobyla_captures_every_objective_value() -> None:
    history: list[float] = []
    minimizer = recording_cobyla(12, history)

    def objective(params):
        return float(np.sum((np.asarray(params) - 0.3) ** 2))

    result = minimizer(objective, np.array([1.0, -1.0]))
    assert len(history) > 1
    assert result.fun <= history[0]
    assert result.x.shape == (2,)
