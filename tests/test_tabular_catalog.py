"""Tabular catalog keys and Phase 4 helper."""

from src.tabular_datasets import CATALOG, list_dataset_keys


def test_catalog_has_core_public_tables() -> None:
    keys = set(list_dataset_keys())
    assert {"cardio", "stroke", "heart_failure", "liver", "kidney"} <= keys
    for spec in CATALOG.values():
        assert "/" in spec.kaggle_slug
        assert spec.target_column
        assert spec.key
