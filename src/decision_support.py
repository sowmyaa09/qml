"""Research decision-support helpers: probability bands and threshold tuning.

The problem statement's "prediction and decision support" deliverable means:
a **probability score for the label this model was trained on**, an early
**risk band**, and a **tunable threshold** that trades recall against false
positives. It does **not** mean a differential diagnosis across diseases.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

LOW_CUT = 0.20
HIGH_CUT = 0.60

BAND_LOWER = "lower research band"
BAND_MIDDLE = "middle research band"
BAND_UPPER = "upper research band"


def is_probability_like(scores) -> bool:
    """True when every score sits in [0, 1] (``predict_proba`` output)."""
    array = np.asarray(scores, dtype=float)
    if array.size == 0:
        return False
    return bool(array.min() >= -1e-9 and array.max() <= 1.0 + 1e-9)


def risk_band(probability: float, *, low: float = LOW_CUT, high: float = HIGH_CUT) -> str:
    """Bucket one probability. Bands describe the **table's** positive class."""
    value = float(probability)
    if not 0.0 - 1e-9 <= value <= 1.0 + 1e-9:
        raise ValueError("risk_band needs a probability in [0, 1].")
    if value < low:
        return BAND_LOWER
    if value < high:
        return BAND_MIDDLE
    return BAND_UPPER


def band_legend(*, low: float = LOW_CUT, high: float = HIGH_CUT) -> str:
    return (
        f"{BAND_LOWER}: p < {low:.2f} | "
        f"{BAND_MIDDLE}: {low:.2f} <= p < {high:.2f} | "
        f"{BAND_UPPER}: p >= {high:.2f}. "
        "Bands are research buckets on one public table, not triage advice."
    )


def threshold_metrics(y_true, y_score, threshold: float) -> dict[str, float]:
    """Confusion counts and rates when class 1 is predicted at ``threshold``."""
    truth = np.asarray(y_true).astype(int)
    scores = np.asarray(y_score, dtype=float)
    predicted = (scores >= float(threshold)).astype(int)
    tn, fp, fn, tp = confusion_matrix(truth, predicted, labels=[0, 1]).ravel()
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    total = tn + fp + fn + tp
    return {
        "threshold": float(threshold),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
        "recall": float(recall),
        "precision": float(precision),
        "specificity": float(specificity),
        "f1": float(f1),
        "accuracy": float((tp + tn) / total) if total else 0.0,
    }


def threshold_sweep(y_true, y_score, *, steps: int = 41) -> pd.DataFrame:
    """Sweep thresholds across the observed score range (works for decision scores)."""
    scores = np.asarray(y_score, dtype=float)
    if scores.size == 0:
        raise ValueError("threshold_sweep needs at least one score.")
    lo, hi = float(scores.min()), float(scores.max())
    if hi <= lo:
        hi = lo + 1e-6
    grid = np.linspace(lo, hi, max(int(steps), 3))
    return pd.DataFrame([threshold_metrics(y_true, scores, t) for t in grid])


_COUNT_COLUMNS = (
    "true_positives",
    "false_positives",
    "false_negatives",
    "true_negatives",
)


def _row_to_dict(row: pd.Series) -> dict:
    out: dict = {}
    for key, value in row.items():
        out[key] = int(value) if key in _COUNT_COLUMNS else float(value)
    return out


def threshold_for_min_recall(y_true, y_score, *, min_recall: float = 0.95) -> dict | None:
    """Highest threshold on this split that still reaches ``min_recall``.

    A sensitivity-first choice for a research demo, measured on the held-out
    split only. It is not a clinical cut-off.
    """
    sweep = threshold_sweep(y_true, y_score, steps=201)
    eligible = sweep[sweep["recall"] >= float(min_recall)]
    if eligible.empty:
        return None
    return _row_to_dict(eligible.sort_values("threshold", ascending=False).iloc[0])


def best_f1_threshold(y_true, y_score) -> dict:
    """Threshold with the highest F1 on this split (reported, not hard-coded)."""
    sweep = threshold_sweep(y_true, y_score, steps=201)
    return _row_to_dict(sweep.sort_values(["f1", "recall"], ascending=False).iloc[0])


def test_scores_filename(artifact_prefix: str = "") -> str:
    prefix = f"{artifact_prefix}_" if artifact_prefix else ""
    return f"{prefix}test_scores.csv"


def save_test_scores(
    y_true,
    scores_by_model: dict[str, np.ndarray],
    path: Path,
) -> Path:
    """Persist held-out truth + per-model score so the UI can retune thresholds."""
    truth = np.asarray(y_true).astype(int)
    rows = []
    for name, scores in scores_by_model.items():
        array = np.asarray(scores, dtype=float).ravel()
        if array.shape[0] != truth.shape[0]:
            continue
        kind = "probability" if is_probability_like(array) else "decision_score"
        for value, label in zip(array, truth):
            rows.append(
                {
                    "model": name,
                    "score": float(value),
                    "score_kind": kind,
                    "y_true": int(label),
                }
            )
    frame = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def load_test_scores(path: Path) -> pd.DataFrame | None:
    if not Path(path).is_file():
        return None
    return pd.read_csv(path)
