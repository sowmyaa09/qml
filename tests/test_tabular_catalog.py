"""Tabular catalog keys and Phase 4 helper."""

from src.tabular_datasets import CATALOG, list_dataset_keys


def test_catalog_has_core_public_tables() -> None:
    keys = set(list_dataset_keys())
    assert {"cardio", "stroke", "heart_failure", "liver", "kidney"} <= keys
    assert {
        "coimbra",
        "seizure",
        "framingham",
        "seer_breast",
        "cervical",
        "hepatitis",
        "pcos",
        "heart_uci_pooled",
        "brfss_heart",
    } <= keys
    for spec in CATALOG.values():
        assert spec.target_column
        assert spec.key
        has_source = (
            ("/" in spec.kaggle_slug)
            or spec.uci_id is not None
            or spec.zenodo_file_url
            or spec.http_urls
            or spec.pooled_urls
        )
        assert has_source, spec.key
