"""Threshold tuning, bands, calibration, and saved held-out scores."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.decision_support import (
    BAND_LOWER,
    BAND_MIDDLE,
    BAND_UPPER,
    best_f1_threshold,
    is_probability_like,
    load_test_scores,
    risk_band,
    save_test_scores,
    threshold_for_min_recall,
    threshold_metrics,
    threshold_sweep,
)
from src.decision_support import test_scores_filename as scores_filename
from src.evaluate import brier_scores, plot_calibration_curves

Y_TRUE = np.array([0, 0, 1, 1, 1, 0, 1, 0])
SCORES = np.array([0.10, 0.60, 0.90, 0.80, 0.40, 0.20, 0.70, 0.15])


def test_risk_bands_split_at_documented_cuts() -> None:
    assert risk_band(0.05) == BAND_LOWER
    assert risk_band(0.35) == BAND_MIDDLE
    assert risk_band(0.95) == BAND_UPPER
    with pytest.raises(ValueError):
        risk_band(1.4)


def test_threshold_metrics_match_hand_counts() -> None:
    at_half = threshold_metrics(Y_TRUE, SCORES, 0.5)
    # Predicted 1: scores 0.60, 0.90, 0.80, 0.70 -> 3 true positives, 1 false positive.
    assert at_half["true_positives"] == 3
    assert at_half["false_positives"] == 1
    assert at_half["false_negatives"] == 1
    assert at_half["true_negatives"] == 3
    assert at_half["recall"] == pytest.approx(0.75)
    assert at_half["specificity"] == pytest.approx(0.75)


def test_lower_threshold_never_reduces_recall() -> None:
    sweep = threshold_sweep(Y_TRUE, SCORES, steps=21).sort_values("threshold")
    recalls = sweep["recall"].to_numpy()
    assert np.all(np.diff(recalls) <= 1e-9)


def test_sensitivity_first_threshold_catches_every_positive() -> None:
    chosen = threshold_for_min_recall(Y_TRUE, SCORES, min_recall=1.0)
    assert chosen is not None
    assert chosen["recall"] == pytest.approx(1.0)
    assert chosen["false_negatives"] == 0


def test_min_recall_returns_none_when_unreachable() -> None:
    impossible = threshold_for_min_recall(Y_TRUE, np.zeros_like(SCORES), min_recall=1.0)
    assert impossible is None or impossible["recall"] >= 1.0


def test_best_f1_threshold_reports_counts_as_integers() -> None:
    best = best_f1_threshold(Y_TRUE, SCORES)
    assert isinstance(best["false_negatives"], int)
    assert 0.0 <= best["f1"] <= 1.0


def test_decision_scores_are_not_treated_as_probabilities() -> None:
    assert is_probability_like(SCORES) is True
    assert is_probability_like(np.array([-1.5, 2.0])) is False
    sweep = threshold_sweep(Y_TRUE, np.array([-2.0, -1.0, 3.0, 2.5, 0.4, -0.9, 1.2, -1.8]))
    assert sweep["threshold"].min() < 0.0


def test_saved_scores_round_trip(tmp_path) -> None:
    path = tmp_path / scores_filename("qml")
    assert path.name == "qml_test_scores.csv"
    save_test_scores(Y_TRUE, {"LR": SCORES, "SVM": SCORES - 0.5}, path)
    frame = load_test_scores(path)
    assert frame is not None
    assert set(frame["model"]) == {"LR", "SVM"}
    kinds = dict(zip(frame["model"], frame["score_kind"]))
    assert kinds["LR"] == "probability"
    assert kinds["SVM"] == "decision_score"
    assert len(frame) == 2 * len(Y_TRUE)


def test_calibration_skips_non_probability_models(tmp_path) -> None:
    scores = {"LR": SCORES, "SVM (decision)": SCORES * 10 - 5}
    assert set(brier_scores(Y_TRUE, scores)) == {"LR"}
    written = plot_calibration_curves(Y_TRUE, scores, tmp_path / "calib.png")
    assert written is not None and written.is_file()
    assert plot_calibration_curves(Y_TRUE, {"SVM": SCORES * 10 - 5}, tmp_path / "b.png") is None


def test_mismatched_score_length_is_dropped(tmp_path) -> None:
    path = tmp_path / "scores.csv"
    save_test_scores(Y_TRUE, {"good": SCORES, "bad": np.array([0.1, 0.2])}, path)
    frame = pd.read_csv(path)
    assert set(frame["model"]) == {"good"}
