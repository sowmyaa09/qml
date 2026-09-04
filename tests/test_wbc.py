"""Tests for white-blood-cell image helpers (skip if images are not downloaded)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.train_wbc import multiclass_metrics
from src.wbc_data import WBC_CLASSES, find_wbc_dataset_root
from src.wbc_model import SmallWbcCnn, count_trainable_parameters


def test_small_cnn_has_about_one_million_weights() -> None:
    model = SmallWbcCnn(n_classes=5)
    n_params = count_trainable_parameters(model)
    assert 400_000 < n_params < 2_000_000


def test_multiclass_metrics_are_between_zero_and_one() -> None:
    y_true = np.array([0, 1, 2, 2, 1, 0])
    y_pred = np.array([0, 1, 1, 2, 1, 0])
    metrics = multiclass_metrics(y_true, y_pred)
    for name, value in metrics.items():
        assert 0.0 <= value <= 1.0, f"{name}={value}"


def test_wbc_folders_exist_if_dataset_is_present() -> None:
    try:
        root = find_wbc_dataset_root()
    except Exception:
        pytest.skip("WBC dataset is not downloaded on this machine.")
    assert (root / "Train").is_dir()
    assert (root / "Test-A").is_dir()
    for name in WBC_CLASSES:
        assert (root / "Train" / name).is_dir()
        assert (root / "Test-A" / name).is_dir()
    assert Path(root).exists()
