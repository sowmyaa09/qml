"""Is the quantum-vs-classical gap real, or is it noise on 114 test rows?

Three tools, all paired on the **same** held-out rows:

* stratified bootstrap confidence intervals for a single model's metric,
* the paired bootstrap CI of a metric **difference** between two models,
* McNemar (paired hard predictions) and DeLong (paired ROC-AUC).

A p-value here is a statement about one public test split, not about clinical
performance.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binomtest, chi2, norm
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.preprocessing import RANDOM_STATE

DEFAULT_RESAMPLES = 2000

# 0.5 for probabilities, 0.0 for decision scores. Matches how each estimator's
# own ``predict`` turns its score into a label.
PROBABILITY_CUTOFF = 0.5
DECISION_CUTOFF = 0.0


def _specificity(y_true, y_pred) -> float:
    tn, fp, _fn, _tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return float(tn / (tn + fp)) if (tn + fp) else 0.0


METRICS = {
    "f1": lambda t, p, s: float(f1_score(t, p, zero_division=0)),
    "recall": lambda t, p, s: float(recall_score(t, p, zero_division=0)),
    "precision": lambda t, p, s: float(precision_score(t, p, zero_division=0)),
    "specificity": lambda t, p, s: _specificity(t, p),
    "accuracy": lambda t, p, s: float(accuracy_score(t, p)),
    "roc_auc": lambda t, p, s: float(roc_auc_score(t, s)),
}


def labels_from_scores(scores, *, probability_like: bool) -> np.ndarray:
    """Reproduce an estimator's hard predictions from its saved scores."""
    cutoff = PROBABILITY_CUTOFF if probability_like else DECISION_CUTOFF
    return (np.asarray(scores, dtype=float) >= cutoff).astype(int)


def stratified_bootstrap_indices(
    y_true,
    *,
    n_resamples: int = DEFAULT_RESAMPLES,
    random_state: int = RANDOM_STATE,
) -> list[np.ndarray]:
    """Resample within each class so no draw loses a class entirely."""
    truth = np.asarray(y_true).astype(int)
    positives = np.flatnonzero(truth == 1)
    negatives = np.flatnonzero(truth == 0)
    if positives.size == 0 or negatives.size == 0:
        raise ValueError("Bootstrap needs both classes in the held-out rows.")
    rng = np.random.default_rng(random_state)
    draws = []
    for _ in range(int(n_resamples)):
        draws.append(
            np.concatenate(
                [
                    rng.choice(positives, positives.size, replace=True),
                    rng.choice(negatives, negatives.size, replace=True),
                ]
            )
        )
    return draws


def bootstrap_metric_ci(
    y_true,
    y_pred,
    y_score,
    *,
    metric: str = "f1",
    n_resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
    random_state: int = RANDOM_STATE,
) -> dict[str, float]:
    """Percentile confidence interval for one model's metric on this split."""
    if metric not in METRICS:
        raise KeyError(f"Unknown metric {metric!r}. Options: {sorted(METRICS)}")
    scorer = METRICS[metric]
    truth = np.asarray(y_true).astype(int)
    pred = np.asarray(y_pred).astype(int)
    score = np.asarray(y_score, dtype=float)

    point = scorer(truth, pred, score)
    values = []
    for index in stratified_bootstrap_indices(
        truth, n_resamples=n_resamples, random_state=random_state
    ):
        try:
            values.append(scorer(truth[index], pred[index], score[index]))
        except ValueError:
            continue
    array = np.asarray(values, dtype=float)
    return {
        "metric": metric,
        "point": float(point),
        "ci_lower": float(np.quantile(array, alpha / 2)),
        "ci_upper": float(np.quantile(array, 1 - alpha / 2)),
        "n_resamples": int(array.size),
    }


def paired_bootstrap_difference(
    y_true,
    first: tuple,
    second: tuple,
    *,
    metric: str = "f1",
    n_resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
    random_state: int = RANDOM_STATE,
) -> dict[str, float]:
    """CI for ``metric(first) - metric(second)`` using the same resamples.

    ``first`` and ``second`` are ``(predictions, scores)`` tuples. Sharing the
    resample indices is what makes the comparison paired: it cancels the
    row-to-row luck that both models saw.
    """
    scorer = METRICS[metric]
    truth = np.asarray(y_true).astype(int)
    pred_a, score_a = np.asarray(first[0]).astype(int), np.asarray(first[1], dtype=float)
    pred_b, score_b = np.asarray(second[0]).astype(int), np.asarray(second[1], dtype=float)

    observed = scorer(truth, pred_a, score_a) - scorer(truth, pred_b, score_b)
    differences = []
    for index in stratified_bootstrap_indices(
        truth, n_resamples=n_resamples, random_state=random_state
    ):
        try:
            differences.append(
                scorer(truth[index], pred_a[index], score_a[index])
                - scorer(truth[index], pred_b[index], score_b[index])
            )
        except ValueError:
            continue
    array = np.asarray(differences, dtype=float)
    lower = float(np.quantile(array, alpha / 2))
    upper = float(np.quantile(array, 1 - alpha / 2))
    return {
        "metric": metric,
        "difference": float(observed),
        "ci_lower": lower,
        "ci_upper": upper,
        "crosses_zero": bool(lower <= 0.0 <= upper),
        "n_resamples": int(array.size),
    }


def mcnemar_test(y_true, pred_a, pred_b, *, exact_below: int = 25) -> dict:
    """McNemar's paired test on hard predictions from the same rows.

    Only the disagreements matter: ``b`` rows where A alone is right and ``c``
    rows where B alone is right.
    """
    truth = np.asarray(y_true).astype(int)
    correct_a = np.asarray(pred_a).astype(int) == truth
    correct_b = np.asarray(pred_b).astype(int) == truth
    only_a = int(np.sum(correct_a & ~correct_b))
    only_b = int(np.sum(~correct_a & correct_b))
    discordant = only_a + only_b

    if discordant == 0:
        return {
            "only_a_correct": 0,
            "only_b_correct": 0,
            "discordant": 0,
            "statistic": 0.0,
            "p_value": 1.0,
            "method": "no disagreements",
        }
    if discordant < int(exact_below):
        return {
            "only_a_correct": only_a,
            "only_b_correct": only_b,
            "discordant": discordant,
            "statistic": float(min(only_a, only_b)),
            "p_value": float(binomtest(only_a, discordant, 0.5).pvalue),
            "method": "exact binomial",
        }
    statistic = (abs(only_a - only_b) - 1.0) ** 2 / discordant
    return {
        "only_a_correct": only_a,
        "only_b_correct": only_b,
        "discordant": discordant,
        "statistic": float(statistic),
        "p_value": float(chi2.sf(statistic, 1)),
        "method": "chi-square with continuity correction",
    }


def _midrank(x: np.ndarray) -> np.ndarray:
    """Mid-ranks, so ties share the average rank (DeLong needs this)."""
    order = np.argsort(x, kind="stable")
    sorted_x = x[order]
    n = sorted_x.size
    ranks = np.zeros(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and sorted_x[j] == sorted_x[i]:
            j += 1
        ranks[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    out = np.empty(n, dtype=float)
    out[order] = ranks
    return out


def _fast_delong(scores_positive_first: np.ndarray, n_positive: int):
    """Fast DeLong AUC covariance (Sun & Xu, 2014). Rows are models."""
    m = int(n_positive)
    n = scores_positive_first.shape[1] - m
    if m < 2 or n < 2:
        raise ValueError("DeLong needs at least two rows in each class.")
    positives = scores_positive_first[:, :m]
    negatives = scores_positive_first[:, m:]
    k = scores_positive_first.shape[0]

    tx = np.empty((k, m), dtype=float)
    ty = np.empty((k, n), dtype=float)
    tz = np.empty((k, m + n), dtype=float)
    for row in range(k):
        tx[row] = _midrank(positives[row])
        ty[row] = _midrank(negatives[row])
        tz[row] = _midrank(scores_positive_first[row])

    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    covariance = np.cov(v01) / m + np.cov(v10) / n
    return aucs, np.atleast_2d(covariance)


def delong_roc_test(y_true, score_a, score_b) -> dict:
    """Two-sided DeLong test for two correlated ROC-AUCs on the same rows."""
    truth = np.asarray(y_true).astype(int)
    order = np.argsort(-truth, kind="stable")  # positives first
    stacked = np.vstack(
        (np.asarray(score_a, dtype=float), np.asarray(score_b, dtype=float))
    )[:, order]
    aucs, covariance = _fast_delong(stacked, int(truth.sum()))

    contrast = np.array([[1.0, -1.0]])
    variance = float((contrast @ covariance @ contrast.T).item())
    difference = float(aucs[0] - aucs[1])
    if variance <= 0.0:
        return {
            "auc_a": float(aucs[0]),
            "auc_b": float(aucs[1]),
            "auc_difference": difference,
            "z": 0.0,
            "p_value": 1.0,
            "method": "DeLong (zero variance; scores are effectively identical)",
        }
    z = difference / np.sqrt(variance)
    return {
        "auc_a": float(aucs[0]),
        "auc_b": float(aucs[1]),
        "auc_difference": difference,
        "z": float(z),
        "p_value": float(2.0 * norm.sf(abs(z))),
        "method": "DeLong",
    }


def describe_p_value(p_value: float, *, alpha: float = 0.05) -> str:
    """Plain-language reading that does not overclaim."""
    if p_value >= alpha:
        return (
            f"p = {p_value:.3f}: this split does not show a difference. Treat the "
            "two models as indistinguishable here."
        )
    return (
        f"p = {p_value:.3f}: the difference on this split is unlikely to be chance "
        "alone. It is still one split of one public table."
    )
