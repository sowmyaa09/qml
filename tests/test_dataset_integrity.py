"""Duplicate handling and multi-cohort pooling.

Public disease tables are re-uploaded constantly. A mirror that repeats its
source rows looks like "more data" but leaks the label across a random split,
so the loader must drop exact duplicates and the audit must be able to count
them.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.audit_datasets import LEAKAGE_WARN_SHARE, audit_key
from src.tabular_datasets import CATALOG, load_tabular_dataset

POOLED_KEY = "heart_uci_pooled"


def test_pooled_spec_lists_four_distinct_cohorts() -> None:
    spec = CATALOG[POOLED_KEY]
    assert len(spec.pooled_urls) == 4
    cohorts = {url.rsplit("/", 1)[-1] for url in spec.pooled_urls}
    assert len(cohorts) == 4
    # The site column must never become a feature: prevalence differs per site.
    assert "source_cohort" in spec.drop_columns
    assert len(spec.pooled_columns) == 14


def test_pooled_table_is_bigger_than_one_cohort() -> None:
    _spec, pooled, target, path = load_tabular_dataset(POOLED_KEY)
    assert path.name == "pooled.csv"
    # Cleveland alone is 303 rows; four cohorts must be substantially more.
    assert len(pooled) > 800
    assert "source_cohort" not in pooled.columns
    assert set(target.unique()) == {0, 1}


def test_loader_drops_exact_duplicates_by_default() -> None:
    _spec, deduped, _y, _path = load_tabular_dataset("heart_disease")
    _spec2, raw, _y2, _path2 = load_tabular_dataset(
        "heart_disease", drop_duplicates=False
    )
    assert len(deduped) < len(raw)
    stacked = deduped.copy()
    stacked["__t__"] = _y.to_numpy()
    assert not stacked.duplicated().any()


def test_audit_reports_the_known_duplicated_mirror() -> None:
    result = audit_key("heart_disease")
    assert result["duplicate_rows"] > 0
    assert result["duplicate_share"] > LEAKAGE_WARN_SHARE
    assert result["leakage_risk"] is True
    assert result["unique_rows"] == result["rows"] - result["duplicate_rows"]


def test_audit_flags_a_clean_table_as_safe() -> None:
    result = audit_key("coimbra")
    assert result["duplicate_rows"] == 0
    assert result["leakage_risk"] is False


def test_duplicate_share_is_a_fraction() -> None:
    result = audit_key("hepatitis")
    assert 0.0 <= result["duplicate_share"] <= 1.0


def test_pooled_urls_are_only_used_for_multi_cohort_specs() -> None:
    with_pooling = [key for key, spec in CATALOG.items() if spec.pooled_urls]
    assert with_pooling == [POOLED_KEY]
    for key, spec in CATALOG.items():
        if spec.pooled_urls:
            assert spec.pooled_columns, key
        else:
            assert not spec.pooled_columns, key


def test_brfss_heart_is_a_survey_table_not_a_kaggle_copy() -> None:
    spec = CATALOG["brfss_heart"]
    assert spec.target_column == "HeartDisease"
    assert spec.zenodo_file_url
    assert "cardio_train" in spec.notes.lower() or "not kaggle cardio" in spec.notes.lower()
    assert not spec.pooled_urls


def test_unknown_key_still_raises() -> None:
    with pytest.raises(KeyError):
        load_tabular_dataset("not_a_real_table")
