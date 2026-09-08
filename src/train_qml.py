"""Phase 3: hybrid QML on Wisconsin k features (Qiskit Aer simulator).

Run from the project root (venv on, Qiskit installed):

    python -m src.train_qml

Optional:

    python -m src.train_qml --maxiter 60 --feature-reps 2 --ansatz-reps 2
    python -m src.train_qml --skip-vqc

Uses the **same** stratified split as Phase 1/2 (`random_state=42`) and
train-only SelectKBest. Includes a classical RBF SVM as a fair kernel
baseline next to QSVC. Does not assume quantum models win.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_loader import load_breast_cancer_dataset
from src.decision_support import best_f1_threshold, threshold_for_min_recall
from src.evaluate import brier_scores, evaluate_models, plot_calibration_curves
from src.feature_selection import (
    DEFAULT_K,
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.qml_models import (
    build_qnn_classifier,
    build_qsvc,
    build_rbf_svm_pipeline,
    build_vqc,
    describe_circuits,
    labels_to_pm1,
    qnn_ranking_scores,
    require_qiskit,
    scale_to_unit_interval,
    swap_in_picklable_optimizer,
)
from src.train_classical import (
    LR_MODEL_NAME,
    RBF_SVM_NAME,
    RF_MODEL_NAME,
    build_logistic_regression_pipeline,
    build_random_forest,
    predict_with_probabilities,
)
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

RBF_NAME = RBF_SVM_NAME
VQC_NAME = "VQC"
QSVC_NAME = "QSVC"
QNN_NAME = "QNN"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train hybrid QML models on reduced Wisconsin features."
    )
    parser.add_argument("--k", type=int, default=DEFAULT_K, help="SelectKBest k")
    parser.add_argument("--maxiter", type=int, default=60, help="VQC COBYLA iterations")
    parser.add_argument("--feature-reps", type=int, default=2, dest="feature_reps")
    parser.add_argument("--ansatz-reps", type=int, default=2, dest="ansatz_reps")
    parser.add_argument(
        "--skip-vqc",
        action="store_true",
        help="Skip VQC (faster; still trains QSVC + classical).",
    )
    parser.add_argument(
        "--with-qnn",
        action="store_true",
        dest="with_qnn",
        help="Also train an EstimatorQNN classifier ('QNN or equivalent').",
    )
    parser.add_argument(
        "--qnn-maxiter",
        type=int,
        default=40,
        dest="qnn_maxiter",
        help="COBYLA iterations for the QNN track.",
    )
    parser.add_argument(
        "--skip-calibration",
        action="store_true",
        dest="skip_calibration",
        help="Skip the calibrated-QSVC reliability curve (saves a few refits).",
    )
    return parser.parse_args(argv)


def _predict_timed(model, x_test):
    start = time.perf_counter()
    y_pred, y_score = predict_with_probabilities(model, x_test)
    return y_pred, y_score, time.perf_counter() - start


def _fit_timed(model, x_train, y_train, x_test):
    start = time.perf_counter()
    model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    y_pred, y_score, pred_s = _predict_timed(model, x_test)
    return model, y_pred, y_score, fit_seconds, pred_s


def _save_joblib(model, path) -> None:
    try:
        joblib.dump(model, path, compress=3)
        print(f"Saved {path}", flush=True)
    except Exception as exc:
        print(f"Could not pickle {path.name} ({exc}); metrics were still saved.", flush=True)


def _plot_optimizer_trace(history: list[float], path, *, label: str = "VQC") -> None:
    if not history:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(1, len(history) + 1), history, marker="o", markersize=3)
    ax.set_xlabel("COBYLA evaluation")
    ax.set_ylabel("Objective")
    ax.set_title(f"{label} optimizer trace\n{RESEARCH_DISCLAIMER}")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _write_circuit_notes(
    path,
    *,
    n_qubits: int,
    feature_reps: int,
    ansatz_reps: int,
) -> None:
    lines = [
        RESEARCH_DISCLAIMER,
        "",
        describe_circuits(
            n_qubits=n_qubits,
            feature_reps=feature_reps,
            ansatz_reps=ansatz_reps,
        ),
        "",
    ]
    try:
        ZZFeatureMap, RealAmplitudes, *_rest = require_qiskit()
        feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=feature_reps)
        ansatz = RealAmplitudes(num_qubits=n_qubits, reps=ansatz_reps)
        lines.append("Feature map (text):")
        lines.append(str(feature_map.decompose().draw(output="text")))
        lines.append("")
        lines.append("Ansatz (text):")
        lines.append(str(ansatz.decompose().draw(output="text")))
        lines.append("")
        lines.append(f"Ansatz parameters: {int(ansatz.num_parameters)}")
    except Exception as exc:
        lines.append(f"Could not draw circuits: {exc}")
    path.write_text("\n".join(lines), encoding="utf-8")


def _calibrated_qsvc_probabilities(qsvc, x_train, y_train, x_test):
    """Platt-scale QSVC on the training split so a reliability curve is honest.

    QSVC ranks with ``decision_function``, which is not a probability. Returns
    ``None`` when the estimator cannot be cloned or refit.
    """
    from sklearn.base import clone
    from sklearn.calibration import CalibratedClassifierCV

    try:
        base = clone(qsvc)
    except Exception as exc:
        print(f"  Calibration skipped (clone failed: {exc}).", flush=True)
        return None
    try:
        calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=3, ensemble=False)
        calibrated.fit(x_train, y_train)
        return np.asarray(calibrated.predict_proba(x_test))[:, 1]
    except Exception as exc:
        print(f"  Calibration skipped ({type(exc).__name__}: {exc}).", flush=True)
        return None


def _verdict(metrics_by_model: dict[str, dict[str, float]]) -> str:
    qml_names = [n for n in (VQC_NAME, QSVC_NAME, QNN_NAME) if n in metrics_by_model]
    classical_names = [
        n
        for n in (LR_MODEL_NAME, RF_MODEL_NAME, RBF_NAME)
        if n in metrics_by_model
    ]
    if not qml_names or not classical_names:
        return "Not enough models to compare QML vs classical on this run."
    qml_f1 = max(metrics_by_model[n]["f1"] for n in qml_names)
    classical_f1 = max(metrics_by_model[n]["f1"] for n in classical_names)
    if qml_f1 > classical_f1 + 1e-6:
        return (
            "On this split, a QML model had a higher F1 than the classical "
            "baselines (including RBF SVM). That is a measured result on this "
            "public table, not a clinical claim."
        )
    if qml_f1 < classical_f1 - 1e-6:
        return (
            "On this split, QML did not beat the better classical F1 "
            "(including RBF SVM on the same reduced features). That is an "
            "acceptable research outcome."
        )
    return "On this split, QML and the better classical model tied on F1."


def _write_report(
    path,
    *,
    names: list[str],
    metrics_by_model: dict[str, dict[str, float]],
    timings: dict[str, dict[str, float]],
    config: dict,
    verdict: str,
    calibration: dict[str, float] | None = None,
    decision_rows: list[dict] | None = None,
) -> None:
    rows = []
    for model_name, scores in metrics_by_model.items():
        row = {"model": model_name, **scores, **timings.get(model_name, {})}
        rows.append(row)
    frame = pd.DataFrame(rows)

    def _table(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        lines = [
            "| " + " | ".join(cols) + " |",
            "| " + " | ".join("---" for _ in cols) + " |",
        ]
        for _, row in df.iterrows():
            cells = []
            for col in cols:
                val = row[col]
                if isinstance(val, float):
                    cells.append(f"{val:.4f}")
                else:
                    cells.append(str(val))
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    body = "\n".join(
        [
            "# Phase 3 — hybrid QML (simulator)",
            "",
            RESEARCH_DISCLAIMER,
            "",
            "Not a medical device. Wisconsin Diagnostic Breast Cancer only. "
            "Circuits run on a **classical simulator**, not hospital hardware.",
            "",
            "## Setup",
            "",
            f"- Split: stratified 80/20, `random_state={RANDOM_STATE}` (same as Phase 1/2).",
            f"- Feature selection: SelectKBest + mutual_info_classif, k={config['k']}, **train-only**.",
            f"- Selected columns: {', '.join(names)}",
            f"- Quantum scaling: MinMaxScaler to [0, 1], **train-only** (angle encoding).",
            f"- VQC: ZZFeatureMap reps={config['feature_reps']}, RealAmplitudes "
            f"reps={config['ansatz_reps']}, COBYLA maxiter={config['maxiter']}.",
            "- QSVC: FidelityStatevectorKernel (exact overlap; shot-based kernels were avoided).",
            f"- QNN track: {'EstimatorQNN + COBYLA maxiter=' + str(config.get('qnn_maxiter')) if config.get('with_qnn') else 'not run (use --with-qnn)'}.",
            "- Extra classical kernel: RBF SVM on the same k columns (fair kernel baseline).",
            "",
            "## Why this design",
            "",
            "Near-term circuits cannot ingest 30 raw FNA columns well. The hybrid "
            "path shrinks the table classically, then trains a small variational "
            "classifier and a quantum kernel SVM. The RBF SVM answers: would a "
            "**classical kernel** already capture this 6-D table?",
            "",
            "## Metrics (this machine, this split)",
            "",
            _table(frame),
            "",
            "## Calibration (probability quality, lower Brier is better)",
            "",
            (
                _table(
                    pd.DataFrame(
                        [
                            {"model": name, "brier_score": value}
                            for name, value in calibration.items()
                        ]
                    )
                )
                if calibration
                else "_No probability outputs to calibrate on this run._"
            ),
            "",
            "Models scored by `decision_function` (RBF SVM, raw QSVC, QNN "
            "expectation values) are **not** probabilities, so they are left out "
            "of the reliability curve unless Platt-scaled.",
            "",
            "## Decision support (threshold tuning on this split)",
            "",
            (
                _table(pd.DataFrame(decision_rows))
                if decision_rows
                else "_Not computed on this run._"
            ),
            "",
            "Thresholds are measured on the held-out rows of a public table. "
            "They are a sensitivity/specificity trade-off for research, **not** a "
            "clinical cut-off and **not** advice to run any test.",
            "",
            "## Verdict",
            "",
            verdict,
            "",
            "Do not treat a quantum win or loss as a product claim. Small public "
            "tables like WDBC are often nearly linearly separable; classical LR "
            "can be very strong.",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        ]
    )
    path.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print("Hybrid QML on a simulator - not a medical device.")
    print()
    ensure_output_directories()

    data = load_breast_cancer_dataset()
    x_train, x_test, y_train, y_test = stratified_train_test_split(
        data.features,
        data.target,
    )
    x_train, x_test = clip_numeric_by_train_quantiles(x_train, x_test)
    selector = fit_select_k_best(x_train, y_train, k=args.k)
    names = selected_feature_names(selector, list(x_train.columns))
    print(f"Selected features (k={args.k}): {', '.join(names)}")

    x_train_red = transform_features(selector, x_train)
    x_test_red = transform_features(selector, x_test)
    y_train_np = np.asarray(y_train)
    y_test_np = np.asarray(y_test)

    predictions: dict = {}
    probabilities: dict = {}
    timings: dict[str, dict[str, float]] = {}

    classical_builders = {
        LR_MODEL_NAME: build_logistic_regression_pipeline,
        RF_MODEL_NAME: build_random_forest,
        RBF_NAME: build_rbf_svm_pipeline,
    }
    print("Training classical baselines on reduced features (one fit each)...", flush=True)
    models_dir = get_models_dir()
    save_map = {
        LR_MODEL_NAME: models_dir / "qml_reduced_logistic_regression_model.joblib",
        RF_MODEL_NAME: models_dir / "qml_reduced_random_forest_model.joblib",
        RBF_NAME: models_dir / "qml_reduced_rbf_svm_model.joblib",
    }
    for name, builder in classical_builders.items():
        model, y_pred, y_score, fit_s, pred_s = _fit_timed(
            builder(), x_train_red, y_train, x_test_red
        )
        predictions[name] = y_pred
        probabilities[name] = y_score
        timings[name] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
        _save_joblib(model, save_map[name])
        print(f"  {name}: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)

    scaler, x_train_q, x_test_q = scale_to_unit_interval(x_train_red, x_test_red)
    n_qubits = int(x_train_q.shape[1])
    joblib.dump(scaler, models_dir / "qml_minmax_scaler.joblib", compress=3)

    config = {
        "k": args.k,
        "n_qubits": n_qubits,
        "maxiter": args.maxiter,
        "feature_reps": args.feature_reps,
        "ansatz_reps": args.ansatz_reps,
        "skip_vqc": bool(args.skip_vqc),
        "with_qnn": bool(args.with_qnn),
        "qnn_maxiter": args.qnn_maxiter,
        "random_state": RANDOM_STATE,
        "selected_features": names,
        "disclaimer": RESEARCH_DISCLAIMER,
    }

    vqc_history: list[float] = []
    if not args.skip_vqc:
        print(
            f"Training VQC ({n_qubits} qubits, COBYLA maxiter={args.maxiter}, "
            f"feature_reps={args.feature_reps}, ansatz_reps={args.ansatz_reps})...",
            flush=True,
        )

        vqc = build_vqc(
            n_qubits=n_qubits,
            maxiter=args.maxiter,
            feature_reps=args.feature_reps,
            ansatz_reps=args.ansatz_reps,
            history=vqc_history,
        )
        vqc, y_pred, y_score, fit_s, pred_s = _fit_timed(
            vqc, x_train_q, y_train_np, x_test_q
        )
        predictions[VQC_NAME] = y_pred
        probabilities[VQC_NAME] = y_score
        timings[VQC_NAME] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
        print(f"  VQC: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)
        _save_joblib(vqc, models_dir / "vqc_model.joblib")
        _plot_optimizer_trace(
            vqc_history,
            get_figures_dir() / "qml_vqc_optimizer_trace.png",
            label="VQC",
        )
    else:
        print("Skipping VQC (--skip-vqc).", flush=True)

    print(
        f"Training QSVC ({n_qubits} qubits, ZZFeatureMap reps={args.feature_reps}, "
        "FidelityStatevectorKernel)...",
        flush=True,
    )
    qsvc = build_qsvc(n_qubits=n_qubits, feature_reps=args.feature_reps)
    qsvc, y_pred, y_score, fit_s, pred_s = _fit_timed(
        qsvc, x_train_q, y_train_np, x_test_q
    )
    predictions[QSVC_NAME] = y_pred
    probabilities[QSVC_NAME] = y_score
    timings[QSVC_NAME] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
    print(f"  QSVC: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)
    _save_joblib(qsvc, models_dir / "qsvc_model.joblib")

    if args.with_qnn:
        print(
            f"Training QNN ({n_qubits} qubits, EstimatorQNN, "
            f"COBYLA maxiter={args.qnn_maxiter})...",
            flush=True,
        )
        qnn_history: list[float] = []
        qnn = build_qnn_classifier(
            n_qubits=n_qubits,
            maxiter=args.qnn_maxiter,
            feature_reps=args.feature_reps,
            ansatz_reps=1,
            history=qnn_history,
        )
        start = time.perf_counter()
        qnn.fit(x_train_q, labels_to_pm1(y_train_np))
        qnn_fit_s = time.perf_counter() - start
        start = time.perf_counter()
        qnn_scores = qnn_ranking_scores(qnn, x_test_q)
        qnn_pred = (qnn_scores > 0).astype(int)
        qnn_pred_s = time.perf_counter() - start
        predictions[QNN_NAME] = qnn_pred
        probabilities[QNN_NAME] = qnn_scores
        timings[QNN_NAME] = {
            "fit_seconds": qnn_fit_s,
            "predict_seconds": qnn_pred_s,
        }
        print(f"  QNN: fit {qnn_fit_s:.2f}s, predict {qnn_pred_s:.2f}s", flush=True)
        swap_in_picklable_optimizer(qnn, maxiter=args.qnn_maxiter)
        _save_joblib(qnn, models_dir / "qnn_model.joblib")
        _plot_optimizer_trace(
            qnn_history,
            get_figures_dir() / "qml_qnn_optimizer_trace.png",
            label="QNN",
        )

    metrics_by_model = evaluate_models(
        y_test_np,
        predictions,
        probabilities,
        save_plots=True,
        artifact_prefix="qml",
    )

    rows = []
    for name, scores in metrics_by_model.items():
        rows.append({"model": name, **scores, **timings.get(name, {})})
    csv_path = get_metrics_dir() / "qml_vs_classical_metrics.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    # Reliability: probability outputs plus a Platt-scaled QSVC for a fair curve.
    calibration_inputs = {
        name: np.asarray(scores, dtype=float)
        for name, scores in probabilities.items()
        if name in (LR_MODEL_NAME, RF_MODEL_NAME)
    }
    if not args.skip_calibration:
        print("Calibrating QSVC probabilities (Platt scaling on train only)...", flush=True)
        qsvc_proba = _calibrated_qsvc_probabilities(
            qsvc, x_train_q, y_train_np, x_test_q
        )
        if qsvc_proba is not None:
            calibration_inputs["QSVC (calibrated)"] = qsvc_proba
    calibration = brier_scores(y_test_np, calibration_inputs)
    plot_calibration_curves(
        y_test_np,
        calibration_inputs,
        get_figures_dir() / "qml_calibration_curve.png",
    )

    decision_rows = []
    for name in (LR_MODEL_NAME, RBF_NAME, QSVC_NAME):
        if name not in probabilities:
            continue
        scores = np.asarray(probabilities[name], dtype=float)
        best = best_f1_threshold(y_test_np, scores)
        decision_rows.append(
            {
                "model": name,
                "rule": "best F1 on this split",
                "threshold": best["threshold"],
                "recall": best["recall"],
                "specificity": best["specificity"],
                "f1": best["f1"],
                "false_negatives": best["false_negatives"],
            }
        )
        sensitive = threshold_for_min_recall(y_test_np, scores, min_recall=0.95)
        if sensitive is not None:
            decision_rows.append(
                {
                    "model": name,
                    "rule": "recall >= 0.95 (sensitivity-first)",
                    "threshold": sensitive["threshold"],
                    "recall": sensitive["recall"],
                    "specificity": sensitive["specificity"],
                    "f1": sensitive["f1"],
                    "false_negatives": sensitive["false_negatives"],
                }
            )
    if decision_rows:
        pd.DataFrame(decision_rows).to_csv(
            get_metrics_dir() / "qml_threshold_options.csv", index=False
        )

    reports = get_reports_dir()
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "phase3_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    _write_circuit_notes(
        reports / "phase3_circuit_notes.txt",
        n_qubits=n_qubits,
        feature_reps=args.feature_reps,
        ansatz_reps=args.ansatz_reps,
    )
    verdict = _verdict(metrics_by_model)
    _write_report(
        reports / "phase3_qml.md",
        names=names,
        metrics_by_model=metrics_by_model,
        timings=timings,
        config=config,
        verdict=verdict,
        calibration=calibration,
        decision_rows=decision_rows,
    )

    print()
    print("Test-set metrics (same split, reduced features)")
    for name, scores in metrics_by_model.items():
        extra = timings.get(name, {})
        timing = (
            f"  fit={extra.get('fit_seconds', float('nan')):.1f}s"
            if extra
            else ""
        )
        print(f"  {name}:{timing}")
        for key, value in scores.items():
            print(f"    {key}: {value:.4f}")

    print()
    print(verdict)
    print(f"Wrote {csv_path}")
    print(f"Wrote {reports / 'phase3_qml.md'}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"QML training failed: {exc}", file=sys.stderr)
        raise
