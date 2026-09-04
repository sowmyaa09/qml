"""Map notes to catalog fields and score saved models when fields suffice.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.catalog_schemas import ALLOWED_KEYS, SCHEMAS, CatalogSchema
from src.utils import RESEARCH_DISCLAIMER, get_models_dir

SYSTEM_PROMPT = """You extract numbers and flags for a RESEARCH machine-learning catalog.
You are not a doctor. Do not diagnose. Do not invent diseases outside the allowed keys.
Allowed catalog keys only: wisconsin, wisconsin_reduced, diabetes, cardio, stroke.
Return a single JSON object with this shape:
{
  "catalog_keys": ["wisconsin"],
  "features_by_key": {
    "wisconsin": {"mean radius": 14.1, "worst area": 800.0}
  },
  "unmapped_phrases": ["headache"]
}
Rules:
- Only include keys from the allowed list.
- Only include feature names that appear in the user schema list.
- Use numbers or 0/1 for binary survey flags. Omit unknown fields.
- Do not output a disease probability. Do not name doctors.
- If the text is unrelated, return empty catalog_keys and list unmapped_phrases.
"""


def extract_pdf_text(data: bytes) -> str:
    """Pull text from a PDF. Empty string if the file is a scan without text."""
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def schema_prompt_block() -> str:
    lines = ["Feature names per catalog key:"]
    for key, schema in SCHEMAS.items():
        lines.append(f"- {key}: {', '.join(schema.features)}")
    return "\n".join(lines)


def map_notes_with_llm(text: str) -> dict[str, Any]:
    """Call NVIDIA NIM and keep only allowed keys/features."""
    from src.nvidia_client import complete_json

    user = (
        schema_prompt_block()
        + "\n\nNotes to extract (research only, not a patient chart):\n"
        + text.strip()
    )
    raw = complete_json(SYSTEM_PROMPT, user)
    return sanitize_mapped_payload(raw)


def sanitize_mapped_payload(raw: dict[str, Any]) -> dict[str, Any]:
    keys_in = raw.get("catalog_keys") or []
    if not isinstance(keys_in, list):
        keys_in = []
    feats_in = raw.get("features_by_key") or {}
    if not isinstance(feats_in, dict):
        feats_in = {}

    keys: list[str] = []
    for item in keys_in:
        key = str(item)
        if key in ALLOWED_KEYS and key not in keys:
            keys.append(key)
    for key in feats_in:
        if key in ALLOWED_KEYS and key not in keys:
            keys.append(key)

    features_by_key: dict[str, dict[str, Any]] = {}
    for key in keys:
        schema = SCHEMAS[key]
        blob = feats_in.get(key) or {}
        if not isinstance(blob, dict):
            blob = {}
        allowed = {name.lower(): name for name in schema.features}
        cleaned: dict[str, Any] = {}
        for fname, value in blob.items():
            canon = allowed.get(str(fname).strip().lower())
            if canon is None or not _present(value):
                continue
            cleaned[canon] = value
        features_by_key[key] = cleaned

    unmapped = raw.get("unmapped_phrases") or []
    if not isinstance(unmapped, list):
        unmapped = []
    unmapped_clean = [str(p) for p in unmapped if str(p).strip()]
    return {
        "catalog_keys": keys,
        "features_by_key": features_by_key,
        "unmapped_phrases": unmapped_clean,
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def coverage_for(schema: CatalogSchema, features: dict[str, Any]) -> dict[str, Any]:
    filled = [name for name in schema.features if _present(features.get(name))]
    missing = [name for name in schema.features if not _present(features.get(name))]
    n = len(schema.features)
    coverage = 100.0 * len(filled) / n if n else 0.0
    runnable = len(filled) >= schema.min_filled
    return {
        "filled": filled,
        "missing": missing,
        "coverage_percent": round(coverage, 1),
        "min_filled": schema.min_filled,
        "runnable": runnable,
    }


def _present(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, float) and np.isnan(value):
        return False
    return True


def _model_paths(prefix: str) -> list:
    models_dir = get_models_dir()
    if prefix:
        return [
            models_dir / f"{prefix}_logistic_regression_model.joblib",
            models_dir / f"{prefix}_random_forest_model.joblib",
        ]
    return [
        models_dir / "logistic_regression_model.joblib",
        models_dir / "random_forest_model.joblib",
    ]


def score_catalog(key: str, features: dict[str, Any]) -> dict[str, Any]:
    """Run a saved model if enough schema fields are present. No LLM probability."""
    if key not in SCHEMAS:
        raise KeyError(f"Unknown catalog key {key!r}")
    schema = SCHEMAS[key]
    cov = coverage_for(schema, features)
    base = {
        "key": key,
        "title": schema.title,
        "positive_label": schema.positive_label,
        "specialty_hint": schema.specialty_hint,
        "notes": schema.notes,
        "disclaimer": RESEARCH_DISCLAIMER,
        "research_positive_percent": None,
        "model_used": None,
        "insufficient": not cov["runnable"],
        **cov,
    }
    if not cov["runnable"]:
        base["message"] = "Insufficient fields — no %."
        return base

    model = None
    model_path = None
    for path in _model_paths(schema.model_prefix):
        if path.is_file():
            model = joblib.load(path)
            model_path = path
            break
    if model is None:
        base["insufficient"] = True
        base["message"] = (
            f"No saved model for {key}. Train it first "
            f"(prefix={schema.model_prefix or 'wisconsin'})."
        )
        return base

    row = _align_row(model, schema, features)
    if row is None:
        base["insufficient"] = True
        base["research_positive_percent"] = None
        base["message"] = "Could not align columns to the saved model."
        return base
    if not hasattr(model, "predict_proba"):
        raise RuntimeError("Saved model has no predict_proba.")
    proba = model.predict_proba(row)
    positive = float(np.asarray(proba)[0, 1])
    base["research_positive_percent"] = round(100.0 * positive, 1)
    base["model_used"] = model_path.name if model_path else type(model).__name__
    base["message"] = (
        "Research positive-class probability for this public table (not a diagnosis)."
    )
    return base


def _align_row(model, schema: CatalogSchema, features: dict[str, Any]) -> pd.DataFrame | None:
    names = list(getattr(model, "feature_names_in_", []) or [])
    if names:
        frame = pd.DataFrame([{k: features.get(k) for k in schema.features}])
        if schema.key == "stroke":
            frame = pd.get_dummies(frame, drop_first=True)
        frame = frame.apply(pd.to_numeric, errors="coerce")
        aligned = frame.reindex(columns=names)
        if aligned.isna().any().any():
            # Dummy columns can be 0 if that category is absent.
            aligned = aligned.fillna(0)
        return aligned
    # Wisconsin sklearn pipeline: order = schema.features
    values = []
    for name in schema.features:
        if not _present(features.get(name)):
            return None
        try:
            values.append(float(features[name]))
        except (TypeError, ValueError):
            return None
    return pd.DataFrame([values], columns=list(schema.features))


def map_and_score(text: str, *, mapped: dict[str, Any] | None = None) -> dict[str, Any]:
    """LLM map (or reuse mapped JSON) then score each catalog key."""
    payload = mapped if mapped is not None else map_notes_with_llm(text)
    results = []
    feats = payload.get("features_by_key") or {}
    keys = list(payload.get("catalog_keys") or [])
    if not keys:
        keys = [k for k, blob in feats.items() if blob]
    for key in keys:
        if key not in SCHEMAS:
            continue
        results.append(score_catalog(key, feats.get(key) or {}))
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "unmapped_phrases": payload.get("unmapped_phrases") or [],
        "results": results,
        "consultancy": (
            "See a licensed clinician in your area if you need care. "
            "This tool does not recommend named doctors, rankings, or treatment."
        ),
    }
