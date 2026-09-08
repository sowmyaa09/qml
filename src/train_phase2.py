"""Phase 2: select 4–8 Wisconsin features on the training split only.

Run from the project root:

    python -m src.train_phase2

Compares full 30-feature classical models vs the reduced set on the
**same** test rows. Writes a reproducibility note under outputs/reports/.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import sys

import pandas as pd

from src.data_loader import load_breast_cancer_dataset, print_dataset_inspection
from src.evaluate import beginner_summary, evaluate_models
from src.feature_selection import (
    DEFAULT_K,
    fit_select_k_best,
    save_selector,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.train_classical import predict_with_probabilities, train_and_save_models
from src.train_tune import clip_numeric_by_train_quantiles
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
    get_reports_dir,
)


def _eval_block(models, x_test, y_test, *, artifact_prefix: str):
    predictions = {}
    probabilities = {}
    for name, model in models.items():
        y_pred, y_prob = predict_with_probabilities(model, x_test)
        predictions[name] = y_pred
        probabilities[name] = y_prob
    return evaluate_models(
        y_test,
        predictions,
        probabilities,
        save_plots=True,
        artifact_prefix=artifact_prefix,
    )


def _write_reproducibility_note(
    *,
    k: int,
    selected: list[str],
    full_metrics: dict,
    reduced_metrics: dict,
    n_train: int,
    n_test: int,
) -> None:
    path = get_reports_dir() / "phase2_reproducibility.md"
    lines = [
        "# Phase 2 reproducibility note",
        "",
        RESEARCH_DISCLAIMER,
        "",
        "This is not a clinical study. Scores are for the public Wisconsin",
        "Diagnostic Breast Cancer test split only.",
        "",
        "## Split",
        "",
        f"- Stratified 80/20, `random_state={RANDOM_STATE}`",
        f"- Train rows: {n_train}",
        f"- Test rows: {n_test}",
        "- The test rows are **never** used to fit `SelectKBest`.",
        "",
        "## Selector",
        "",
        f"- `SelectKBest` with `mutual_info_classif` (`random_state={RANDOM_STATE}`)",
        f"- `k={k}` (target range 4–8 for near-term quantum circuits)",
        "",
        "## Selected features",
        "",
    ]
    for name in selected:
        lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Full vs reduced (same test rows)",
            "",
            "| Setting | Model | recall | f1 | roc_auc | accuracy |",
            "|---------|-------|--------|----|---------|----------|",
        ]
    )
    for label, metrics in (("full_30", full_metrics), (f"reduced_{k}", reduced_metrics)):
        for model_name, scores in metrics.items():
            lines.append(
                f"| {label} | {model_name} | {scores['recall']:.4f} | "
                f"{scores['f1']:.4f} | {scores['roc_auc']:.4f} | "
                f"{scores['accuracy']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## How to reproduce",
            "",
            "```text",
            "python -m src.train_phase2",
            "```",
            "",
            "Artifacts: `models/phase2_select_kbest.joblib`,",
            "`outputs/reports/phase2_selected_features.json`,",
            "`outputs/metrics/phase2_*_classical_model_metrics.csv`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}", flush=True)


def main() -> int:
    k = DEFAULT_K
    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print()

    ensure_output_directories()
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

    print("Fitting SelectKBest on the training split only...", flush=True)
    selector = fit_select_k_best(x_train, y_train, k=k)
    selected = selected_feature_names(selector, list(x_train.columns))
    print(f"Kept k={k} features: {', '.join(selected)}")

    save_selector(selector, list(x_train.columns), k=k)
    x_train_red = transform_features(selector, x_train)
    x_test_red = transform_features(selector, x_test)

    print("Training full 30-feature classical models...", flush=True)
    full_models = train_and_save_models(x_train, y_train, name_prefix="phase2_full")
    full_metrics = _eval_block(
        full_models, x_test, y_test, artifact_prefix="phase2_full"
    )

    print("Training reduced-feature classical models...", flush=True)
    reduced_models = train_and_save_models(
        x_train_red, y_train, name_prefix="phase2_reduced"
    )
    reduced_metrics = _eval_block(
        reduced_models, x_test_red, y_test, artifact_prefix="phase2_reduced"
    )

    comparison_rows = []
    for setting, metrics in (("full_30", full_metrics), (f"reduced_{k}", reduced_metrics)):
        for model_name, scores in metrics.items():
            comparison_rows.append({"setting": setting, "model": model_name, **scores})
    comparison_path = get_metrics_dir() / "phase2_full_vs_reduced_metrics.csv"
    pd.DataFrame(comparison_rows).to_csv(comparison_path, index=False)
    print(f"Wrote {comparison_path}", flush=True)

    print()
    print("Reduced-set test metrics (malignant = positive class)")
    for name, scores in reduced_metrics.items():
        print(f"  {name}:")
        for key, value in scores.items():
            print(f"    {key}: {value:.4f}")

    print()
    print(beginner_summary(reduced_metrics, positive_name="malignant"))
    _write_reproducibility_note(
        k=k,
        selected=selected,
        full_metrics=full_metrics,
        reduced_metrics=reduced_metrics,
        n_train=len(x_train),
        n_test=len(x_test),
    )
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Phase 2 failed: {exc}", file=sys.stderr)
        raise
