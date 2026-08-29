"""Basic tests for the Phase 1 classical pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data_loader import load_breast_cancer_dataset
from src.evaluate import compute_classification_metrics
from src.preprocessing import stratified_train_test_split


def test_dataset_loads_successfully() -> None:
    data = load_breast_cancer_dataset()
    assert data.n_samples > 0
    assert data.n_features == 30
    assert data.features.shape == (data.n_samples, 30)
    assert set(data.target.unique()) == {0, 1}
    assert data.n_malignant > 0
    assert data.n_benign > 0
    assert data.n_malignant + data.n_benign == data.n_samples


def test_train_test_split_preserves_both_target_classes() -> None:
    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    assert set(pd.Series(y_train).unique()) == {0, 1}
    assert set(pd.Series(y_test).unique()) == {0, 1}
    assert len(x_train) + len(x_test) == data.n_samples
    assert abs(len(x_test) / data.n_samples - 0.20) < 0.02


def test_metric_evaluation_values_are_between_zero_and_one() -> None:
    y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
    y_pred = np.array([0, 1, 1, 1, 0, 0, 1, 0])
    y_prob = np.array([0.1, 0.6, 0.9, 0.8, 0.4, 0.2, 0.7, 0.15])
    metrics = compute_classification_metrics(y_true, y_pred, y_prob)
    assert set(metrics) == {
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1",
        "roc_auc",
    }
    for name, value in metrics.items():
        assert 0.0 <= value <= 1.0, f"{name}={value} is outside [0, 1]"


def test_specificity_matches_confusion_matrix_formula() -> None:
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    y_prob = np.array([0.1, 0.8, 0.9, 0.7])
    metrics = compute_classification_metrics(y_true, y_pred, y_prob)
    # TN=1, FP=1, FN=0, TP=2 → specificity = 1/2
    assert metrics["specificity"] == pytest.approx(0.5)
