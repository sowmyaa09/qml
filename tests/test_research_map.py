"""Research mapper: schema filter and incomplete-score behaviour."""

from __future__ import annotations

from src.catalog_schemas import SCHEMAS
from src.nvidia_client import parse_json_object
from src.research_map import sanitize_mapped_payload, score_catalog


def test_parse_json_object_from_fence() -> None:
    payload = parse_json_object('```json\n{"catalog_keys": ["wisconsin"]}\n```')
    assert payload["catalog_keys"] == ["wisconsin"]


def test_sanitize_drops_unknown_disease_keys() -> None:
    raw = {
        "catalog_keys": ["wisconsin", "flu", "ebola"],
        "features_by_key": {
            "wisconsin": {"mean radius": 14.0, "not a real column": 1},
            "flu": {"cough": 1},
        },
        "unmapped_phrases": ["headache"],
    }
    out = sanitize_mapped_payload(raw)
    assert "flu" not in out["catalog_keys"]
    assert "ebola" not in out["catalog_keys"]
    assert out["catalog_keys"] == ["wisconsin"]
    assert out["features_by_key"]["wisconsin"] == {"mean radius": 14.0}
    assert "headache" in out["unmapped_phrases"]
    assert "diagnosis" not in out["disclaimer"].lower() or "not for clinical" in out["disclaimer"].lower()


def test_score_insufficient_fields_has_no_percent() -> None:
    result = score_catalog("wisconsin", {"mean radius": 14.0})
    assert result["insufficient"] is True
    assert result["research_positive_percent"] is None
    assert "Insufficient" in result["message"]
    assert result["coverage_percent"] < 20
    assert "mean texture" in result["missing"]


def test_wisconsin_schema_has_thirty_features() -> None:
    assert len(SCHEMAS["wisconsin"].features) == 30
    assert SCHEMAS["wisconsin_reduced"].min_filled == 6
