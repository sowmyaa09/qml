"""Explainability tables, QNN label mapping, and the reviewer sheet."""

from __future__ import annotations

import numpy as np
import pytest

from src.explain import (
    QML_EXPLAINABILITY_LIMITS,
    logistic_coefficient_table,
    permutation_table,
    row_contributions,
)
from src.make_judge_sheet import build_sheet
from src.qml_models import labels_to_pm1
from src.train_classical import build_logistic_regression_pipeline, build_random_forest

FEATURES = ["a", "b", "c", "d"]


def _fitted_logistic():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(60, 4))
    y = (x[:, 0] + 0.5 * x[:, 1] > 0).astype(int)
    import pandas as pd

    frame = pd.DataFrame(x, columns=FEATURES)
    model = build_logistic_regression_pipeline()
    model.fit(frame, y)
    return model, frame, y


def test_coefficient_table_is_sorted_and_signed() -> None:
    model, _x, _y = _fitted_logistic()
    table = logistic_coefficient_table(model, FEATURES)
    assert list(table["feature"])[0] == "a"
    assert table["abs_coefficient"].is_monotonic_decreasing
    assert set(table["pushes_toward"]) <= {"positive class", "negative class"}


def test_coefficient_table_rejects_tree_models() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=(40, 4))
    y = (x[:, 0] > 0).astype(int)
    forest = build_random_forest()
    forest.fit(x, y)
    with pytest.raises(TypeError):
        logistic_coefficient_table(forest, FEATURES)


def test_row_contributions_explain_one_row() -> None:
    model, frame, _y = _fitted_logistic()
    top = row_contributions(model, frame.iloc[0], FEATURES, top=3)
    assert len(top) == 3
    assert top["abs_contribution"].is_monotonic_decreasing
    assert set(top["feature"]) <= set(FEATURES)


def test_permutation_table_uses_held_out_rows() -> None:
    model, frame, y = _fitted_logistic()
    table = permutation_table(model, frame, y, FEATURES, n_repeats=3)
    assert len(table) == len(FEATURES)
    assert "permutation_f1_mean" in table.columns


def test_labels_to_pm1_only_accepts_binary() -> None:
    assert list(labels_to_pm1([0, 1, 1])) == [-1.0, 1.0, 1.0]
    with pytest.raises(ValueError):
        labels_to_pm1([0, 1, 2])


def test_judge_sheet_states_the_refusals() -> None:
    text = build_sheet()
    lowered = text.lower()
    assert "not for clinical use" in lowered
    assert "no diagnosis" in lowered
    assert "no multi-disease score" in lowered
    assert "random_state=42" in text


def test_qml_limits_text_is_explicit() -> None:
    assert "not feature importances" in QML_EXPLAINABILITY_LIMITS
