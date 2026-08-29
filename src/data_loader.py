"""Load the public Wisconsin Diagnostic Breast Cancer dataset.

sklearn originally uses:
  0 = malignant, 1 = benign

This project converts labels so that:
  1 = malignant / disease present  (positive class)
  0 = benign / disease absent
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.datasets import load_breast_cancer


@dataclass(frozen=True)
class BreastCancerData:
    """Container for features, converted labels, and a short description."""

    features: pd.DataFrame
    target: pd.Series
    feature_names: list[str]
    n_samples: int
    n_features: int
    n_malignant: int
    n_benign: int


def load_breast_cancer_dataset() -> BreastCancerData:
    """Load sklearn's built-in breast cancer data and relabel the target.

    Returns
    -------
    BreastCancerData
        Features ``X`` and binary target ``y`` (1 = malignant).

    Raises
    ------
    RuntimeError
        If the dataset cannot be loaded or has the wrong shape.
    """
    try:
        raw = load_breast_cancer(as_frame=True)
    except Exception as exc:  # pragma: no cover - sklearn should always work
        raise RuntimeError(
            "Could not load the sklearn breast cancer dataset. "
            "Check that scikit-learn is installed (`pip install scikit-learn`)."
        ) from exc

    features = raw.data
    # Original: 0 = malignant, 1 = benign. We want 1 = malignant.
    target = (raw.target == 0).astype(int)
    target.name = "malignant"

    if features.shape[1] != 30:
        raise RuntimeError(
            f"Expected 30 features, found {features.shape[1]}. "
            "The sklearn dataset may have changed."
        )
    if set(target.unique()) - {0, 1}:
        raise RuntimeError("Target labels must be only 0 and 1 after conversion.")

    n_malignant = int((target == 1).sum())
    n_benign = int((target == 0).sum())

    return BreastCancerData(
        features=features,
        target=target,
        feature_names=list(features.columns),
        n_samples=int(features.shape[0]),
        n_features=int(features.shape[1]),
        n_malignant=n_malignant,
        n_benign=n_benign,
    )


def inspect_dataset(data: BreastCancerData) -> str:
    """Build a beginner-friendly text summary of the loaded dataset."""
    lines = [
        "Dataset: Wisconsin Diagnostic Breast Cancer (sklearn, public benchmark)",
        f"Rows (samples): {data.n_samples}",
        f"Columns (features): {data.n_features}",
        f"Malignant (positive class = 1): {data.n_malignant}",
        f"Benign (negative class = 0): {data.n_benign}",
        "All features are numeric. There are no patient names or hospital IDs.",
        "This is research data only - not for clinical use.",
    ]
    return "\n".join(lines)


def print_dataset_inspection(data: BreastCancerData) -> None:
    """Print the dataset summary to the terminal."""
    print(inspect_dataset(data))
    print(f"First feature names: {', '.join(data.feature_names[:5])}, ...")
