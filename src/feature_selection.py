"""Train-only feature selection for near-term quantum circuits.

Fit ``SelectKBest`` on the **training** split only, then apply the same
mask to the test split. Default ``k=6`` (allowed range 4–8).

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_classif

from src.preprocessing import RANDOM_STATE
from src.utils import get_models_dir, get_reports_dir

DEFAULT_K = 6
MIN_K = 4
MAX_K = 8
SELECTOR_FILENAME = "phase2_select_kbest.joblib"
FEATURES_JSON = "phase2_selected_features.json"


def _mutual_info(x, y):
    return mutual_info_classif(x, y, random_state=RANDOM_STATE)


def fit_select_k_best(
    x_train: pd.DataFrame,
    y_train,
    *,
    k: int = DEFAULT_K,
) -> SelectKBest:
    """Fit a selector on training rows only."""
    if not MIN_K <= k <= MAX_K:
        raise ValueError(f"k must be between {MIN_K} and {MAX_K}, got {k}.")
    n_features = x_train.shape[1]
    if k > n_features:
        raise ValueError(f"k={k} is larger than the number of columns ({n_features}).")
    selector = SelectKBest(score_func=_mutual_info, k=k)
    selector.fit(x_train, y_train)
    return selector


def selected_feature_names(selector: SelectKBest, feature_names: list[str]) -> list[str]:
    """Return column names kept by the fitted selector."""
    mask = selector.get_support()
    if mask is None:
        raise RuntimeError("Selector has no support mask. Call fit first.")
    return [name for name, keep in zip(feature_names, mask) if keep]


def transform_features(selector: SelectKBest, features: pd.DataFrame) -> pd.DataFrame:
    """Apply a fitted selector and keep pandas column names."""
    names = selected_feature_names(selector, list(features.columns))
    transformed = selector.transform(features)
    return pd.DataFrame(transformed, columns=names, index=features.index)


def save_selector(
    selector: SelectKBest,
    feature_names: list[str],
    *,
    k: int,
    reports_dir: Path | None = None,
    models_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Write the selector and a JSON list of kept feature names."""
    models_dir = models_dir or get_models_dir()
    reports_dir = reports_dir or get_reports_dir()
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    selector_path = models_dir / SELECTOR_FILENAME
    joblib.dump(selector, selector_path, compress=3)

    kept = selected_feature_names(selector, feature_names)
    scores = {
        name: float(score)
        for name, score in zip(feature_names, np.asarray(selector.scores_, dtype=float))
    }
    payload = {
        "k": k,
        "score_func": "mutual_info_classif",
        "random_state": RANDOM_STATE,
        "selected_features": kept,
        "all_feature_scores": scores,
        "disclaimer": "Research risk classification - not for clinical use.",
    }
    json_path = reports_dir / FEATURES_JSON
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return selector_path, json_path


def load_selected_feature_names(json_path: Path | None = None) -> list[str]:
    """Read kept feature names from the Phase 2 JSON report."""
    path = json_path or (get_reports_dir() / FEATURES_JSON)
    if not path.is_file():
        raise FileNotFoundError(
            f"Selected-feature file not found: {path}. "
            "Run python -m src.train_phase2 first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    names = payload.get("selected_features")
    if not names:
        raise ValueError(f"No selected_features in {path}")
    return list(names)
