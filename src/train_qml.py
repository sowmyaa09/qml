"""Phase 3: VQC + QSVC vs reduced classical models on Wisconsin k features.

Run from the project root (venv on, Qiskit installed):

    python -m src.train_qml

Uses the **same** stratified split as Phase 1/2 (`random_state=42`) and the
Phase 2 selected columns. Does not assume quantum models win.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import sys
import time

import joblib
import numpy as np
import pandas as pd

from src.data_loader import load_breast_cancer_dataset
from src.evaluate import evaluate_models
from src.feature_selection import (
    DEFAULT_K,
    fit_select_k_best,
    selected_feature_names,
    transform_features,
)
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.qml_models import build_qsvc, build_vqc, scale_to_unit_interval
from src.train_classical import predict_with_probabilities, train_and_save_models
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
    get_models_dir,
)


def _fit_timed(model, x_train, y_train, x_test):
    start = time.perf_counter()
    model.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred, y_score = predict_with_probabilities(model, x_test)
    predict_seconds = time.perf_counter() - start
    return model, y_pred, y_score, fit_seconds, predict_seconds


def main() -> int:
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
    selector = fit_select_k_best(x_train, y_train, k=DEFAULT_K)
    names = selected_feature_names(selector, list(x_train.columns))
    print(f"Selected features (k={DEFAULT_K}): {', '.join(names)}")

    x_train_red = transform_features(selector, x_train)
    x_test_red = transform_features(selector, x_test)
    y_train_np = np.asarray(y_train)
    y_test_np = np.asarray(y_test)

    print("Training reduced classical baselines...", flush=True)
    classical = train_and_save_models(
        x_train_red, y_train, name_prefix="qml_reduced"
    )

    predictions = {}
    probabilities = {}
    timings: dict[str, dict[str, float]] = {}

    for name, model in classical.items():
        model, y_pred, y_score, fit_s, pred_s = _fit_timed(
            model, x_train_red, y_train, x_test_red
        )
        predictions[name] = y_pred
        probabilities[name] = y_score
        timings[name] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
        print(f"  {name}: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)

    scaler, x_train_q, x_test_q = scale_to_unit_interval(x_train_red, x_test_red)
    n_qubits = x_train_q.shape[1]
    joblib.dump(scaler, get_models_dir() / "qml_minmax_scaler.joblib", compress=3)

    print(f"Training VQC ({n_qubits} qubits, COBYLA maxiter=40)...", flush=True)
    vqc = build_vqc(n_qubits=n_qubits, maxiter=40)
    vqc, y_pred, y_score, fit_s, pred_s = _fit_timed(
        vqc, x_train_q, y_train_np, x_test_q
    )
    predictions["VQC"] = y_pred
    probabilities["VQC"] = y_score
    timings["VQC"] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
    print(f"  VQC: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)
    try:
        joblib.dump(vqc, get_models_dir() / "vqc_model.joblib", compress=3)
    except Exception as exc:
        print(f"Could not pickle VQC ({exc}); metrics were still saved.", flush=True)

    print(f"Training QSVC ({n_qubits} qubits, fidelity kernel)...", flush=True)
    qsvc = build_qsvc(n_qubits=n_qubits)
    qsvc, y_pred, y_score, fit_s, pred_s = _fit_timed(
        qsvc, x_train_q, y_train_np, x_test_q
    )
    predictions["QSVC"] = y_pred
    probabilities["QSVC"] = y_score
    timings["QSVC"] = {"fit_seconds": fit_s, "predict_seconds": pred_s}
    print(f"  QSVC: fit {fit_s:.2f}s, predict {pred_s:.2f}s", flush=True)
    try:
        joblib.dump(qsvc, get_models_dir() / "qsvc_model.joblib", compress=3)
    except Exception as exc:
        print(f"Could not pickle QSVC ({exc}); metrics were still saved.", flush=True)

    metrics_by_model = evaluate_models(
        y_test_np,
        predictions,
        probabilities,
        save_plots=True,
        artifact_prefix="qml",
    )

    rows = []
    for name, scores in metrics_by_model.items():
        row = {"model": name, **scores, **timings.get(name, {})}
        rows.append(row)
    csv_path = get_metrics_dir() / "qml_vs_classical_metrics.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

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

    qml_f1 = max(metrics_by_model["VQC"]["f1"], metrics_by_model["QSVC"]["f1"])
    classical_f1 = max(
        metrics_by_model["Logistic Regression"]["f1"],
        metrics_by_model["Random Forest"]["f1"],
    )
    if qml_f1 > classical_f1 + 1e-6:
        verdict = "On this split, a QML model had a higher F1 than both classical models."
    elif qml_f1 < classical_f1 - 1e-6:
        verdict = (
            "On this split, both QML models did not beat the better classical F1. "
            "That is an acceptable research outcome."
        )
    else:
        verdict = "On this split, QML and the better classical model tied on F1."
    print()
    print(verdict)
    print(f"Wrote {csv_path}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"QML training failed: {exc}", file=sys.stderr)
        raise
