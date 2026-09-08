"""Bootstrap intervals, McNemar, and DeLong on the held-out split."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from src.significance import (
    bootstrap_metric_ci,
    delong_roc_test,
    describe_p_value,
    labels_from_scores,
    mcnemar_test,
    paired_bootstrap_difference,
    stratified_bootstrap_indices,
)


@pytest.fixture(scope="module")
def synthetic():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, size=200)
    strong = y * 0.6 + rng.normal(0, 0.4, size=200)
    weak = y * 0.3 + rng.normal(0, 0.5, size=200)
    return y, strong, weak


def test_delong_auc_matches_sklearn(synthetic) -> None:
    y, strong, weak = synthetic
    result = delong_roc_test(y, strong, weak)
    assert result["auc_a"] == pytest.approx(roc_auc_score(y, strong), abs=1e-9)
    assert result["auc_b"] == pytest.approx(roc_auc_score(y, weak), abs=1e-9)


def test_delong_detects_a_real_auc_gap(synthetic) -> None:
    y, strong, weak = synthetic
    assert delong_roc_test(y, strong, weak)["p_value"] < 0.01


def test_delong_on_identical_scores_is_not_significant(synthetic) -> None:
    y, strong, _weak = synthetic
    result = delong_roc_test(y, strong, strong)
    assert result["auc_difference"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)


def test_mcnemar_uses_only_disagreements() -> None:
    y = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    a = np.array([1, 1, 1, 1, 0, 0, 0, 0])  # perfect
    b = np.array([0, 0, 1, 1, 0, 0, 0, 0])  # misses two positives
    result = mcnemar_test(y, a, b)
    assert result["only_a_correct"] == 2
    assert result["only_b_correct"] == 0
    assert result["discordant"] == 2
    assert result["method"] == "exact binomial"


def test_mcnemar_on_identical_predictions_is_neutral() -> None:
    y = np.array([1, 0, 1, 0])
    pred = np.array([1, 0, 0, 0])
    result = mcnemar_test(y, pred, pred)
    assert result["discordant"] == 0
    assert result["p_value"] == 1.0


def test_mcnemar_switches_to_chi_square_when_disagreements_pile_up(synthetic) -> None:
    y, strong, weak = synthetic
    result = mcnemar_test(y, (strong > 0.5).astype(int), (weak > 0.5).astype(int))
    assert result["discordant"] >= 25
    assert result["method"].startswith("chi-square")
    assert result["p_value"] < 0.05


def test_bootstrap_interval_brackets_the_point_estimate(synthetic) -> None:
    y, strong, _weak = synthetic
    pred = (strong > 0.5).astype(int)
    interval = bootstrap_metric_ci(y, pred, strong, metric="f1", n_resamples=300)
    assert interval["ci_lower"] <= interval["point"] <= interval["ci_upper"]
    assert 0.0 <= interval["ci_lower"] <= 1.0


def test_paired_difference_flags_an_indistinguishable_pair(synthetic) -> None:
    y, strong, _weak = synthetic
    pred = (strong > 0.5).astype(int)
    same = paired_bootstrap_difference(
        y, (pred, strong), (pred, strong), metric="f1", n_resamples=200
    )
    assert same["difference"] == pytest.approx(0.0)
    assert same["crosses_zero"] is True


def test_paired_difference_flags_a_real_gap(synthetic) -> None:
    y, strong, weak = synthetic
    result = paired_bootstrap_difference(
        y,
        ((strong > 0.5).astype(int), strong),
        ((weak > 0.5).astype(int), weak),
        metric="f1",
        n_resamples=300,
    )
    assert result["difference"] > 0
    assert result["crosses_zero"] is False


def test_bootstrap_keeps_both_classes_in_every_resample(synthetic) -> None:
    y, _strong, _weak = synthetic
    for index in stratified_bootstrap_indices(y, n_resamples=25):
        assert set(np.asarray(y)[index]) == {0, 1}
        assert index.size == y.size


def test_labels_from_scores_uses_the_right_cutoff() -> None:
    probabilities = np.array([0.2, 0.5, 0.9])
    assert list(labels_from_scores(probabilities, probability_like=True)) == [0, 1, 1]
    decisions = np.array([-1.0, 0.0, 2.0])
    assert list(labels_from_scores(decisions, probability_like=False)) == [0, 1, 1]


def test_p_value_wording_does_not_overclaim() -> None:
    assert "does not show a difference" in describe_p_value(0.4)
    assert "unlikely to be chance" in describe_p_value(0.001)


def test_unknown_metric_is_rejected(synthetic) -> None:
    y, strong, _weak = synthetic
    with pytest.raises(KeyError):
        bootstrap_metric_ci(y, (strong > 0.5).astype(int), strong, metric="dice")
