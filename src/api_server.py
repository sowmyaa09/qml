"""Local research API + LAKSHYA (stitchfrontend) UI. Not a medical device.

    uvicorn src.api_server:app --reload --port 8000

Serves ``stitchfrontend/dist`` on ``/``. Build with ``npm run build`` in stitchfrontend.
The UI calls ``/v1/*`` to score saved models.
Requires NVIDIA_API_KEY in .env only for /v1/research-map.
"""

from __future__ import annotations

from typing import Any

from datetime import date

from dotenv import load_dotenv

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field, field_validator

from src.catalog_schemas import SCHEMAS, auto_detect_schema_detailed, resolve_catalog_key
from src.interview import next_interview_step
from src.research_map import (
    iter_scorable_model_files,
    map_and_score,
    map_notes_with_llm,
    score_catalog,
    score_notes_for_table,
    score_pasted_record,
    score_pasted_record_auto,
    score_pdf_record,
)
from src.research_report_pdf import (
    build_locked_pdf,
    fingerprint_key,
    generate_unlock_key,
)
from src.qml_cost_dashboard import build_cost_latency_payload
from src.supabase_store import store_unlock_key
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    get_figures_dir,
    get_metrics_dir,
    get_project_root,
)

load_dotenv(get_project_root() / ".env")

app = FastAPI(
    title="Q-Care research mapper",
    description=LONG_DISCLAIMER + " " + RESEARCH_DISCLAIMER,
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Unlock-Key",
        "X-Report-Stored",
        "X-Key-Fingerprint",
        "Content-Disposition",
    ],
)

ROOT = get_project_root()
FRONTEND_DIST = ROOT / "stitchfrontend" / "dist"
_SPA_RESERVED = frozenset({"v1", "health", "docs", "redoc", "openapi.json"})

# Tables available in the research platform (one table = one label).
UI_TABLES = tuple(SCHEMAS.keys())

SLIDER_HINTS: dict[str, dict[str, float | str]] = {
    "mean perimeter": {"min": 50, "max": 190, "step": 0.5, "default": 92, "unit": ""},
    "mean concave points": {
        "min": 0,
        "max": 0.2,
        "step": 0.005,
        "default": 0.05,
        "unit": "",
    },
    "worst radius": {"min": 8, "max": 36, "step": 0.1, "default": 16.3, "unit": ""},
    "worst perimeter": {"min": 50, "max": 250, "step": 0.5, "default": 107, "unit": ""},
    "worst area": {"min": 185, "max": 4250, "step": 5, "default": 880, "unit": ""},
    "worst concave points": {
        "min": 0,
        "max": 0.3,
        "step": 0.005,
        "default": 0.11,
        "unit": "",
    },
    "age": {"min": 29, "max": 77, "step": 1, "default": 54, "unit": "yrs"},
    "sex": {"min": 0, "max": 1, "step": 1, "default": 1, "unit": ""},
    "cp": {"min": 0, "max": 3, "step": 1, "default": 0, "unit": ""},
    "trestbps": {"min": 94, "max": 200, "step": 1, "default": 131, "unit": "mmHg"},
    "chol": {"min": 126, "max": 564, "step": 1, "default": 246, "unit": "mg/dL"},
    "fbs": {"min": 0, "max": 1, "step": 1, "default": 0, "unit": ""},
    "restecg": {"min": 0, "max": 2, "step": 1, "default": 0, "unit": ""},
    "thalach": {"min": 71, "max": 202, "step": 1, "default": 149, "unit": "bpm"},
    "exang": {"min": 0, "max": 1, "step": 1, "default": 0, "unit": ""},
    "oldpeak": {"min": 0, "max": 6.2, "step": 0.1, "default": 1.0, "unit": ""},
    "slope": {"min": 0, "max": 2, "step": 1, "default": 1, "unit": ""},
    "ca": {"min": 0, "max": 4, "step": 1, "default": 0, "unit": ""},
    "thal": {"min": 0, "max": 3, "step": 1, "default": 2, "unit": ""},
    "Pregnancies": {"min": 0, "max": 17, "step": 1, "default": 3, "unit": ""},
    "Glucose": {"min": 44, "max": 199, "step": 1, "default": 120, "unit": "mg/dL"},
    "BloodPressure": {"min": 24, "max": 122, "step": 1, "default": 69, "unit": "mmHg"},
    "SkinThickness": {"min": 0, "max": 99, "step": 1, "default": 23, "unit": "mm"},
    "Insulin": {"min": 0, "max": 846, "step": 5, "default": 79, "unit": "mu U/ml"},
    "BMI": {"min": 18, "max": 67, "step": 0.1, "default": 32.0, "unit": "kg/m2"},
    "DiabetesPedigreeFunction": {
        "min": 0.08,
        "max": 2.4,
        "step": 0.01,
        "default": 0.47,
        "unit": "",
    },
    "Age": {"min": 21, "max": 81, "step": 1, "default": 33, "unit": "years"},
    "Total_Bilirubin": {"min": 0.4, "max": 75.0, "step": 0.1, "default": 1.2, "unit": "mg/dL"},
    "Direct_Bilirubin": {"min": 0.1, "max": 19.7, "step": 0.1, "default": 0.4, "unit": "mg/dL"},
    "Alkaline_Phosphotase": {"min": 60, "max": 2100, "step": 5, "default": 290, "unit": "IU/L"},
    "Alamine_Aminotransferase": {"min": 10, "max": 2000, "step": 5, "default": 40, "unit": "IU/L"},
    "Aspartate_Aminotransferase": {"min": 10, "max": 4900, "step": 5, "default": 50, "unit": "IU/L"},
    "Total_Protiens": {"min": 2.7, "max": 9.6, "step": 0.1, "default": 6.5, "unit": "g/dL"},
    "Albumin": {"min": 0.9, "max": 5.5, "step": 0.1, "default": 3.1, "unit": "g/dL"},
    "Albumin_and_Globulin_Ratio": {"min": 0.3, "max": 2.8, "step": 0.05, "default": 0.95, "unit": ""},
    "creatinine_phosphokinase": {"min": 20, "max": 7860, "step": 10, "default": 250, "unit": "mcg/L"},
    "ejection_fraction": {"min": 14, "max": 80, "step": 1, "default": 38, "unit": "%"},
    "platelets": {"min": 25000, "max": 850000, "step": 5000, "default": 263000, "unit": "mcL"},
    "serum_creatinine": {"min": 0.5, "max": 9.4, "step": 0.1, "default": 1.1, "unit": "mg/dL"},
    "serum_sodium": {"min": 113, "max": 148, "step": 1, "default": 137, "unit": "mEq/L"},
    "bgr": {"min": 22, "max": 490, "step": 2, "default": 121, "unit": "mgs/dl"},
    "bu": {"min": 1.5, "max": 390, "step": 1, "default": 36, "unit": "mgs/dl"},
    "sc": {"min": 0.4, "max": 76.0, "step": 0.1, "default": 1.2, "unit": "mgs/dl"},
    "sod": {"min": 4.5, "max": 163, "step": 1, "default": 137, "unit": "mEq/L"},
    "pot": {"min": 2.5, "max": 47.0, "step": 0.1, "default": 4.6, "unit": "mEq/L"},
    "hemo": {"min": 3.1, "max": 17.8, "step": 0.1, "default": 12.5, "unit": "gms"},
    "pelvic_incidence": {"min": 26, "max": 130, "step": 0.5, "default": 60.0, "unit": "deg"},
    "pelvic_tilt": {"min": -7, "max": 50, "step": 0.5, "default": 17.0, "unit": "deg"},
    "lumbar_lordosis_angle": {"min": 14, "max": 126, "step": 0.5, "default": 52.0, "unit": "deg"},
    "sacral_slope": {"min": 13, "max": 122, "step": 0.5, "default": 43.0, "unit": "deg"},
    "pelvic_radius": {"min": 70, "max": 163, "step": 0.5, "default": 118.0, "unit": "mm"},
    "degree_spondylolisthesis": {"min": -11, "max": 150, "step": 0.5, "default": 26.0, "unit": ""},
    "TSH": {"min": 0.0, "max": 500.0, "step": 0.5, "default": 2.1, "unit": "mIU/L"},
    "TT4": {"min": 2.0, "max": 430.0, "step": 1.0, "default": 108.0, "unit": "nmol/L"},
}

METRICS_FILES = {
    "wisconsin": "classical_model_metrics.csv",
    "wisconsin_reduced": "phase2_reduced_classical_model_metrics.csv",
    "qml": "qml_classical_model_metrics.csv",
    "qml_vs": "qml_vs_classical_metrics.csv",
    "cardio": "cardio_classical_model_metrics.csv",
    "stroke": "stroke_classical_model_metrics.csv",
    "diabetes": "diabetes_classical_model_metrics.csv",
    "coimbra": "coimbra_classical_model_metrics.csv",
    "framingham": "framingham_classical_model_metrics.csv",
    "hepatitis": "hepatitis_classical_model_metrics.csv",
    "pima": "pima_classical_model_metrics.csv",
    "heart_uci_pooled": "heart_uci_pooled_classical_model_metrics.csv",
    "kidney": "kidney_classical_model_metrics.csv",
    "liver": "liver_classical_model_metrics.csv",
    "parkinson": "parkinson_classical_model_metrics.csv",
    "thyroid": "thyroid_classical_model_metrics.csv",
    "heart_failure": "heart_failure_classical_model_metrics.csv",
    "heart_disease": "heart_disease_classical_model_metrics.csv",
    "fetal": "fetal_classical_model_metrics.csv",
    "cervical": "cervical_classical_model_metrics.csv",
    "pcos": "pcos_classical_model_metrics.csv",
    "seer_breast": "seer_breast_classical_model_metrics.csv",
    "seizure": "seizure_classical_model_metrics.csv",
    "brfss_heart": "brfss_heart_classical_model_metrics.csv",
    "ddd": "ddd_classical_model_metrics.csv",
}


class MapRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Notes or extracted PDF text.")
    catalog_key: str | None = Field(
        default=None,
        description="If set, extract and score only this public table.",
    )


class ScoreRequest(BaseModel):
    catalog_key: str = Field(
        default="wisconsin_reduced",
        min_length=1,
        description="One public table key.",
    )
    features: dict[str, Any] = Field(default_factory=dict)


class RecordRequest(BaseModel):
    catalog_key: str = Field(
        default="auto",
        min_length=1,
        description="Public table key, or 'auto' to match field names (not scores).",
    )
    text: str = Field(..., min_length=1)
    use_nvidia: bool = False


class ReportRequest(BaseModel):
    catalog_key: str = Field(default="auto", min_length=1)
    subject_name: str = Field(..., min_length=1, max_length=120)
    date_of_birth: date
    text: str = ""
    features: dict[str, Any] = Field(default_factory=dict)
    use_nvidia: bool = False

    @field_validator("subject_name")
    @classmethod
    def _name_stripped(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Name is required.")
        return name

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def _dob_required(cls, value: Any) -> Any:
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(
                "Date of birth is required (label on the PDF only, not the password)."
            )
        return value


class InterviewRequest(BaseModel):
    catalog_key: str = Field(..., min_length=1)
    features: dict[str, Any] = Field(default_factory=dict)
    last_text: str = ""


def _slider_for(name: str) -> dict[str, Any]:
    from src.feature_labels import enrich_field

    hint = SLIDER_HINTS.get(name)
    if hint:
        return enrich_field(name, dict(hint))
    return enrich_field(
        name,
        {
            "min": 0,
            "max": 100,
            "step": 1,
            "default": 1,
            "unit": "",
        },
    )


def _table_payload(schema) -> dict[str, Any]:
    models = []
    for name, path in iter_scorable_model_files(schema.key, schema.model_prefix):
        models.append({"name": name, "file": path.name, "available": path.is_file()})
    return {
        "key": schema.key,
        "title": schema.title,
        "positive_label": schema.positive_label,
        "features": list(schema.features),
        "min_filled": schema.min_filled,
        "notes": schema.notes,
        "specialty_hint": schema.specialty_hint,
        "ui": schema.key in UI_TABLES,
        "sliders": [_slider_for(name) for name in schema.features],
        "models": models,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "disclaimer": RESEARCH_DISCLAIMER}


@app.get("/v1/catalog")
def catalog() -> dict[str, Any]:
    """Which public tables can be scored, and how many fields each one needs."""
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "note": (
            "One entry = one public table with its own label. There is no "
            "combined multi-disease endpoint."
        ),
        "ui_tables": list(UI_TABLES),
        "tables": [_table_payload(schema) for schema in SCHEMAS.values()],
    }


@app.get("/v1/models")
def models_status() -> dict[str, Any]:
    """Which saved joblib files exist for the UI tables."""
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "tables": [_table_payload(SCHEMAS[key]) for key in UI_TABLES if key in SCHEMAS],
    }


@app.get("/v1/qml-cost-latency")
def qml_cost_latency() -> dict[str, Any]:
    """F1 vs wall-clock seconds vs qubits for the cost/latency dashboard."""
    return build_cost_latency_payload()


@app.get("/v1/metrics/{key}")
def metrics_for(key: str) -> dict[str, Any]:
    """Held-out metrics CSV as JSON (research scores, not clinical)."""
    import pandas as pd

    name = METRICS_FILES.get(key, f"{key}_classical_model_metrics.csv")
    path = get_metrics_dir() / name
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"No metrics file {name}. Train that table first.",
        )
    frame = pd.read_csv(path)
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "key": key,
        "file": name,
        "rows": frame.to_dict(orient="records"),
    }


@app.get("/v1/figures/{name}")
def figure(name: str):
    """Serve a generated PNG from outputs/figures."""
    if "/" in name or "\\" in name or not name.endswith(".png"):
        raise HTTPException(status_code=400, detail="PNG name only.")
    path = get_figures_dir() / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"No figure {name}.")
    return FileResponse(path, media_type="image/png")


@app.post("/v1/research-map")
def research_map(body: MapRequest) -> dict[str, Any]:
    try:
        if body.catalog_key:
            return score_notes_for_table(body.catalog_key, body.text)
        mapped = map_notes_with_llm(body.text)
        return map_and_score(body.text, mapped=mapped)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/research-score")
def research_score(body: ScoreRequest) -> dict[str, Any]:
    try:
        result = score_catalog(body.catalog_key, body.features)
        return {"disclaimer": RESEARCH_DISCLAIMER, "result": result}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/research-record")
def research_record(body: RecordRequest) -> dict[str, Any]:
    """Paste a row for one table. Not a symptom-to-disease oracle."""
    try:
        if body.use_nvidia:
            resolved, meta = resolve_catalog_key(body.catalog_key, body.text)
            if meta.get("detected") and not meta.get("detect_confident"):
                return score_pasted_record_auto(body.catalog_key, body.text)
            scored = score_notes_for_table(resolved, body.text)
            scored["detected_catalog_key"] = resolved
            scored["detect_confident"] = True
            scored["table_was_auto_detected"] = bool(meta.get("detected"))
            return scored
        return score_pasted_record_auto(body.catalog_key, body.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


MAX_PDF_BYTES = 5 * 1024 * 1024


@app.post("/v1/research-record-pdf")
async def research_record_pdf(
    file: UploadFile = File(...),
    catalog_key: str = Form("auto"),
    use_nvidia: str = Form("false"),
) -> dict[str, Any]:
    """Extract selectable PDF text, then score one table. Not a scan-to-diagnosis tool."""
    name = (file.filename or "").lower()
    if not name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a .pdf with selectable text.")
    data = await file.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="PDF is too large (max 5 MB).")
    nvidia = str(use_nvidia).strip().lower() in {"1", "true", "yes", "on"}
    try:
        return score_pdf_record(catalog_key, data, use_nvidia=nvidia)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/research-report")
def research_report(body: ReportRequest) -> Response:
    """Score one table, return a password-locked research PDF. Not a diagnosis."""
    try:
        if body.text.strip():
            if body.use_nvidia:
                resolved, meta = resolve_catalog_key(body.catalog_key, body.text)
                if meta.get("detected") and not meta.get("detect_confident"):
                    payload = score_pasted_record_auto(body.catalog_key, body.text)
                else:
                    payload = score_notes_for_table(resolved, body.text)
                    payload["detected_catalog_key"] = resolved
            else:
                payload = score_pasted_record_auto(body.catalog_key, body.text)
        elif body.features:
            resolved, meta = resolve_catalog_key(body.catalog_key, body.features)
            if meta.get("detected") and not meta.get("detect_confident"):
                raise HTTPException(
                    status_code=400,
                    detail="Could not tell which table those field names belong to.",
                )
            result = score_catalog(resolved, body.features)
            payload = {
                "disclaimer": RESEARCH_DISCLAIMER,
                "extracted": body.features,
                "refused_symptom_checker": False,
                "detected_catalog_key": resolved,
                "result": result,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Paste field: number lines or send features for one table.",
            )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = payload.get("result") or {}
    if payload.get("refused_symptom_checker") or result.get("insufficient"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message")
            or "Not enough of this table’s own numbers — no locked PDF.",
        )

    unlock_key = generate_unlock_key()
    pdf_bytes, unlock_key = build_locked_pdf(
        subject_name=body.subject_name,
        date_of_birth=body.date_of_birth,
        catalog_title=result.get("title") or body.catalog_key,
        extracted=payload.get("extracted") or {},
        result=result,
        unlock_key=unlock_key,
    )
    fingerprint = fingerprint_key(unlock_key)
    score = result.get("research_positive_percent")
    stored = store_unlock_key(
        catalog_key=payload.get("detected_catalog_key") or body.catalog_key,
        subject_name=body.subject_name,
        date_of_birth=body.date_of_birth,
        unlock_key=unlock_key,
        key_fingerprint=fingerprint,
        research_score=None if score is None else float(score),
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="quresense-research-score.pdf"',
            "X-Unlock-Key": unlock_key,
            "X-Report-Stored": "true" if stored else "false",
            "X-Key-Fingerprint": fingerprint,
        },
    )


@app.post("/v1/interview")
def interview(body: InterviewRequest) -> dict[str, Any]:
    """Next missing column for one table. Not a headache triage bot."""
    try:
        return next_interview_step(body.catalog_key, body.features, body.last_text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class AutoDetectRequest(BaseModel):
    text: str = ""
    features: dict[str, Any] = Field(default_factory=dict)


@app.post("/v1/auto-detect")
def auto_detect(body: AutoDetectRequest) -> dict[str, Any]:
    """Auto-detect which public table best matches the supplied column names or text."""
    inp = body.text if body.text else body.features
    key, match_pct, schema, confident, count = auto_detect_schema_detailed(inp)
    return {
        "disclaimer": RESEARCH_DISCLAIMER,
        "catalog_key": key if confident else None,
        "guess_catalog_key": key,
        "match_percentage": match_pct,
        "match_count": count,
        "detect_confident": confident,
        "schema_title": schema.title,
        "features": list(schema.features),
        "min_filled": schema.min_filled,
        "note": (
            "Matched by field names only. A research score does not switch tables "
            "or name a disease."
        ),
    }



def _frontend_index_path():
    return FRONTEND_DIST / "index.html"


@app.get("/")
def frontend_index():
    path = _frontend_index_path()
    if not path.is_file():
        raise HTTPException(
            status_code=503,
            detail="Frontend not built. cd stitchfrontend && npm install && npm run build",
        )
    return FileResponse(path)


@app.get("/{full_path:path}")
def frontend_spa(full_path: str):
    first = full_path.split("/", 1)[0]
    if first in _SPA_RESERVED:
        raise HTTPException(status_code=404, detail="Not found")
    dist = FRONTEND_DIST.resolve()
    if not dist.is_dir():
        raise HTTPException(
            status_code=503,
            detail="Frontend not built. cd stitchfrontend && npm install && npm run build",
        )
    candidate = (dist / full_path).resolve()
    try:
        candidate.relative_to(dist)
    except ValueError:
        raise HTTPException(status_code=404, detail="Not found") from None
    if candidate.is_file():
        return FileResponse(candidate)
    index = dist / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(
        status_code=503,
        detail="Frontend not built. cd stitchfrontend && npm install && npm run build",
    )
