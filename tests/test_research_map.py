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


def test_schema_prompt_can_scope_to_one_table() -> None:
    from src.research_map import schema_prompt_block

    block = schema_prompt_block("pima")
    assert "pima" in block
    assert "Glucose" in block
    assert "mean radius" not in block
    assert len(SCHEMAS["wisconsin"].features) == 30
    assert SCHEMAS["wisconsin_reduced"].min_filled == 6


def test_pasted_symptoms_are_not_a_diagnosis() -> None:
    from src.research_map import score_pasted_record

    out = score_pasted_record("wisconsin_reduced", "I have a headache and chest pain")
    assert out["refused_symptom_checker"] is True
    assert out["result"]["research_positive_percent"] is None
    assert out["extracted"] == {}


def test_pasted_record_extracts_named_fields() -> None:
    from src.research_map import score_pasted_record

    text = "mean perimeter: 92\nworst area: 880\nmean concave points: 0.05"
    out = score_pasted_record("wisconsin_reduced", text)
    assert out["refused_symptom_checker"] is False
    assert "mean perimeter" in out["extracted"]
    assert out["result"]["key"] == "wisconsin_reduced"


def test_align_row_accepts_numpy_feature_names() -> None:
    import numpy as np
    from src.research_map import _align_row

    class Fake:
        feature_names_in_ = np.array(["mean perimeter", "worst area"])

    schema = SCHEMAS["wisconsin_reduced"]
    row = _align_row(
        Fake(),
        schema,
        {"mean perimeter": 90.0, "worst area": 800.0},
        quantum=False,
    )
    assert list(row.columns) == ["mean perimeter", "worst area"]
    assert float(row.iloc[0]["mean perimeter"]) == 90.0


def test_local_extractor_reads_named_numbers() -> None:
    text = "mean radius: 14.1\nworst area = 800\nheadache yesterday"
    out = extract_catalog_fields_locally(text)
    assert "wisconsin" in out["catalog_keys"]
    assert out["features_by_key"]["wisconsin"]["mean radius"] == 14.1
    assert out["features_by_key"]["wisconsin"]["worst area"] == 800.0
    assert "flu" not in out["catalog_keys"]


def test_all_22_schemas_registered() -> None:
    expected_new = [
        "kidney", "liver", "parkinson", "thyroid", "heart_failure",
        "heart_disease", "fetal", "cervical", "pcos", "seer_breast",
        "seizure", "brfss_heart"
    ]
    assert len(SCHEMAS) >= 22
    for k in expected_new:
        assert k in SCHEMAS
        assert len(SCHEMAS[k].features) > 0
        assert SCHEMAS[k].min_filled > 0


def test_dynamic_model_discovery() -> None:
    from src.research_map import iter_scorable_model_files

    # wisconsin_reduced should find LR, RF, and at least QSVC / RBF
    wr_models = iter_scorable_model_files("wisconsin_reduced", "phase2_reduced")
    wr_names = [name for name, _ in wr_models]
    assert "Logistic Regression" in wr_names
    assert "Random Forest" in wr_names
    assert "QSVC" in wr_names

    # coimbra should find LR, RF, and QSVC
    coimbra_models = iter_scorable_model_files("coimbra", "coimbra")
    coimbra_names = [name for name, _ in coimbra_models]
    assert "Logistic Regression" in coimbra_names
    assert "Random Forest" in coimbra_names

    # kidney should find LR and RF
    kidney_models = iter_scorable_model_files("kidney", "kidney")
    kidney_names = [name for name, _ in kidney_models]
    assert "Logistic Regression" in kidney_names
    assert "Random Forest" in kidney_names


def test_score_catalog_on_new_datasets() -> None:
    from src.research_map import score_catalog

    # Test scoring kidney with partial active features
    kidney_feats = {
        "age": 48, "bp": 80, "sg": 1.020, "al": 1, "su": 0,
        "bgr": 121, "bu": 36, "sc": 1.2, "sod": 135, "pot": 4.5, "hemo": 15.4
    }
    res = score_catalog("kidney", kidney_feats)
    assert res["key"] == "kidney"
    assert res["insufficient"] is False
    assert res["research_positive_percent"] is not None
    assert len(res["models"]) >= 2


def test_extract_wisconsin_reduced_accepts_sklearn_aliases() -> None:
    text = (
        "perimeter_mean: 122.8\n"
        "concave_points_mean: 0.1471\n"
        "radius_worst: 25.38\n"
        "perimeter_worst: 184.6\n"
        "area_worst: 2019.0\n"
        "concave_points_worst: 0.2654\n"
    )
    mapped = extract_catalog_fields_locally(text)
    feats = mapped["features_by_key"]["wisconsin_reduced"]
    assert len(feats) == 6
    assert feats["mean perimeter"] == 122.8
    assert feats["worst area"] == 2019.0
