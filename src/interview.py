"""Ask one missing schema field at a time. Not a symptom checker.

Questions only match columns on the selected public table. A headache is not
a Wisconsin FNA field and is not a 1-10 pain score on the UCI heart table
(that table uses chest-pain *type* 0-3).

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from typing import Any

from src.catalog_schemas import SCHEMAS
from src.research_map import _present, coverage_for
from src.utils import RESEARCH_DISCLAIMER

# Plain-language prompts for the HTML interview. Keys must be schema columns.
QUESTIONS: dict[str, dict[str, dict[str, Any]]] = {
    "wisconsin_reduced": {
        "mean perimeter": {
            "question": (
                "Mean perimeter of cell nuclei — average length around the edge "
                "of breast cells in the FNA sample (not a symptom). Value?"
            ),
            "kind": "number",
            "min": 50,
            "max": 190,
            "step": 0.5,
        },
        "mean concave points": {
            "question": "Mean concave points (0-0.2 on this table)?",
            "kind": "number",
            "min": 0,
            "max": 0.2,
            "step": 0.005,
        },
        "worst radius": {
            "question": (
                "Worst (largest) radius — biggest half-width among the most "
                "abnormal nuclei. Value?"
            ),
            "kind": "number",
            "min": 8,
            "max": 36,
            "step": 0.1,
        },
        "worst perimeter": {
            "question": (
                "Worst (largest) perimeter — longest edge around the most "
                "abnormal nuclei. Value?"
            ),
            "kind": "number",
            "min": 50,
            "max": 250,
            "step": 0.5,
        },
        "worst area": {
            "question": "Worst area?",
            "kind": "number",
            "min": 185,
            "max": 4250,
            "step": 5,
        },
        "worst concave points": {
            "question": "Worst concave points (0-0.3)?",
            "kind": "number",
            "min": 0,
            "max": 0.3,
            "step": 0.005,
        },
    },
    "heart_uci_pooled": {
        "age": {
            "question": "Age in years?",
            "kind": "number",
            "min": 29,
            "max": 77,
            "step": 1,
        },
        "sex": {
            "question": "Sex on this UCI table: 1 = male, 0 = female?",
            "kind": "choice",
            "choices": [{"value": 0, "label": "0 female"}, {"value": 1, "label": "1 male"}],
        },
        "cp": {
            "question": (
                "Chest Pain type (CP) on this table: 0 = typical angina, "
                "1 = atypical angina, 2 = non-anginal pain, 3 = asymptomatic. "
                "Pick 0–3 — not a 1–10 pain score and not headache."
            ),
            "kind": "choice",
            "choices": [
                {"value": 0, "label": "0 typical"},
                {"value": 1, "label": "1 atypical"},
                {"value": 2, "label": "2 non-anginal"},
                {"value": 3, "label": "3 asymptomatic"},
            ],
        },
        "trestbps": {
            "question": "Resting blood pressure (mmHg)?",
            "kind": "number",
            "min": 94,
            "max": 200,
            "step": 1,
        },
        "chol": {
            "question": "Serum cholesterol (mg/dL)?",
            "kind": "number",
            "min": 126,
            "max": 564,
            "step": 1,
        },
        "fbs": {
            "question": "Fasting blood sugar > 120 mg/dL? 1 = yes, 0 = no.",
            "kind": "choice",
            "choices": [{"value": 0, "label": "0 no"}, {"value": 1, "label": "1 yes"}],
        },
        "restecg": {
            "question": "Resting ECG code on this table (0, 1, or 2)?",
            "kind": "choice",
            "choices": [
                {"value": 0, "label": "0"},
                {"value": 1, "label": "1"},
                {"value": 2, "label": "2"},
            ],
        },
        "thalach": {
            "question": "Maximum heart rate achieved (bpm)?",
            "kind": "number",
            "min": 71,
            "max": 202,
            "step": 1,
        },
        "exang": {
            "question": "Exercise-induced angina on this table? 1 = yes, 0 = no.",
            "kind": "choice",
            "choices": [{"value": 0, "label": "0 no"}, {"value": 1, "label": "1 yes"}],
        },
        "oldpeak": {
            "question": "ST depression (oldpeak)?",
            "kind": "number",
            "min": 0,
            "max": 6.2,
            "step": 0.1,
        },
        "slope": {
            "question": "Slope of peak ST segment (0, 1, or 2)?",
            "kind": "choice",
            "choices": [
                {"value": 0, "label": "0"},
                {"value": 1, "label": "1"},
                {"value": 2, "label": "2"},
            ],
        },
        "ca": {
            "question": "Number of major vessels colored (0-4)?",
            "kind": "choice",
            "choices": [{"value": i, "label": str(i)} for i in range(5)],
        },
        "thal": {
            "question": "Thal code on this table (0-3)?",
            "kind": "choice",
            "choices": [{"value": i, "label": str(i)} for i in range(4)],
        },
    },
    "pima": {
        "Pregnancies": {
            "question": "Number of pregnancies?",
            "kind": "number",
            "min": 0,
            "max": 17,
            "step": 1,
        },
        "Glucose": {
            "question": "Plasma glucose (mg/dL)?",
            "kind": "number",
            "min": 44,
            "max": 199,
            "step": 1,
        },
        "BloodPressure": {
            "question": "Diastolic blood pressure (mmHg)?",
            "kind": "number",
            "min": 24,
            "max": 122,
            "step": 1,
        },
        "SkinThickness": {
            "question": "Triceps skin fold (mm)?",
            "kind": "number",
            "min": 0,
            "max": 99,
            "step": 1,
        },
        "Insulin": {
            "question": "2-hour serum insulin?",
            "kind": "number",
            "min": 0,
            "max": 846,
            "step": 5,
        },
        "BMI": {
            "question": "Body mass index?",
            "kind": "number",
            "min": 18,
            "max": 67,
            "step": 0.1,
        },
        "DiabetesPedigreeFunction": {
            "question": "Diabetes pedigree function on this table?",
            "kind": "number",
            "min": 0.08,
            "max": 2.4,
            "step": 0.01,
        },
        "Age": {
            "question": "Age in years?",
            "kind": "number",
            "min": 21,
            "max": 81,
            "step": 1,
        },
    },
}

_SYMPTOM_WORDS = (
    "headache",
    "pain",
    "fever",
    "cough",
    "nausea",
    "dizzy",
    "tired",
    "symptom",
)


def _notice_for_text(key: str, last_text: str) -> str:
    blob = (last_text or "").lower()
    if not any(word in blob for word in _SYMPTOM_WORDS):
        return ""
    title = SCHEMAS[key].title
    return (
        f"Those words are symptoms, not columns on {title}. "
        "This questionnaire only asks that table's research fields. "
        "It will not ask a 1-10 headache score and will not name a disease. "
        "See a licensed clinician for real symptoms."
    )


def next_interview_step(
    key: str,
    features: dict[str, Any] | None = None,
    last_text: str = "",
) -> dict[str, Any]:
    """Return the next unanswered schema field for one table."""
    if key not in SCHEMAS:
        raise KeyError(f"Unknown catalog key {key!r}")
    schema = SCHEMAS[key]
    filled = dict(features or {})
    cov = coverage_for(schema, filled)
    prompts = QUESTIONS.get(key, {})
    next_name = None
    for name in schema.features:
        if not _present(filled.get(name)):
            next_name = name
            break
    notice = _notice_for_text(key, last_text)
    payload = {
        "disclaimer": RESEARCH_DISCLAIMER,
        "key": key,
        "title": schema.title,
        "min_filled": schema.min_filled,
        "filled_count": len(cov["filled"]),
        "remaining": cov["missing"],
        "can_score": cov["runnable"],
        "done": next_name is None,
        "notice": notice,
        "field": next_name,
        "question": None,
        "kind": None,
        "min": None,
        "max": None,
        "step": None,
        "choices": None,
    }
    if next_name is None:
        payload["question"] = (
            "All columns for this table are filled. Score this table only — "
            "not a diagnosis."
        )
        return payload
    spec = prompts.get(next_name) or {
        "question": f"Value for `{next_name}` on this table?",
        "kind": "number",
        "min": 0,
        "max": 400,
        "step": 1,
    }
    payload["question"] = spec["question"]
    payload["kind"] = spec.get("kind", "number")
    payload["min"] = spec.get("min")
    payload["max"] = spec.get("max")
    payload["step"] = spec.get("step")
    payload["choices"] = spec.get("choices")
    return payload
