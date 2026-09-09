"""Load QML cost/latency artifacts for the LAKSHYA dashboard.

Reads ``outputs/metrics/qml_ablation_k.csv`` and
``outputs/metrics/qml_vs_classical_metrics.csv`` when present; otherwise
returns documented fallback numbers from the judge sheet (same machine run).

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import RESEARCH_DISCLAIMER, get_figures_dir, get_metrics_dir

# Fallback when metrics/ is empty (fresh clone before training).
FALLBACK_ABLATION: list[dict[str, Any]] = [
    {"k": 4, "model": "RBF SVM", "f1": 0.8889, "fit_seconds": 0.01, "predict_seconds": 0.0},
    {"k": 4, "model": "QSVC", "f1": 0.8889, "fit_seconds": 1.40, "predict_seconds": 0.0},
    {"k": 6, "model": "RBF SVM", "f1": 0.9512, "fit_seconds": 0.01, "predict_seconds": 0.0},
    {"k": 6, "model": "QSVC", "f1": 0.9500, "fit_seconds": 2.04, "predict_seconds": 0.0},
    {"k": 8, "model": "RBF SVM", "f1": 0.9524, "fit_seconds": 0.01, "predict_seconds": 0.0},
    {"k": 8, "model": "QSVC", "f1": 0.9524, "fit_seconds": 3.20, "predict_seconds": 0.0},
]

FALLBACK_HEADLINE: list[dict[str, Any]] = [
    {"model": "Logistic Regression", "f1": 0.9412, "fit_seconds": 0.05, "predict_seconds": 0.0},
    {"model": "Random Forest", "f1": 0.9157, "fit_seconds": 0.12, "predict_seconds": 0.0},
    {"model": "RBF SVM", "f1": 0.9512, "fit_seconds": 0.01, "predict_seconds": 0.0},
    {"model": "QSVC", "f1": 0.9500, "fit_seconds": 2.12, "predict_seconds": 0.0},
    {"model": "VQC", "f1": 0.5806, "fit_seconds": 600.0, "predict_seconds": 0.0},
    {"model": "QNN", "f1": 0.5867, "fit_seconds": 120.0, "predict_seconds": 0.0},
]


def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _row_total_seconds(row: dict[str, Any]) -> float:
    fit_s = float(row.get("fit_seconds") or 0.0)
    pred_s = float(row.get("predict_seconds") or 0.0)
    return fit_s + pred_s


def _normalize_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in frame.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for key, value in record.items():
            if pd.isna(value):
                continue
            if key in ("k",):
                clean[key] = int(value)
            elif key == "model":
                clean[key] = str(value)
            elif isinstance(value, (int, float)):
                clean[key] = float(value)
            else:
                clean[key] = value
        if clean:
            rows.append(clean)
    return rows


def _headline_insight(models: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {str(r["model"]): r for r in models if "model" in r}
    qsvc = by_name.get("QSVC")
    rbf = by_name.get("RBF SVM")
    if not qsvc or not rbf:
        return {}
    qsvc_f1 = float(qsvc.get("f1", 0.0))
    rbf_f1 = float(rbf.get("f1", 0.0))
    qsvc_s = _row_total_seconds(qsvc)
    rbf_s = max(_row_total_seconds(rbf), 1e-6)
    ratio = qsvc_s / rbf_s
    return {
        "qsvc_f1": qsvc_f1,
        "rbf_f1": rbf_f1,
        "f1_delta": qsvc_f1 - rbf_f1,
        "qsvc_seconds": qsvc_s,
        "rbf_seconds": rbf_s,
        "latency_ratio": ratio,
        "verdict": (
            "QSVC matches RBF on F1 within this split but takes "
            f"~{ratio:.0f}× longer to fit — pitch cost, not accuracy."
            if ratio >= 2
            else "QSVC and RBF are comparable on this split; check fit seconds."
        ),
    }


def build_cost_latency_payload() -> dict[str, Any]:
    """JSON payload for GET /v1/qml-cost-latency."""
    metrics_dir = get_metrics_dir()
    ablation_path = metrics_dir / "qml_ablation_k.csv"
    headline_path = metrics_dir / "qml_vs_classical_metrics.csv"
    figure_path = get_figures_dir() / "qml_ablation_k.png"

    ablation_frame = _read_csv(ablation_path)
    headline_frame = _read_csv(headline_path)

    ablation_source = "live" if ablation_frame is not None else "fallback"
    headline_source = "live" if headline_frame is not None else "fallback"

    ablation = (
        _normalize_rows(ablation_frame)
        if ablation_frame is not None
        else list(FALLBACK_ABLATION)
    )
    headline = (
        _normalize_rows(headline_frame)
        if headline_frame is not None
        else list(FALLBACK_HEADLINE)
    )

    for row in ablation + headline:
        row["total_seconds"] = _row_total_seconds(row)

    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "dataset": "Wisconsin Diagnostic Breast Cancer (reduced k features)",
        "hardware_note": "Qiskit Aer statevector simulator on laptop; wall-clock seconds.",
        "ablation": ablation,
        "ablation_source": ablation_source,
        "headline_models": headline,
        "headline_source": headline_source,
        "insight": _headline_insight(headline),
        "figure_available": figure_path.is_file(),
        "figure_url": "/v1/figures/qml_ablation_k.png" if figure_path.is_file() else None,
        "train_commands": [
            "python -m src.train_qml --skip-vqc",
            "python -m src.train_qml_ablation",
        ],
    }
