"""Explainability for the **classical** models on the same columns as QML.

Circuit models (VQC / QSVC / QNN) do not give a per-feature medical story,
so we explain the classical model trained on the identical features and say
so out loud.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline

from src.preprocessing import RANDOM_STATE

QML_EXPLAINABILITY_LIMITS = (
    "VQC / QNN weights live inside a parameterized circuit; they are not "
    "feature importances. A fidelity kernel (QSVC) mixes all inputs into a "
    "state overlap. We therefore explain the classical model on the same "
    "columns and report QML only through metrics and runtime."
)


def _final_estimator(model):
    if isinstance(model, Pipeline):
        return model.steps[-1][1]
    return model


def _transform_through_pipeline(model, x):
    """Apply every step except the final estimator."""
    if not isinstance(model, Pipeline):
        return np.asarray(x, dtype=float)
    data = x
    for _name, step in model.steps[:-1]:
        data = step.transform(data)
    return np.asarray(data, dtype=float)


def logistic_coefficient_table(model, feature_names) -> pd.DataFrame:
    """Signed standardized coefficients for a logistic-regression pipeline."""
    estimator = _final_estimator(model)
    coefficients = getattr(estimator, "coef_", None)
    if coefficients is None:
        raise TypeError("This model has no linear coefficients to report.")
    values = np.asarray(coefficients).ravel()
    names = list(feature_names)
    if len(names) != values.shape[0]:
        raise ValueError(
            f"Got {len(names)} feature names for {values.shape[0]} coefficients."
        )
    frame = pd.DataFrame(
        {
            "feature": names,
            "coefficient": values,
            "abs_coefficient": np.abs(values),
            "pushes_toward": ["positive class" if v > 0 else "negative class" for v in values],
        }
    )
    return frame.sort_values("abs_coefficient", ascending=False).reset_index(drop=True)


def permutation_table(
    model,
    x_test,
    y_test,
    feature_names,
    *,
    scoring: str = "f1",
    n_repeats: int = 10,
) -> pd.DataFrame:
    """Permutation importance measured on the held-out rows."""
    result = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=n_repeats,
        random_state=RANDOM_STATE,
        scoring=scoring,
    )
    frame = pd.DataFrame(
        {
            "feature": list(feature_names),
            f"permutation_{scoring}_mean": result.importances_mean,
            f"permutation_{scoring}_std": result.importances_std,
        }
    )
    return frame.sort_values(
        f"permutation_{scoring}_mean", ascending=False
    ).reset_index(drop=True)


def row_contributions(model, row, feature_names, *, top: int = 6) -> pd.DataFrame:
    """Per-feature contribution for one row of a linear pipeline.

    contribution = standardized_value * coefficient. This explains **why the
    research score moved** for that row on this public table. It is not a
    clinical explanation.
    """
    estimator = _final_estimator(model)
    coefficients = getattr(estimator, "coef_", None)
    if coefficients is None:
        raise TypeError("row_contributions needs a linear model (coef_).")
    frame_row = pd.DataFrame([row], columns=list(feature_names))
    transformed = _transform_through_pipeline(model, frame_row).ravel()
    weights = np.asarray(coefficients).ravel()
    contributions = transformed * weights
    frame = pd.DataFrame(
        {
            "feature": list(feature_names),
            "standardized_value": transformed,
            "coefficient": weights,
            "contribution": contributions,
            "abs_contribution": np.abs(contributions),
        }
    )
    frame = frame.sort_values("abs_contribution", ascending=False).reset_index(drop=True)
    return frame.head(int(top))
