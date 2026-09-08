"""Train and save diabetes survey models (Logistic Regression + Random Forest).

Run from the project root with the venv on:

    python -m src.train_diabetes

Saves (does not overwrite breast-cancer files):
    models/diabetes_logistic_regression_model.joblib
    models/diabetes_random_forest_model.joblib

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import sys

from src.diabetes_data import inspect_diabetes_dataset, load_diabetes_dataset
from src.evaluate import beginner_summary, evaluate_models
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.train_classical import (
    forest_for_table,
    predict_with_probabilities,
    train_and_save_models,
)
from src.train_tune import clip_numeric_by_train_quantiles
from src.train_tune import clip_numeric_by_train_quantiles
from src.utils import LONG_DISCLAIMER, RESEARCH_DISCLAIMER


def main() -> int:
    print(LONG_DISCLAIMER, flush=True)
    print(RESEARCH_DISCLAIMER, flush=True)
    print("Survey diabetes label - not a clinical test.", flush=True)
    print(flush=True)

    data = load_diabetes_dataset()
    print(inspect_diabetes_dataset(data), flush=True)
    print(flush=True)

    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    print(
        f"Train rows: {len(x_train)} | Test rows: {len(x_test)} "
        f"(80/20 stratified split, random_state={RANDOM_STATE})",
        flush=True,
    )
    print(
        "Fitting compact models (capped tree depth so the save file stays small)...",
        flush=True,
    )
    print(flush=True)

    models = train_and_save_models(
        x_train,
        y_train,
        name_prefix="diabetes",
        forest=forest_for_table(len(x_train)),
        tune=True,
    )

    predictions = {}
    probabilities = {}
    for name, model in models.items():
        y_pred, y_prob = predict_with_probabilities(model, x_test)
        predictions[name] = y_pred
        probabilities[name] = y_prob

    metrics_by_model = evaluate_models(
        y_test,
        predictions,
        probabilities,
        save_plots=True,
        artifact_prefix="diabetes",
    )

    print(flush=True)
    print("Test-set metrics (1 = diabetes survey label)", flush=True)
    for name, scores in metrics_by_model.items():
        print(f"  {name}:", flush=True)
        for key, value in scores.items():
            print(f"    {key}: {value:.4f}", flush=True)

    print(flush=True)
    print(
        beginner_summary(metrics_by_model, positive_name="diabetes (survey)"),
        flush=True,
    )
    print(RESEARCH_DISCLAIMER, flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Diabetes training failed: {exc}", file=sys.stderr)
        raise
