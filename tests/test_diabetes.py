"""Diabetes CSV loader tests (skip if the Kaggle file is not on disk)."""

from __future__ import annotations

import pytest

from src.diabetes_data import find_diabetes_csv, load_diabetes_dataset


def test_diabetes_csv_loads_when_downloaded() -> None:
    try:
        path = find_diabetes_csv()
    except Exception:
        pytest.skip("Diabetes Kaggle CSV is not downloaded.")
    if not path.is_file():
        pytest.skip("Diabetes Kaggle CSV is not downloaded.")
    data = load_diabetes_dataset()
    assert data.n_samples > 1000
    assert data.n_features > 1
    assert set(data.target.unique()) == {0, 1}
    assert data.n_positive > 0
    assert data.n_negative > 0
