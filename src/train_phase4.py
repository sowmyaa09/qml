"""Phase 4: classical explainability notes + hybrid comparison report.

    python -m src.train_phase4

Reads Phase 2/3 artifacts when present. Does not claim quantum is better.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance

from src.data_loader import load_breast_cancer_dataset
from src.explain import (
    QML_EXPLAINABILITY_LIMITS,
    logistic_coefficient_table,
    row_contributions,
)
from src.feature_selection import (
    DEFAULT_K,
    FEATURES_JSON,
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.train_tune import clip_numeric_by_train_quantiles
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_figures_dir,
    get_metrics_dir,
    get_models_dir,
    get_reports_dir,
)


def _read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if path.is_file():
        return pd.read_csv(path)
    return None


def _md_table(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in frame.iterrows():
        cells = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                cells.append(f"{val:.4f}")
            else:
                cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print()
    ensure_output_directories()

    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features, data.target
    )
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    selector = fit_select_k_best(x_train, y_train, k=DEFAULT_K)
    names = selected_feature_names(selector, list(x_train.columns))
    x_test_red = transform_features(selector, x_test)

    rf_path = get_models_dir() / "phase2_reduced_random_forest_model.joblib"
    if not rf_path.is_file():
        rf_path = get_models_dir() / "qml_reduced_random_forest_model.joblib"
    importance_lines = ["No reduced Random Forest file found yet."]
    if rf_path.is_file():
        forest = joblib.load(rf_path)
        native = getattr(forest, "feature_importances_", None)
        perm = permutation_importance(
            forest,
            x_test_red,
            y_test,
            n_repeats=10,
            random_state=RANDOM_STATE,
            scoring="f1",
        )
        frame = pd.DataFrame(
            {
                "feature": names,
                "rf_impurity_importance": native if native is not None else [None] * len(names),
                "permutation_f1_mean": perm.importances_mean,
                "permutation_f1_std": perm.importances_std,
            }
        ).sort_values("permutation_f1_mean", ascending=False)
        csv_path = get_metrics_dir() / "phase4_feature_importance.csv"
        frame.to_csv(csv_path, index=False)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(frame["feature"], frame["permutation_f1_mean"])
        ax.invert_yaxis()
        ax.set_xlabel("Permutation importance (F1, test split)")
        ax.set_title(f"Reduced-feature Random Forest\n{RESEARCH_DISCLAIMER}")
        fig.tight_layout()
        fig_path = get_figures_dir() / "phase4_permutation_importance.png"
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        importance_lines = [
            f"Loaded `{rf_path.name}`.",
            "",
            _md_table(frame),
            "",
            f"Plot: `{fig_path.name}`. Impurity importance is a training-set hint;",
            "permutation importance is measured on the **test** rows for this split.",
        ]
        print(f"Wrote {csv_path}")
        print(f"Wrote {fig_path}")

    lr_lines = ["No reduced Logistic Regression file found yet."]
    lr_path = get_models_dir() / "qml_reduced_logistic_regression_model.joblib"
    if not lr_path.is_file():
        lr_path = get_models_dir() / "phase2_reduced_logistic_regression_model.joblib"
    if lr_path.is_file():
        logistic = joblib.load(lr_path)
        coefficients = logistic_coefficient_table(logistic, names)
        coef_csv = get_metrics_dir() / "phase4_lr_coefficients.csv"
        coefficients.to_csv(coef_csv, index=False)

        # One worked row so "why did the score move" is concrete, not abstract.
        example_index = 0
        example_row = x_test_red.iloc[example_index]
        contributions = row_contributions(logistic, example_row, names, top=DEFAULT_K)
        contrib_csv = get_metrics_dir() / "phase4_lr_row_contributions.csv"
        contributions.to_csv(contrib_csv, index=False)
        true_label = int(pd.Series(y_test).iloc[example_index])
        score = float(logistic.predict_proba(x_test_red.iloc[[example_index]])[0, 1])

        lr_lines = [
            f"Loaded `{lr_path.name}`. Standardized coefficients "
            "(sign = which class the feature pushes toward):",
            "",
            _md_table(coefficients),
            "",
            f"Worked example — test row {example_index} "
            f"(true label {true_label}, research probability {score:.3f}):",
            "",
            _md_table(contributions),
            "",
            "`contribution = standardized value x coefficient`. This says which "
            "columns moved **this row's** research score on this public table. "
            "It is not a clinical explanation and not a cause of disease.",
        ]
        print(f"Wrote {coef_csv}")
        print(f"Wrote {contrib_csv}")

    qml_csv = _read_csv_if_exists(get_metrics_dir() / "qml_vs_classical_metrics.csv")
    phase2_csv = _read_csv_if_exists(
        get_metrics_dir() / "phase2_full_vs_reduced_metrics.csv"
    )
    classical_csv = _read_csv_if_exists(
        get_metrics_dir() / "classical_model_metrics.csv"
    )

    report = get_reports_dir() / "hybrid_comparison.md"
    blocks = [
        "# Hybrid vs classical comparison",
        "",
        RESEARCH_DISCLAIMER,
        "",
        "Educational research only. Not a medical device. Not a diagnosis.",
        "",
        "## Scope",
        "",
        "- Public Wisconsin Diagnostic Breast Cancer table.",
        f"- Feature selection: `SelectKBest` mutual information, k={DEFAULT_K}, train only.",
        f"- Selected features: {', '.join(f'`{n}`' for n in names)}.",
        "- QML (when trained): Qiskit **Aer / statevector simulator**, VQC and QSVC.",
        "- Same stratified split (`random_state=42`).",
        "",
        "## Classical full vs reduced (Phase 2)",
        "",
    ]
    if phase2_csv is not None:
        blocks.append(_md_table(phase2_csv))
    else:
        blocks.append("_Run `python -m src.train_phase2` to fill this table._")

    blocks.extend(
        [
            "",
            "## QML vs reduced classical (Phase 3)",
            "",
        ]
    )
    if qml_csv is not None:
        blocks.append(_md_table(qml_csv))
        blocks.append("")
        blocks.append(
            "Runtime columns (if present) are wall-clock seconds on this machine. "
            "Simulator QML is often **slower** than logistic regression even when "
            "accuracy is similar. That is expected on near-term / simulated circuits."
        )
    else:
        blocks.append("_Run `python -m src.train_qml` to fill this table._")

    blocks.extend(
        [
            "",
            "## Phase 1 full-feature classical (reference)",
            "",
        ]
    )
    if classical_csv is not None:
        blocks.append(_md_table(classical_csv))
    else:
        blocks.append("_Run `python -m src.train_classical` if this file is missing._")

    blocks.extend(
        [
            "",
            "## Explainability — permutation importance (Random Forest)",
            "",
            *importance_lines,
            "",
            "## Explainability — linear coefficients and one worked row",
            "",
            *lr_lines,
            "",
            "## Limits of QML explainability here",
            "",
            QML_EXPLAINABILITY_LIMITS,
            "",
            "- VQC / QNN weights live in a parameterized circuit; they are **not** the",
            "  same as Random Forest split importances.",
            "- A fidelity kernel (QSVC) does not give a simple per-feature medical story.",
            "- Near-term devices cannot ingest 30 raw biomedical columns; selection is",
            "  required, and it can drop signal.",
            "",
            "## What this does **not** mean",
            "",
            "- Quantum is not automatically better.",
            "- Extra public tables (diabetes, cardio, stroke, images) are **other**",
            "  experiments, not fused diagnosis.",
            "- Do not use these scores for clinical care.",
            "",
            f"Feature JSON: `{FEATURES_JSON}`.",
            "",
        ]
    )
    report.write_text("\n".join(blocks), encoding="utf-8")
    print(f"Wrote {report}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Phase 4 failed: {exc}", file=sys.stderr)
        raise
