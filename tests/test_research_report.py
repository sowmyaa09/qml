"""Locked research PDF: encrypt/decrypt and API refusals."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from src.api_server import app
from src.research_report_pdf import (
    NOT_CLINICAL,
    build_locked_pdf,
    fingerprint_key,
    generate_unlock_key,
    score_band,
)
from src.supabase_store import store_unlock_key, supabase_configured
from src.utils import RESEARCH_DISCLAIMER as DISCLAIMER


def test_store_unlock_key_skips_when_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert supabase_configured() is False
    assert (
        store_unlock_key(
            catalog_key="pima",
            subject_name="Ada Example",
            date_of_birth="1991-04-02",
            unlock_key="nope",
            key_fingerprint="abc",
            research_score=1.0,
        )
        is False
    )

client = TestClient(app)

SAMPLE_RESULT = {
    "insufficient": False,
    "research_positive_percent": 55.2,
    "title": "Wisconsin reduced (Phase 2, 6 features)",
    "models": [
        {"name": "Logistic Regression", "percent": 55.2, "error": None},
        {"name": "Random Forest", "percent": 40.0, "error": None},
    ],
    "filled": ["mean perimeter"],
    "missing": [],
    "specialty_hint": (
        "Same Wisconsin benchmark, 6 selected columns for hybrid QML. "
        "See a licensed clinician for personal care. We do not name doctors."
    ),
}


def test_fingerprint_is_stable() -> None:
    key = "abc_unlock_key"
    assert fingerprint_key(key) == fingerprint_key(key)
    assert fingerprint_key(key) != fingerprint_key(key + "x")
    assert len(fingerprint_key(key)) == 64


def test_score_band_plain_language() -> None:
    assert score_band(10) == "Lower"
    assert score_band(50) == "In the middle"
    assert score_band(80) == "Higher"
    assert score_band(None) == "—"


def test_locked_pdf_needs_generated_key() -> None:
    key = generate_unlock_key()
    pdf, used = build_locked_pdf(
        subject_name="Ada Example",
        date_of_birth="1991-04-02",
        catalog_title="Wisconsin reduced",
        extracted={"mean perimeter": 122.8},
        result=SAMPLE_RESULT,
        unlock_key=key,
    )
    assert used == key
    assert pdf.startswith(b"%PDF")
    reader = PdfReader(io.BytesIO(pdf))
    assert reader.is_encrypted
    with pytest.raises(Exception):
        _ = reader.pages[0].extract_text()
    reader = PdfReader(io.BytesIO(pdf))
    assert reader.decrypt(key)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert "not for clinical" in text.lower()
    assert "not a clinical" in text.lower() or NOT_CLINICAL[:20] in text
    assert "we do not name doctors" in text.lower()
    assert "ada example" in text.lower()
    assert "1991-04-02" in text
    assert "lakshya" in text.lower()
    assert "research score sheet" in text.lower()
    assert "not a diagnosis" in text.lower()
    assert "the disease you got" in text.lower()
    assert "cannot be sure" in text.lower() or "does not claim" in text.lower()
    assert "research band" in text.lower()
    assert "insurance" not in text.lower() or "not an insurance" in text.lower()
    assert key not in text


def test_report_endpoint_refuses_symptoms() -> None:
    response = client.post(
        "/v1/research-report",
        json={
            "catalog_key": "wisconsin_reduced",
            "subject_name": "Ada Example",
            "date_of_birth": "1991-04-02",
            "text": "what disease do I have I feel fever and cough",
        },
    )
    assert response.status_code == 400


def test_report_endpoint_refuses_insufficient_fields() -> None:
    response = client.post(
        "/v1/research-report",
        json={
            "catalog_key": "wisconsin_reduced",
            "subject_name": "Ada Example",
            "date_of_birth": "1991-04-02",
            "features": {"mean perimeter": 90},
        },
    )
    assert response.status_code == 400


@patch("src.api_server.store_unlock_key", return_value=False)
@patch("src.api_server.score_pasted_record")
def test_report_endpoint_returns_encrypted_pdf(mock_score, mock_store) -> None:
    mock_score.return_value = {
        "disclaimer": DISCLAIMER,
        "extracted": {"mean perimeter": 122.8, "worst radius": 25.0},
        "refused_symptom_checker": False,
        "result": SAMPLE_RESULT,
    }
    response = client.post(
        "/v1/research-report",
        json={
            "catalog_key": "wisconsin_reduced",
            "subject_name": "Ada Example",
            "date_of_birth": "1991-04-02",
            "text": "mean perimeter: 122.8\nworst radius: 25.0",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    unlock = response.headers.get("X-Unlock-Key")
    assert unlock
    assert response.headers.get("X-Report-Stored") == "false"
    assert response.headers.get("X-Key-Fingerprint") == fingerprint_key(unlock)
    mock_store.assert_called_once()
    reader = PdfReader(io.BytesIO(response.content))
    assert reader.is_encrypted
    assert reader.decrypt(unlock)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert "not for clinical" in text.lower() or "research" in text.lower()


def test_report_endpoint_requires_name_and_dob() -> None:
    response = client.post(
        "/v1/research-report",
        json={
            "catalog_key": "wisconsin_reduced",
            "subject_name": "",
            "date_of_birth": "",
            "text": "mean perimeter: 122.8",
        },
    )
    assert response.status_code == 422
    blob = str(response.json()).lower()
    assert "name" in blob or "subject_name" in blob
    assert "date of birth" in blob or "date_of_birth" in blob
