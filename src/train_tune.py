"""Train-only cleaning and small hyperparameter search. No test-set leakage.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from src.preprocessing import RANDOM_STATE


class QuantileClipper(BaseEstimator, TransformerMixin):
    """Winsorize continuous columns at train percentiles, as a pipeline step.

    Same rule as :func:`clip_numeric_by_train_quantiles`, but usable inside a
    ``Pipeline`` so cross-validation folds cannot leak their own quantiles.
    """

    def __init__(self, lower: float = 0.01, upper: float = 0.99):
        self.lower = lower
        self.upper = upper

    def fit(self, X, y=None):
        frame = pd.DataFrame(X)
        self.n_features_in_ = frame.shape[1]
        lows: list[float] = []
        highs: list[float] = []
        for column in frame.columns:
            series = pd.to_numeric(frame[column], errors="coerce")
            if series.nunique(dropna=True) <= 2:
                lows.append(-np.inf)
                highs.append(np.inf)
                continue
            low = series.quantile(self.lower)
            high = series.quantile(self.upper)
            if pd.isna(low) or pd.isna(high) or low >= high:
                lows.append(-np.inf)
                highs.append(np.inf)
            else:
                lows.append(float(low))
                highs.append(float(high))
        self.lower_bounds_ = np.asarray(lows, dtype=float)
        self.upper_bounds_ = np.asarray(highs, dtype=float)
        return self

    def transform(self, X):
        values = pd.DataFrame(X).apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        return np.clip(values, self.lower_bounds_, self.upper_bounds_)


def clip_numeric_by_train_quantiles(x_train, x_test, *, lower: float = 0.01, upper: float = 0.99):
    """Winsorize continuous columns using **train** percentiles only."""
    train = x_train.copy()
    test = x_test.copy()
    for col in train.columns:
        series = pd.to_numeric(train[col], errors="coerce")
        if series.nunique(dropna=True) <= 2:
            continue
        lo = series.quantile(lower)
        hi = series.quantile(upper)
        if pd.isna(lo) or pd.isna(hi) or lo >= hi:
            continue
        train[col] = pd.to_numeric(train[col], errors="coerce").clip(lo, hi)
        test[col] = pd.to_numeric(test[col], errors="coerce").clip(lo, hi)
    return train, test


def should_grid_search(n_rows: int, n_features: int) -> bool:
    """Skip expensive CV on huge tables (cardio, seizure)."""
    if n_rows < 80:
        return False
    if n_rows > 8000:
        return False
    if n_rows * n_features > 250_000:
        return False
    return True


def fit_with_optional_search(estimator, param_grid, x_train, y_train, *, scoring: str = "f1"):
    """Fit ``estimator``, or GridSearchCV on the training split only."""
    y = np.asarray(y_train)
    counts = np.bincount(y) if y.size and y.min() >= 0 else np.array([0])
    min_class = int(counts.min()) if counts.size else 0
    n_splits = min(5, min_class)
    if (
        param_grid
        and should_grid_search(len(y), np.asarray(x_train).shape[1])
        and n_splits >= 2
    ):
        search = GridSearchCV(
            estimator,
            param_grid,
            cv=StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE),
            scoring=scoring,
            n_jobs=-1,
            refit=True,
        )
        search.fit(x_train, y_train)
        print(f"  CV best {scoring}={search.best_score_:.4f} params={search.best_params_}", flush=True)
        return search.best_estimator_
    estimator.fit(x_train, y_train)
    return estimator
