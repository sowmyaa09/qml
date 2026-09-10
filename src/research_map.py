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

import re

from src.catalog_schemas import (
    ALLOWED_KEYS,
    FEATURE_NAME_ALIASES,
    SCHEMAS,
    CatalogSchema,
    resolve_catalog_key,
)
from src.nvidia_client import NvidiaChatError, NvidiaConfigError
from src.utils import RESEARCH_DISCLAIMER, get_models_dir

SYSTEM_PROMPT = """You extract numbers and flags for a RESEARCH machine-learning catalog.
You are not a doctor. Do not diagnose. Do not invent diseases outside the allowed keys.
Allowed catalog keys only: wisconsin, wisconsin_reduced, diabetes, cardio, stroke, coimbra, framingham, hepatitis, pima, heart_uci_pooled, ddd.
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
- Conversational phrasing is allowed when a number is present
  (example: "I am 54 years old" may fill age/Age).
- NEVER invent a lab, FNA, or survey value that is not in the notes.
- NEVER fill fields from symptoms such as pain, tiredness, or cough.
- Do not output a disease probability. Do not name doctors.
- If the text is only symptoms with no numbers, return empty catalog_keys
  and list those phrases in unmapped_phrases.
"""


def extract_pdf_text(data: bytes) -> str:
    """Pull text from a PDF. Empty string if the file is a scan without text."""
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def schema_prompt_block(catalog_key: str | None = None) -> str:
    if catalog_key:
        if catalog_key not in SCHEMAS:
            raise KeyError(f"Unknown catalog key {catalog_key!r}")
        schema = SCHEMAS[catalog_key]
        return (
            f"Extract fields only for catalog key `{catalog_key}` ({schema.title}).\n"
            f"Allowed feature names: {', '.join(schema.features)}\n"
            "Do not include any other catalog key."
        )
    lines = ["Feature names per catalog key:"]
    for key, schema in SCHEMAS.items():
        lines.append(f"- {key}: {', '.join(schema.features)}")
    return "\n".join(lines)


def extract_catalog_fields_locally(text: str) -> dict[str, Any]:
    """Regex field grabber when NIM is unavailable. No diagnosis, no %."""
    features_by_key: dict[str, dict[str, Any]] = {}
    for key, schema in SCHEMAS.items():
        cleaned: dict[str, Any] = {}
        for name in schema.features:
            aliases = FEATURE_NAME_ALIASES.get(name, ())
            match = None
            for candidate in (name, *aliases):
                pattern = re.compile(
                    rf"{re.escape(candidate)}\s*[:=]\s*(-?\d+(?:\.\d+)?)",
                    re.IGNORECASE,
                )
                match = pattern.search(text)
                if match:
                    break
            if not match:
                continue
            number = float(match.group(1))
            if number.is_integer() and abs(number) <= 1 and name[:1].isupper():
                cleaned[name] = int(number)
            else:
                cleaned[name] = number
        if cleaned:
            features_by_key[key] = cleaned
    leftover = []
    if not features_by_key:
        leftover = [line.strip() for line in text.splitlines() if line.strip()][:8]
    return sanitize_mapped_payload(
        {
            "catalog_keys": list(features_by_key),
            "features_by_key": features_by_key,
            "unmapped_phrases": leftover,
        }
    )


_SYMPTOM_HINT = re.compile(
    r"\b(pain|fever|cough|headache|nausea|symptom|dizzy|vomit|"
    r"i have|i feel|what disease|which disease)\b",
    re.IGNORECASE,
)

_SIMULATOR_KEYS = frozenset(
    {"radius_mean", "concavity_mean", "texture_mean", "perimeter_mean"}
)


def canonical_feature_name(schema: CatalogSchema, fname: str) -> str | None:
    """Map pasted JSON/CSV keys onto this table’s schema names."""
    raw = str(fname).strip()
    lower = raw.lower()
    spaced = lower.replace("_", " ")
    allowed = {name.lower(): name for name in schema.features}
    if lower in allowed:
        return allowed[lower]
    if spaced in allowed:
        return allowed[spaced]
    for canon in schema.features:
        if lower == canon.lower().replace(" ", "_"):
            return canon
        aliases = FEATURE_NAME_ALIASES.get(canon, ())
        if lower in aliases or spaced in {a.replace("_", " ") for a in aliases}:
            return canon
    return None


def _looks_like_simulator_json(raw: str) -> bool:
    try:
        blob = json.loads(raw)
    except json.JSONDecodeError:
        return False
    if isinstance(blob, dict) and isinstance(blob.get("features"), dict):
        blob = blob["features"]
    if not isinstance(blob, dict):
        return False
    keys = {str(k).strip().lower() for k in blob}
    return bool(keys) and keys <= _SIMULATOR_KEYS


def score_pasted_record(key: str, text: str) -> dict[str, Any]:
    """Score one catalog table from pasted `field: number` lines or JSON.

    Free-text symptoms are not a diagnosis source. If no schema fields are
    found, no multi-disease ranking is invented.
    """
    if key not in SCHEMAS:
        raise KeyError(f"Unknown catalog key {key!r}")
    raw = (text or "").strip()
    features: dict[str, Any] = {}
    if raw.startswith("{") or raw.startswith("["):
        try:
            blob = json.loads(raw)
            if isinstance(blob, dict) and isinstance(blob.get("features"), dict):
                blob = blob["features"]
            if isinstance(blob, dict):
                schema = SCHEMAS[key]
                for fname, value in blob.items():
                    canon = canonical_feature_name(schema, str(fname))
                    if canon is not None:
                        features[canon] = value
        except json.JSONDecodeError:
            features = {}
    if not features:
        mapped = extract_catalog_fields_locally(raw)
        features = dict(mapped.get("features_by_key", {}).get(key) or {})
    result = score_catalog(key, features)
    refused = (not features) and bool(_SYMPTOM_HINT.search(raw))
    if refused:
        result["insufficient"] = True
        result["research_positive_percent"] = None
        result["models"] = []
        result["message"] = (
            "Not a symptom checker. This model only scores columns from "
            f"{SCHEMAS[key].title}. Paste lines like `field: number` for that "
            "table. It cannot name a disease from symptoms."
        )
    elif key == "wisconsin_reduced" and _looks_like_simulator_json(raw):
        needed = ", ".join(SCHEMAS[key].features)
        result["insufficient"] = True
        result["research_positive_percent"] = None
        result["message"] = (
            "That JSON is the Simulator demo (z-scores like radius_mean). "
            "This sheet needs the six wisconsin_reduced FNA columns: "
            f"{needed}. Click High-range sample or upload "
            "demo/synthetic_wisconsin_reduced_demo.pdf."
        )
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "note": (
            "One table, one label. Other trained models are not consulted. "
            "Not a diagnosis."
        ),
        "extracted": features,
        "refused_symptom_checker": refused,
        "result": result,
    }


def score_pasted_record_auto(key: str, text: str) -> dict[str, Any]:
    """Score using an explicit table or field-name detection. Not score-based switching."""
    resolved, meta = resolve_catalog_key(key, text)
    if meta.get("detected") and not meta.get("detect_confident"):
        guess = meta.get("guess_catalog_key")
        return {
            "disclaimer": RESEARCH_DISCLAIMER,
            "detected_catalog_key": None,
            "detect_confident": False,
            "guess_catalog_key": guess,
            "match_percentage": meta.get("match_percentage"),
            "extracted": {},
            "refused_symptom_checker": False,
            "result": {
                "insufficient": True,
                "research_positive_percent": None,
                "models": [],
                "message": (
                    "Could not tell which public table those field *names* belong to. "
                    "Paste enough of one schema’s columns (any catalog table), or pick "
                    "a table in the dropdown. The numeric score does not choose a disease."
                ),
            },
        }
    payload = score_pasted_record(resolved, text)
    payload["detected_catalog_key"] = resolved
    payload["detect_confident"] = True
    payload["match_percentage"] = meta.get("match_percentage")
    payload["schema_title"] = meta.get("schema_title")
    payload["table_was_auto_detected"] = bool(meta.get("detected"))
    return payload


def score_notes_for_table(key: str, text: str) -> dict[str, Any]:
    """NVIDIA (or local regex) extracts this table's fields, then scores it.

    Other catalog tables are ignored. Missing values are not invented.
    """
    if key not in SCHEMAS:
        raise KeyError(f"Unknown catalog key {key!r}")
    raw = (text or "").strip()
    mapped = map_notes_with_llm(raw, catalog_key=key)
    local = extract_catalog_fields_locally(raw).get("features_by_key", {}).get(key) or {}
    nvidia_feats = mapped.get("features_by_key", {}).get(key) or {}
    features = {**local, **nvidia_feats}
    result = score_catalog(key, features)
    refused = (not features) and bool(_SYMPTOM_HINT.search(raw))
    if refused:
        result["insufficient"] = True
        result["research_positive_percent"] = None
        result["models"] = []
        result["message"] = (
            "NVIDIA can read numbers you mention (age, glucose, blood pressure, "
            "named lab fields). It cannot invent those numbers from symptoms, "
            "and it cannot say which disease you have."
        )
    missing = result.get("missing") or []
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "note": (
            "One table, one label. NVIDIA filled only fields it could read "
            "from your words. Not a diagnosis."
        ),
        "extracted": features,
        "missing": missing,
        "mapper_source": mapped.get("mapper_source"),
        "nvidia_model_used": mapped.get("nvidia_model_used"),
        "unmapped_phrases": mapped.get("unmapped_phrases") or [],
        "refused_symptom_checker": refused,
        "result": result,
    }


def score_pdf_record(
    key: str, data: bytes, *, use_nvidia: bool = False
) -> dict[str, Any]:
    """Score one table from selectable PDF text. Scans and invented labs are refused."""
    text = extract_pdf_text(data)
    if not text.strip():
        raise ValueError(
            "No selectable text in that PDF (often a scan). "
            "This is not a diagnosis from images. Use a text PDF with field: number lines."
        )
    if use_nvidia:
        resolved, meta = resolve_catalog_key(key, text)
        if meta.get("detected") and not meta.get("detect_confident"):
            payload = score_pasted_record_auto(key, text)
        else:
            payload = score_notes_for_table(resolved, text)
            payload["detected_catalog_key"] = resolved
            payload["detect_confident"] = True
            payload["table_was_auto_detected"] = bool(meta.get("detected"))
    else:
        payload = score_pasted_record_auto(key, text)
    payload["extracted_text"] = text[:12000]
    return payload


def map_notes_with_llm(text: str, *, catalog_key: str | None = None) -> dict[str, Any]:
    """Call NVIDIA NIM when possible; otherwise regex-extract catalog fields."""
    from src.nvidia_client import complete_json

    user = (
        schema_prompt_block(catalog_key)
        + "\n\nNotes to extract (research only, not a patient chart):\n"
        + text.strip()
    )
    try:
        raw = complete_json(SYSTEM_PROMPT, user)
        used = raw.pop("_nvidia_model_used", None)
        payload = sanitize_mapped_payload(raw)
        if catalog_key:
            feats = (payload.get("features_by_key") or {}).get(catalog_key) or {}
            payload["catalog_keys"] = [catalog_key] if feats else []
            payload["features_by_key"] = {catalog_key: feats} if feats else {}
        payload["mapper_source"] = "nvidia"
        if used:
            payload["nvidia_model_used"] = used
        return payload
    except (NvidiaChatError, NvidiaConfigError, ValueError):
        payload = extract_catalog_fields_locally(text)
        if catalog_key:
            feats = (payload.get("features_by_key") or {}).get(catalog_key) or {}
            payload["catalog_keys"] = [catalog_key] if feats else []
            payload["features_by_key"] = {catalog_key: feats} if feats else {}
        payload["mapper_source"] = "local_regex"
        payload["unmapped_phrases"] = list(payload.get("unmapped_phrases") or []) + [
            "NVIDIA chat unavailable; used local field extraction (not an LLM diagnosis)."
        ]
        return payload


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


def _model_display_name(filename: str, prefix: str) -> str:
    base = filename
    if base.endswith(".joblib"):
        base = base[:-7]
    stem = f"{prefix}_" if prefix else ""
    if stem and base.startswith(stem):
        base = base[len(stem):]
    if base.endswith("_model"):
        base = base[:-6]

    known = {
        "logistic_regression": "Logistic Regression",
        "random_forest": "Random Forest",
        "qsvc": "QSVC",
        "rbf_svm": "RBF SVM",
        "vqc": "VQC",
        "qnn": "QNN",
        "gradient_boosting": "Gradient Boosting",
        "xgboost": "XGBoost",
        "decision_tree": "Decision Tree",
        "knn": "K-Nearest Neighbors",
        "naive_bayes": "Naive Bayes",
        "mlp": "Neural Network (MLP)",
    }
    return known.get(base, base.replace("_", " ").title())


def iter_scorable_model_files(key: str, prefix: str) -> list[tuple[str, Any]]:
    """Named joblib files the UI can run for one catalog table (auto-discovers all matching models)."""
    models_dir = get_models_dir()
    items: list[tuple[str, Any]] = []
    seen: set[str] = set()
    stem = f"{prefix}_" if prefix else ""

    if prefix:
        for path in sorted(models_dir.glob(f"{stem}*_model.joblib")):
            name = _model_display_name(path.name, prefix)
            items.append((name, path))
            seen.add(path.name)
    else:
        for expected in ("logistic_regression_model.joblib", "random_forest_model.joblib"):
            p = models_dir / expected
            if p.is_file():
                items.append((_model_display_name(expected, ""), p))
                seen.add(expected)

    if key == "wisconsin_reduced":
        for extra, extra_prefix in [
            ("qsvc_model.joblib", ""),
            ("qml_reduced_rbf_svm_model.joblib", "qml_reduced"),
            ("qnn_model.joblib", ""),
        ]:
            p = models_dir / extra
            if p.is_file() and extra not in seen:
                items.append((_model_display_name(extra, extra_prefix), p))
                seen.add(extra)

    qsvc_cand = models_dir / f"{stem}qsvc_model.joblib" if prefix else models_dir / "qsvc_model.joblib"
    if qsvc_cand.is_file() and qsvc_cand.name not in seen:
        items.append(("QSVC", qsvc_cand))
        seen.add(qsvc_cand.name)

    priority = {
        "Logistic Regression": 1,
        "Random Forest": 2,
        "RBF SVM": 3,
        "QSVC": 4,
        "QNN": 5,
        "VQC": 6,
    }
    items.sort(key=lambda x: priority.get(x[0], 20))
    return items


def _positive_score_percent(model, row: pd.DataFrame) -> float:
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(row)
            if getattr(proba, "ndim", 1) == 2 and proba.shape[1] >= 2:
                return round(100.0 * float(np.asarray(proba)[0, 1]), 1)
        except Exception:
            pass
    if hasattr(model, "decision_function"):
        score = float(np.asarray(model.decision_function(row)).reshape(-1)[0])
        # Ranking score, not a calibrated probability.
        mapped = 1.0 / (1.0 + np.exp(-score))
        return round(100.0 * float(mapped), 1)
    raise RuntimeError("Saved model has neither predict_proba nor decision_function.")


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
        missing = ", ".join(cov["missing"])
        base["message"] = (
            "Insufficient data: not enough of this table’s own numbers yet — "
            "no research score. "
            f"Need: {missing}."
        )
        return base

    scored: list[dict[str, Any]] = []
    for name, path in iter_scorable_model_files(key, schema.model_prefix):
        if not path.is_file():
            continue
        try:
            model = joblib.load(path)
            row = _align_row(model, schema, features, quantum=(name == "QSVC"))
            if row is None:
                scored.append(
                    {
                        "name": name,
                        "file": path.name,
                        "percent": None,
                        "error": "Could not align columns to this saved model.",
                    }
                )
                continue
            percent = _positive_score_percent(model, row)
            scored.append(
                {
                    "name": name,
                    "file": path.name,
                    "percent": percent,
                    "error": None,
                }
            )
        except Exception as exc:
            scored.append(
                {
                    "name": name,
                    "file": path.name,
                    "percent": None,
                    "error": str(exc),
                }
            )

    usable = [item for item in scored if item.get("percent") is not None]
    if not usable:
        base["insufficient"] = True
        base["models"] = scored
        if not scored:
            base["message"] = (
                f"No saved model for {key}. Train it first "
                f"(prefix={schema.model_prefix or 'wisconsin'})."
            )
        else:
            base["message"] = scored[0].get("error") or "Could not score saved models."
        return base

    first = usable[0]
    base["research_positive_percent"] = first["percent"]
    base["model_used"] = first["file"]
    base["models"] = scored
    missing = cov["missing"]
    extra = ""
    if missing:
        missing_str = ", ".join(missing)
        base["completeness_advice"] = (
            f"Partial input: {len(cov['filled'])} of {len(schema.features)} features provided. "
            f"Missing measurement(s): [{missing_str}]. "
            f"The score was calculated using baseline population median imputation for missing values. "
            f"Without test values for [{missing_str}], this is an estimated determination on partial data. "
            f"Providing [{missing_str}] will enable full, non-imputed schema determination."
        )
        extra = f" {base['completeness_advice']}"
    else:
        base["completeness_advice"] = "Full schema provided. All features evaluated without imputation."

    base["message"] = (
        "Research score for this one public table only — not a diagnosis."
        + extra
    )
    return base


def _align_row(
    model,
    schema: CatalogSchema,
    features: dict[str, Any],
    *,
    quantum: bool = False,
) -> pd.DataFrame | None:
    raw_names = getattr(model, "feature_names_in_", None)
    names = list(raw_names) if raw_names is not None and len(raw_names) else []
    frame = pd.DataFrame([{k: features.get(k) for k in schema.features}])
    if schema.key == "stroke":
        frame = pd.get_dummies(frame, drop_first=True)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    if names:
        aligned = frame.reindex(columns=names)
        extra = [col for col in aligned.columns if col not in schema.features]
        if extra:
            aligned[extra] = aligned[extra].fillna(0)
    else:
        aligned = frame
    if not quantum:
        has_imputer = False
        if hasattr(model, "named_steps") and "imputer" in model.named_steps:
            has_imputer = True
        elif hasattr(model, "steps") and any(s[0] == "imputer" for s in model.steps):
            has_imputer = True
        if not has_imputer and aligned.isna().to_numpy().any():
            aligned = aligned.fillna(0)
    if quantum:
        scaler_name = (
            "qml_minmax_scaler.joblib"
            if schema.key in {"wisconsin", "wisconsin_reduced"}
            else f"{schema.model_prefix}_qml_minmax_scaler.joblib"
        )
        scaler_path = get_models_dir() / scaler_name
        if not scaler_path.is_file():
            return None
        scaler = joblib.load(scaler_path)
        if aligned.isna().to_numpy().any():
            return None
        scaled = scaler.transform(aligned)
        return pd.DataFrame(scaled, columns=list(aligned.columns))
    return aligned


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
        "mapper_source": payload.get("mapper_source"),
        "nvidia_model_used": payload.get("nvidia_model_used"),
        "results": results,
        "consultancy": (
            "See a licensed clinician in your area if you need care. "
            "This tool does not recommend named doctors, rankings, or treatment."
        ),
    }
