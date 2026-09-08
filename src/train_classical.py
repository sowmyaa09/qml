"""Train classical baselines: Logistic Regression and Random Forest.

Run from the project root:

    python -m src.train_classical

Research risk classification — not for clinical use.
"""

from __future__ import annotations

import sys

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.data_loader import load_breast_cancer_dataset, print_dataset_inspection
from src.evaluate import beginner_summary, evaluate_models
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.train_tune import clip_numeric_by_train_quantiles, fit_with_optional_search
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_models_dir,
)

LR_MODEL_NAME = "Logistic Regression"
RF_MODEL_NAME = "Random Forest"
RBF_SVM_NAME = "RBF SVM"


def build_logistic_regression_pipeline() -> Pipeline:
    """Imputer + scaler + logistic regression. Fit on training data only."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=8000,
                    class_weight="balanced",
                    solver="lbfgs",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def build_random_forest() -> Pipeline:
    """Median impute + Random Forest. Scaling is not required."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=400,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_compact_random_forest() -> Pipeline:
    """Smaller forest for large tables so the ``.joblib`` file stays usable."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=150,
                    max_depth=16,
                    min_samples_leaf=20,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def forest_for_table(n_rows: int) -> Pipeline:
    """Full forest on small tables; compact forest on large CSVs."""
    if n_rows >= 8000:
        return build_compact_random_forest()
    return build_random_forest()


def train_and_save_models(
    x_train,
    y_train,
    *,
    name_prefix: str = "",
    forest: Pipeline | RandomForestClassifier | None = None,
    tune: bool = True,
    scoring: str = "f1",
) -> dict:
    """Fit both models and write compressed ``.joblib`` files to ``models/``.

    ``name_prefix`` avoids overwriting the breast-cancer files, e.g. ``diabetes``.
    Optional ``tune`` runs a small GridSearchCV on the **training** split only.
    """
    ensure_output_directories()
    models_dir = get_models_dir()
    prefix = f"{name_prefix}_" if name_prefix else ""

    logistic = build_logistic_regression_pipeline()
    forest_model = forest if forest is not None else build_random_forest()

    lr_grid = {"classifier__C": [0.25, 1.0, 4.0]} if tune else None
    rf_grid = None
    if tune:
        rf_grid = {
            "classifier__max_depth": [12, None],
            "classifier__min_samples_leaf": [1, 4],
        }

    print("Fitting Logistic Regression...", flush=True)
    logistic = fit_with_optional_search(
        logistic, lr_grid, x_train, y_train, scoring=scoring
    )
    print("Fitting Random Forest...", flush=True)
    forest_model = fit_with_optional_search(
        forest_model, rf_grid, x_train, y_train, scoring=scoring
    )

    lr_path = models_dir / f"{prefix}logistic_regression_model.joblib"
    rf_path = models_dir / f"{prefix}random_forest_model.joblib"
    joblib.dump(logistic, lr_path, compress=3)
    joblib.dump(forest_model, rf_path, compress=3)
    print(f"Saved {lr_path} ({lr_path.stat().st_size / 1_000_000:.1f} MB)", flush=True)
    print(f"Saved {rf_path} ({rf_path.stat().st_size / 1_000_000:.1f} MB)", flush=True)

    return {LR_MODEL_NAME: logistic, RF_MODEL_NAME: forest_model}


def predict_with_probabilities(model, x_test):
    """Return class labels and a ranking score for class 1 (ROC-AUC)."""
    y_pred = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(x_test)
            if getattr(proba, "ndim", 1) == 2 and proba.shape[1] >= 2:
                return y_pred, proba[:, 1]
        except Exception:
            pass
    if hasattr(model, "decision_function"):
        scores = model.decision_function(x_test)
        return y_pred, scores
    raise RuntimeError(
        f"{type(model).__name__} has neither usable predict_proba nor "
        "decision_function. ROC-AUC needs a ranking score for class 1."
    )


def main() -> int:
    """Load data, split, train, evaluate, save artifacts, print a summary."""
    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print()

    data = load_breast_cancer_dataset()
    print_dataset_inspection(data)
    print()

    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    print(
        f"Train rows: {len(x_train)} | Test rows: {len(x_test)} "
        f"(80/20 stratified split, random_state={RANDOM_STATE})"
    )
    print()

    models = train_and_save_models(x_train, y_train)

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
    )

    print()
    print("Test-set metrics (malignant = positive class)")
    for name, scores in metrics_by_model.items():
        print(f"  {name}:")
        for key, value in scores.items():
            print(f"    {key}: {value:.4f}")

    print()
    print(beginner_summary(metrics_by_model, positive_name="malignant"))
    print()
    print("Wrote outputs/metrics/classical_model_metrics.csv")
    print("Wrote PNG plots under outputs/figures/")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Training failed: {exc}", file=sys.stderr)
        raise
