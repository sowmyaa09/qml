"""Tabular catalog keys and Phase 4 helper."""

from src.tabular_datasets import CATALOG, list_dataset_keys, load_tabular_dataset


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
        "ddd",
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


def test_ddd_vertebral_column_loads_binary() -> None:
    spec, features, target, _path = load_tabular_dataset("ddd")
    assert spec.key == "ddd"
    assert len(features) >= 300
    assert features.shape[1] == 6
    assert set(target.unique()) <= {0, 1}
    assert int(target.sum()) > 50
    assert int((1 - target).sum()) > 50
    for col in (
        "pelvic_incidence",
        "pelvic_tilt",
        "lumbar_lordosis_angle",
        "sacral_slope",
        "pelvic_radius",
        "degree_spondylolisthesis",
    ):
        assert col in features.columns
