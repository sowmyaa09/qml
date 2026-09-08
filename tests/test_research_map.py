"""Research mapper: schema filter and incomplete-score behaviour."""

from __future__ import annotations

from src.catalog_schemas import SCHEMAS
from src.nvidia_client import parse_json_object
from src.research_map import (
    extract_catalog_fields_locally,
    sanitize_mapped_payload,
    score_catalog,
)


def test_parse_json_object_from_fence() -> None:
    payload = parse_json_object('```json\n{"catalog_keys": ["wisconsin"]}\n```')
    assert payload["catalog_keys"] == ["wisconsin"]


def test_assistant_text_prefers_content_then_reasoning() -> None:
    from src.nvidia_client import assistant_text

    assert assistant_text({"content": '{"a": 1}', "reasoning_content": "noise"}) == '{"a": 1}'
    assert assistant_text({"content": None, "reasoning_content": '{"a": 1}'}) == '{"a": 1}'


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


def test_local_extractor_reads_named_numbers() -> None:
    text = "mean radius: 14.1\nworst area = 800\nheadache yesterday"
    out = extract_catalog_fields_locally(text)
    assert "wisconsin" in out["catalog_keys"]
    assert out["features_by_key"]["wisconsin"]["mean radius"] == 14.1
    assert out["features_by_key"]["wisconsin"]["worst area"] == 800.0
    assert "flu" not in out["catalog_keys"]
