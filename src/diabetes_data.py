"""Load the public CDC BRFSS diabetes health indicators table from Kaggle.

Binary label: 1 = diabetes (survey indicator), 0 = no diabetes.
Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DIABETES_KAGGLE_SLUG = "alexteboul/diabetes-health-indicators-dataset"
DIABETES_CSV_NAME = "diabetes_binary_health_indicators_BRFSS2015.csv"
TARGET_COLUMN = "Diabetes_binary"


@dataclass(frozen=True)
class DiabetesSurveyData:
    """Numeric features and binary survey diabetes label."""

    features: pd.DataFrame
    target: pd.Series
    source_path: Path
    n_samples: int
    n_features: int
    n_positive: int
    n_negative: int


def find_diabetes_csv() -> Path:
    """Return the diabetes CSV in KaggleHub cache, downloading if needed."""
    cache_hit = (
        Path.home()
        / ".cache"
        / "kagglehub"
        / "datasets"
        / "alexteboul"
        / "diabetes-health-indicators-dataset"
        / "versions"
        / "1"
        / DIABETES_CSV_NAME
    )
    if cache_hit.is_file():
        return cache_hit

    try:
        import kagglehub
    except ImportError as exc:
        raise FileNotFoundError(
            f"Diabetes CSV not found at {cache_hit} and kagglehub is not installed. "
            "Run: pip install kagglehub"
        ) from exc

    folder = Path(kagglehub.dataset_download(DIABETES_KAGGLE_SLUG))
    path = folder / DIABETES_CSV_NAME
    if not path.is_file():
        raise FileNotFoundError(
            f"Expected {DIABETES_CSV_NAME} under {folder}."
        )
    return path


def load_diabetes_dataset() -> DiabetesSurveyData:
    """Load the binary diabetes survey table (public BRFSS-derived data)."""
    path = find_diabetes_csv()
    frame = pd.read_csv(path)
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(
            f"Column {TARGET_COLUMN!r} is missing. Found: {list(frame.columns)}"
        )
    target = frame[TARGET_COLUMN].astype(int)
    features = frame.drop(columns=[TARGET_COLUMN])
    if set(target.unique()) - {0, 1}:
        raise ValueError("Diabetes_binary must contain only 0 and 1.")
    n_positive = int((target == 1).sum())
    n_negative = int((target == 0).sum())
    return DiabetesSurveyData(
        features=features,
        target=target,
        source_path=path,
        n_samples=int(len(frame)),
        n_features=int(features.shape[1]),
        n_positive=n_positive,
        n_negative=n_negative,
    )


def inspect_diabetes_dataset(data: DiabetesSurveyData) -> str:
    """Beginner-friendly summary of the diabetes survey table."""
    return "\n".join(
        [
            "Dataset: CDC BRFSS diabetes health indicators (Kaggle / public survey)",
            f"File: {data.source_path}",
            f"Rows: {data.n_samples}",
            f"Feature columns: {data.n_features}",
            f"Diabetes present (1): {data.n_positive}",
            f"Diabetes absent (0): {data.n_negative}",
            "Research risk classification - not for clinical use.",
            "This is a survey label, not a medical diagnosis.",
        ]
    )
