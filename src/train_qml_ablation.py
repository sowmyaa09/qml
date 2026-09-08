"""Phase 3 ablation: how many qubits does the quantum kernel actually need?

    python -m src.train_qml_ablation
    python -m src.train_qml_ablation --ks 4 6 8 --feature-reps 2

For each k, SelectKBest keeps k Wisconsin columns (train only), one qubit per
column. QSVC is compared against an RBF SVM on the **same** columns, with
wall-clock time. VQC is skipped on purpose: it is the slow part, and the
question here is qubit count vs kernel quality.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_loader import load_breast_cancer_dataset
from src.evaluate import compute_classification_metrics
from src.feature_selection import (
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.qml_models import (
    build_qsvc,
    build_rbf_svm_pipeline,
    scale_to_unit_interval,
)
from src.train_classical import predict_with_probabilities
from src.train_tune import clip_numeric_by_train_quantiles
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_figures_dir,
    get_metrics_dir,
    get_reports_dir,
)

CSV_NAME = "qml_ablation_k.csv"
FIGURE_NAME = "qml_ablation_k.png"
REPORT_NAME = "phase3_ablation.md"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep the number of selected features (qubits) for QSVC."
    )
    parser.add_argument(
        "--ks",
        type=int,
        nargs="+",
        default=[4, 6, 8],
        help="Feature counts to try (allowed range 4-8).",
    )
    parser.add_argument("--feature-reps", type=int, default=2, dest="feature_reps")
    return parser.parse_args(argv)


def _fit_and_score(model, x_train, y_train, x_test, y_test) -> dict[str, float]:
    start = time.perf_counter()
    model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred, y_score = predict_with_probabilities(model, x_test)
    predict_seconds = time.perf_counter() - start
    metrics = compute_classification_metrics(y_test, y_pred, np.asarray(y_score))
    metrics["fit_seconds"] = fit_seconds
    metrics["predict_seconds"] = predict_seconds
    return metrics


def _plot(frame: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for model_name, group in frame.groupby("model"):
        ordered = group.sort_values("k")
        ax.plot(ordered["k"], ordered["f1"], marker="o", label=f"{model_name} F1")
    ax.set_xlabel("Selected features (= qubits for QSVC)")
    ax.set_ylabel("F1 on the held-out split")
    ax.set_ylim(0.0, 1.05)
    ax.set_xticks(sorted(frame["k"].unique()))

    twin = ax.twinx()
    qsvc = frame[frame["model"] == "QSVC"].sort_values("k")
    if not qsvc.empty:
        total = qsvc["fit_seconds"] + qsvc["predict_seconds"]
        twin.plot(
            qsvc["k"],
            total,
            marker="s",
            linestyle="--",
            color="gray",
            label="QSVC seconds",
        )
        twin.set_ylabel("QSVC fit + predict (seconds)")

    handles, labels = ax.get_legend_handles_labels()
    twin_handles, twin_labels = twin.get_legend_handles_labels()
    ax.legend(handles + twin_handles, labels + twin_labels, loc="lower left")
    ax.set_title(f"Qubit count vs quantum-kernel quality\n{RESEARCH_DISCLAIMER}")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


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
    print("Qubit-count ablation on a simulator - not a medical device.")
    print()
    ensure_output_directories()

    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features, data.target
    )
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    y_train_np = np.asarray(y_train)
    y_test_np = np.asarray(y_test)

    rows: list[dict] = []
    features_by_k: dict[int, list[str]] = {}
    for k in args.ks:
        selector = fit_select_k_best(x_train, y_train, k=k)
        names = selected_feature_names(selector, list(x_train.columns))
        features_by_k[k] = names
        x_train_red = transform_features(selector, x_train)
        x_test_red = transform_features(selector, x_test)
        _scaler, x_train_q, x_test_q = scale_to_unit_interval(x_train_red, x_test_red)

        print(f"k={k} ({', '.join(names)})", flush=True)

        rbf = _fit_and_score(
            build_rbf_svm_pipeline(), x_train_red, y_train, x_test_red, y_test_np
        )
        rows.append({"k": k, "model": "RBF SVM", **rbf})
        print(f"  RBF SVM: F1 {rbf['f1']:.4f} in {rbf['fit_seconds']:.2f}s", flush=True)

        qsvc = _fit_and_score(
            build_qsvc(n_qubits=k, feature_reps=args.feature_reps),
            x_train_q,
            y_train_np,
            x_test_q,
            y_test_np,
        )
        rows.append({"k": k, "model": "QSVC", **qsvc})
        print(
            f"  QSVC:    F1 {qsvc['f1']:.4f} in "
            f"{qsvc['fit_seconds'] + qsvc['predict_seconds']:.2f}s",
            flush=True,
        )

    frame = pd.DataFrame(rows)
    csv_path = get_metrics_dir() / CSV_NAME
    frame.to_csv(csv_path, index=False)
    figure_path = get_figures_dir() / FIGURE_NAME
    _plot(frame, figure_path)

    qsvc_only = frame[frame["model"] == "QSVC"].sort_values("f1", ascending=False)
    best_k = int(qsvc_only.iloc[0]["k"]) if not qsvc_only.empty else args.ks[0]
    slowest = frame[frame["model"] == "QSVC"].sort_values("fit_seconds").iloc[-1]

    report = get_reports_dir() / REPORT_NAME
    body = "\n".join(
        [
            "# Phase 3 ablation — qubits vs quantum-kernel quality",
            "",
            RESEARCH_DISCLAIMER,
            "",
            "Public Wisconsin table, simulator only. Not a medical device.",
            "",
            "## Setup",
            "",
            f"- Split: stratified 80/20, `random_state={RANDOM_STATE}`.",
            f"- Feature map reps: {args.feature_reps}. One qubit per selected column.",
            "- Selection is refit on the **training** rows for every k.",
            "- QSVC uses `FidelityStatevectorKernel`; RBF SVM sees the same columns.",
            "",
            "## Selected columns per k",
            "",
            *[f"- k={k}: {', '.join(v)}" for k, v in features_by_k.items()],
            "",
            "## Results",
            "",
            _md_table(frame),
            "",
            f"Figure: `{FIGURE_NAME}`.",
            "",
            "## Reading this",
            "",
            f"- Best QSVC F1 on this split came from **k={best_k}**.",
            f"- Cost grows with k: the slowest QSVC fit here was k={int(slowest['k'])} "
            f"at {float(slowest['fit_seconds']):.1f}s.",
            "- More qubits is not automatically better: the feature map entangles "
            "more dimensions, and a small table can lose more to noise in the "
            "selection step than it gains in expressivity.",
            "- The RBF column is the honest control. If a classical kernel matches "
            "QSVC at the same k, the quantum kernel is not adding value **here**.",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        ]
    )
    report.write_text(body, encoding="utf-8")

    print()
    print(f"Wrote {csv_path}")
    print(f"Wrote {figure_path}")
    print(f"Wrote {report}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ablation failed: {exc}", file=sys.stderr)
        raise
