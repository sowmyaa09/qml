"""API serves the HTML UI and scores saved models."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api_server import app
from src.catalog_schemas import SCHEMAS
from src.utils import get_project_root


client = TestClient(app)


def test_health_and_cors_headers() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "not for clinical" in response.json()["disclaimer"].lower()


def test_qml_cost_latency_dashboard() -> None:
    response = client.get("/v1/qml-cost-latency")
    assert response.status_code == 200
    body = response.json()
    assert "ablation" in body
    assert len(body["ablation"]) >= 4
    assert body["insight"].get("latency_ratio", 0) >= 1
    assert "not for clinical" in body["disclaimer"].lower()


def test_catalog_includes_ui_tables_and_sliders() -> None:
    response = client.get("/v1/catalog")
    assert response.status_code == 200
    body = response.json()
    assert "wisconsin_reduced" in body["ui_tables"]
    keys = {row["key"] for row in body["tables"]}
    assert "pima" in keys
    assert "heart_uci_pooled" in keys
    reduced = next(row for row in body["tables"] if row["key"] == "wisconsin_reduced")
    assert len(reduced["sliders"]) == 6
    assert reduced["min_filled"] == 6
    assert "do not name doctors" in reduced["specialty_hint"].lower()


def test_legacy_static_ui_removed() -> None:
    root = get_project_root()
    assert not (root / "app.js").is_file()
    assert not (root / "styles.css").is_file()
    assert not (root / "stitch_assets").exists()
    assert not (root / "index.html").is_file()


def test_frontend_index_is_served() -> None:
    dist = get_project_root() / "stitchfrontend" / "dist" / "index.html"
    if not dist.is_file():
        pytest.skip("stitchfrontend not built (npm run build)")
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert b"LAKSHYA" in response.content
    js = None
    for token in response.text.split('"'):
        if token.startswith("/assets/") and token.endswith(".js"):
            js = token
            break
    assert js
    asset = client.get(js)
    assert asset.status_code == 200
    assert len(asset.content) > 1000


def test_score_insufficient_fields_has_no_percent() -> None:
    response = client.post(
        "/v1/research-score",
        json={"catalog_key": "wisconsin", "features": {"mean radius": 14.0}},
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["insufficient"] is True
    assert result["research_positive_percent"] is None


def test_interview_endpoint_explains_headache() -> None:
    response = client.post(
        "/v1/interview",
        json={"catalog_key": "pima", "features": {}, "last_text": "I have a headache"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["field"] == "Pregnancies"
    assert "not columns" in body["notice"].lower()


def test_record_endpoint_refuses_symptom_text() -> None:
    response = client.post(
        "/v1/research-record",
        json={
            "catalog_key": "wisconsin_reduced",
            "text": "what disease do I have I feel fever and cough",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["refused_symptom_checker"] is True
    assert body["result"]["research_positive_percent"] is None


def test_score_accepts_features_without_catalog_key() -> None:
    response = client.post("/v1/research-score", json={"features": {}})
    assert response.status_code == 200
    assert response.json()["result"]["key"] == "wisconsin_reduced"


def test_new_schemas_are_registered() -> None:
    assert "pima" in SCHEMAS
    assert len(SCHEMAS["heart_uci_pooled"].features) == 13
