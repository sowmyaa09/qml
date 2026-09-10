"""Second quantum experiment: QSVC on one small catalog table.

    python -m src.train_qml_table coimbra
    python -m src.train_qml_table ddd
    python -m src.train_qml_table hepatitis --k 6

One table, one label, its own report. This is **not** combined with the
Wisconsin experiment and it does not produce a multi-disease answer.

Wide tables (for example 178-column EEG) are rejected on purpose: a
near-term circuit gets a handful of classically selected features, never raw
signal channels.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from src.evaluate import evaluate_models
from src.feature_selection import (
    MAX_K,
    MIN_K,
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.qml_models import (
    build_qsvc,
    build_rbf_svm_pipeline,
    describe_circuits,
    scale_to_unit_interval,
)
from src.tabular_datasets import CATALOG, list_dataset_keys, load_tabular_dataset
from src.train_classical import (
    LR_MODEL_NAME,
    RBF_SVM_NAME,
    build_logistic_regression_pipeline,
    predict_with_probabilities,
)
from src.train_tune import clip_numeric_by_train_quantiles
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
    get_models_dir,
    get_reports_dir,
)

QSVC_NAME = "QSVC"
# A fidelity kernel is O(n^2) statevector overlaps; keep the demo laptop-sized.
DEFAULT_MAX_TRAIN = 400
DEFAULT_MAX_TEST = 150
MAX_SOURCE_COLUMNS = 60
# Large survey tables are classical-only. A 400-row subsample of 300k rows is
# not a hybrid experiment on that table.
MAX_QML_ROWS = 5000


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train QSVC + classical baselines on one small catalog table."
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default="coimbra",
        help=f"Catalog key (default coimbra). Options: {', '.join(list_dataset_keys())}",
    )
    parser.add_argument("--k", type=int, default=6, help="Features to keep (4-8).")
    parser.add_argument("--feature-reps", type=int, default=2, dest="feature_reps")
    parser.add_argument(
        "--max-train", type=int, default=DEFAULT_MAX_TRAIN, dest="max_train"
    )
    parser.add_argument("--max-test", type=int, default=DEFAULT_MAX_TEST, dest="max_test")
    return parser.parse_args(argv)


def _cap_rows(x, y, max_rows: int):
    """Stratified subsample so the quantum kernel stays laptop-sized."""
    if max_rows <= 0 or len(x) <= max_rows:
        return x, y, False
    x_small, _x_rest, y_small, _y_rest = train_test_split(
        x,
        y,
        train_size=max_rows,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    return x_small, y_small, True


def _fit_timed(model, x_train, y_train, x_test):
    start = time.perf_counter()
    model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred, y_score = predict_with_probabilities(model, x_test)
    return model, y_pred, y_score, fit_seconds, time.perf_counter() - start


def _md_table(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in frame.iterrows():
        cells = [
            f"{row[col]:.4f}" if isinstance(row[col], float) else str(row[col])
            for col in cols
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print("Second hybrid experiment on a simulator - not a medical device.")
    print()

    key = args.dataset
    if key not in CATALOG:
        print(
            f"Unknown dataset {key!r}. Options: {', '.join(list_dataset_keys())}",
            file=sys.stderr,
        )
        return 1
    if not MIN_K <= args.k <= MAX_K:
        print(f"--k must be between {MIN_K} and {MAX_K}.", file=sys.stderr)
        return 1

    ensure_output_directories()
    spec, features, target, path = load_tabular_dataset(key)
    if not spec.binary:
        print(f"{key} is multiclass; this hybrid script expects a binary label.", file=sys.stderr)
        return 1
    if features.shape[1] > MAX_SOURCE_COLUMNS:
        print(
            f"{key} has {features.shape[1]} columns. Refusing to run a circuit on a "
            "wide signal table; keep QML on compact clinical tables.",
            file=sys.stderr,
        )
        return 1
    if len(features) > MAX_QML_ROWS:
        print(
            f"{key} has {len(features)} rows. QSVC stays on small clinical tables "
            f"(at most {MAX_QML_ROWS} rows). Use `python -m src.train_tabular {key}` "
            "for the classical experiment instead of a tiny kernel subsample.",
            file=sys.stderr,
        )
        return 1

    print(f"=== {spec.title} ===")
    print(f"File: {path}")
    print(f"Rows: {len(features)} | Features: {features.shape[1]}")
    print(spec.notes or spec.positive_name)

    x_train, x_test, y_train, y_test = stratified_train_test_split(features, target)
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    x_train, y_train, capped_train = _cap_rows(x_train, y_train, args.max_train)
    x_test, y_test, capped_test = _cap_rows(x_test, y_test, args.max_test)

    # Small tables may have fewer usable columns than k.
    k = min(args.k, x_train.shape[1])
    if k < MIN_K:
        print(f"{key} has too few columns for a k>={MIN_K} hybrid run.", file=sys.stderr)
        return 1

    # Multi-cohort tables carry real missing values, and neither SelectKBest nor
    # a circuit accepts NaN. Impute on training statistics only, before
    # selection, so the test rows never influence the fill values.
    imputer = SimpleImputer(strategy="median")
    columns = list(x_train.columns)
    x_train = pd.DataFrame(
        imputer.fit_transform(x_train), columns=columns, index=x_train.index
    )
    x_test = pd.DataFrame(
        imputer.transform(x_test), columns=columns, index=x_test.index
    )

    selector = fit_select_k_best(x_train, y_train, k=k)
    names = selected_feature_names(selector, list(x_train.columns))
    x_train_red = transform_features(selector, x_train)
    x_test_red = transform_features(selector, x_test)
    y_train_np = np.asarray(y_train)
    y_test_np = np.asarray(y_test)
    print(f"Selected features (k={k}): {', '.join(names)}")

    predictions: dict = {}
    probabilities: dict = {}
    timings: dict[str, dict[str, float]] = {}

    for name, builder in (
        (LR_MODEL_NAME, build_logistic_regression_pipeline),
        (RBF_SVM_NAME, build_rbf_svm_pipeline),
    ):
        _model, y_pred, y_score, fit_s, pred_s = _fit_timed(
            builder(), x_train_red, y_train, x_test_red
        )
        predictions[name] = y_pred
        probabilities[name] = y_score
        timings[name] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
        print(f"  {name}: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)

    scaler, x_train_q, x_test_q = scale_to_unit_interval(x_train_red, x_test_red)
    joblib.dump(scaler, get_models_dir() / f"{key}_qml_minmax_scaler.joblib", compress=3)

    print(f"Training QSVC ({k} qubits, fidelity kernel)...", flush=True)
    qsvc, y_pred, y_score, fit_s, pred_s = _fit_timed(
        build_qsvc(n_qubits=k, feature_reps=args.feature_reps),
        x_train_q,
        y_train_np,
        x_test_q,
    )
    predictions[QSVC_NAME] = y_pred
    probabilities[QSVC_NAME] = y_score
    timings[QSVC_NAME] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
    print(f"  QSVC: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)
    try:
        joblib.dump(qsvc, get_models_dir() / f"{key}_qsvc_model.joblib", compress=3)
    except Exception as exc:
        print(f"Could not pickle QSVC ({exc}); metrics were still saved.", flush=True)

    metrics_by_model = evaluate_models(
        y_test_np,
        predictions,
        probabilities,
        save_plots=True,
        artifact_prefix=f"{key}_qml",
    )

    rows = [
        {"model": name, **scores, **timings.get(name, {})}
        for name, scores in metrics_by_model.items()
    ]
    frame = pd.DataFrame(rows)
    csv_path = get_metrics_dir() / f"{key}_qml_metrics.csv"
    frame.to_csv(csv_path, index=False)

    qsvc_f1 = metrics_by_model[QSVC_NAME]["f1"]
    classical_f1 = max(
        metrics_by_model[LR_MODEL_NAME]["f1"], metrics_by_model[RBF_SVM_NAME]["f1"]
    )
    if qsvc_f1 > classical_f1 + 1e-6:
        verdict = (
            f"On this split, QSVC had the higher F1 on {key}. One split on a small "
            "public table is weak evidence, not a quantum advantage claim."
        )
    elif qsvc_f1 < classical_f1 - 1e-6:
        verdict = (
            f"On this split, QSVC did not beat the better classical F1 on {key}. "
            "That is an acceptable research outcome."
        )
    else:
        verdict = f"On this split, QSVC tied the better classical F1 on {key}."

    report = get_reports_dir() / f"phase3_qml_{key}.md"
    body = "\n".join(
        [
            f"# Hybrid QML on a second table — {spec.title}",
            "",
            RESEARCH_DISCLAIMER,
            "",
            "Separate experiment. Not combined with Wisconsin. Not a diagnosis and "
            "not a multi-disease score.",
            "",
            "## Setup",
            "",
            f"- Source file: `{path.name}`",
            f"- Positive class: {spec.positive_name}",
            f"- Split: stratified 80/20, `random_state={RANDOM_STATE}`.",
            f"- Train rows used: {len(x_train_red)}"
            + (f" (capped at {args.max_train} for kernel cost)" if capped_train else ""),
            f"- Test rows used: {len(x_test_red)}"
            + (f" (capped at {args.max_test})" if capped_test else ""),
            f"- Selected columns (train-only SelectKBest, k={k}): {', '.join(names)}",
            "",
            "## Circuits",
            "",
            "```",
            describe_circuits(
                n_qubits=k, feature_reps=args.feature_reps, ansatz_reps=0
            ),
            "```",
            "",
            "## Results",
            "",
            _md_table(frame),
            "",
            "## Verdict",
            "",
            verdict,
            "",
            "Row caps mean this is a smaller sample than the classical run in "
            "`train_tabular`, so do not compare the two tables' numbers directly.",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        ]
    )
    report.write_text(body, encoding="utf-8")

    print()
    print("Test-set metrics")
    for name, scores in metrics_by_model.items():
        print(f"  {name}:")
        for metric, value in scores.items():
            print(f"    {metric}: {value:.4f}")
    print()
    print(verdict)
    print(f"Wrote {csv_path}")
    print(f"Wrote {report}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Second hybrid experiment failed: {exc}", file=sys.stderr)
        raise
