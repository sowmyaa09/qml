"""Feature schemas for research-table scoring. Not a diagnosis catalog.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogSchema:
    key: str
    title: str
    positive_label: str
    specialty_hint: str
    model_prefix: str
    features: tuple[str, ...]
    min_filled: int
    notes: str


WISCONSIN_FEATURES = (
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
    "mean symmetry",
    "mean fractal dimension",
    "radius error",
    "texture error",
    "perimeter error",
    "area error",
    "smoothness error",
    "compactness error",
    "concavity error",
    "concave points error",
    "symmetry error",
    "fractal dimension error",
    "worst radius",
    "worst texture",
    "worst perimeter",
    "worst area",
    "worst smoothness",
    "worst compactness",
    "worst concavity",
    "worst concave points",
    "worst symmetry",
    "worst fractal dimension",
)

WISCONSIN_REDUCED = (
    "mean perimeter",
    "mean concave points",
    "worst radius",
    "worst perimeter",
    "worst area",
    "worst concave points",
)

DIABETES_FEATURES = (
    "HighBP",
    "HighChol",
    "CholCheck",
    "BMI",
    "Smoker",
    "Stroke",
    "HeartDiseaseorAttack",
    "PhysActivity",
    "Fruits",
    "Veggies",
    "HvyAlcoholConsump",
    "AnyHealthcare",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Sex",
    "Age",
    "Education",
    "Income",
)

CARDIO_FEATURES = (
    "age",
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
)

STROKE_RAW_FEATURES = (
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "Residence_type",
    "avg_glucose_level",
    "bmi",
    "smoking_status",
)

COIMBRA_FEATURES = (
    "Age",
    "BMI",
    "Glucose",
    "Insulin",
    "HOMA",
    "Leptin",
    "Adiponectin",
    "Resistin",
    "MCP.1",
)

FRAMINGHAM_FEATURES = (
    "male",
    "age",
    "education",
    "currentSmoker",
    "cigsPerDay",
    "BPMeds",
    "prevalentStroke",
    "prevalentHyp",
    "diabetes",
    "totChol",
    "sysBP",
    "diaBP",
    "BMI",
    "heartRate",
    "glucose",
)

HEPATITIS_FEATURES = (
    "Age",
    "Sex",
    "Steroid",
    "Antivirals",
    "Fatigue",
    "Malaise",
    "Anorexia",
    "Liver Big",
    "Liver Firm",
    "Spleen Palpable",
    "Spiders",
    "Ascites",
    "Varices",
    "Bilirubin",
    "Alk Phosphate",
    "Sgot",
    "Albumin",
    "Protime",
    "Histology",
)

SCHEMAS: dict[str, CatalogSchema] = {
    "wisconsin": CatalogSchema(
        key="wisconsin",
        title="Wisconsin breast cancer (public FNA table)",
        positive_label="malignant class on this benchmark only",
        specialty_hint=(
            "This table is a public FNA nuclear-feature benchmark. "
            "If you have a real concern, talk to a licensed clinician. "
            "Oncology is the usual clinical domain of this *research* table. "
            "We do not recommend named doctors or rankings."
        ),
        model_prefix="",
        features=WISCONSIN_FEATURES,
        min_filled=24,
        notes="Need most of the 30 numeric FNA fields.",
    ),
    "wisconsin_reduced": CatalogSchema(
        key="wisconsin_reduced",
        title="Wisconsin reduced (Phase 2, 6 features)",
        positive_label="malignant class on this benchmark only",
        specialty_hint=(
            "Same Wisconsin benchmark, 6 selected columns for hybrid QML. "
            "See a licensed clinician for personal care. We do not name doctors."
        ),
        model_prefix="phase2_reduced",
        features=WISCONSIN_REDUCED,
        min_filled=6,
        notes="All 6 selected FNA fields required.",
    ),
    "diabetes": CatalogSchema(
        key="diabetes",
        title="Diabetes BRFSS survey table",
        positive_label="diabetes survey label in this table only",
        specialty_hint=(
            "Survey-style indicators, not a lab diagnosis. "
            "A licensed clinician (often primary care / endocrinology as a domain) "
            "is who you would ask in real life. We do not recommend named doctors."
        ),
        model_prefix="diabetes",
        features=DIABETES_FEATURES,
        min_filled=15,
        notes="BRFSS-style 0/1 flags plus BMI, Age, etc.",
    ),
    "cardio": CatalogSchema(
        key="cardio",
        title="Cardiovascular Kaggle table",
        positive_label="cardio=1 in this table only",
        specialty_hint=(
            "Public cardio benchmark rows, not an exam. "
            "Cardiology is the usual *domain* of this table. "
            "Seek licensed local care yourself; we do not rank doctors."
        ),
        model_prefix="cardio",
        features=CARDIO_FEATURES,
        min_filled=8,
        notes="Age in this source table is in days.",
    ),
    "stroke": CatalogSchema(
        key="stroke",
        title="Stroke prediction table",
        positive_label="stroke=1 in this table only",
        specialty_hint=(
            "Public stroke-risk table, not an ER score. "
            "Neurology / stroke care is the usual *domain*. "
            "See a licensed clinician locally. We do not invent doctor names."
        ),
        model_prefix="stroke",
        features=STROKE_RAW_FEATURES,
        min_filled=7,
        notes="Categoricals are dummy-encoded to match the saved model.",
    ),
    "coimbra": CatalogSchema(
        key="coimbra",
        title="Breast Cancer Coimbra (blood markers)",
        positive_label="patient class on this UCI table only",
        specialty_hint=(
            "Public blood-marker benchmark, not an FNA and not a diagnosis. "
            "See a licensed clinician. We do not name doctors."
        ),
        model_prefix="coimbra",
        features=COIMBRA_FEATURES,
        min_filled=9,
        notes="All 9 Coimbra fields. Separate from Wisconsin FNA.",
    ),
    "framingham": CatalogSchema(
        key="framingham",
        title="Framingham 10-year CHD table",
        positive_label="TenYearCHD=1 in this table only",
        specialty_hint=(
            "Public teaching subset of risk factors, not a clinic visit. "
            "Cardiology is the usual *domain*. Seek licensed local care; we do not rank doctors."
        ),
        model_prefix="framingham",
        features=FRAMINGHAM_FEATURES,
        min_filled=10,
        notes="Classic epidemiology columns.",
    ),
    "hepatitis": CatalogSchema(
        key="hepatitis",
        title="UCI hepatitis table",
        positive_label="die class on this tiny UCI table only",
        specialty_hint=(
            "Tiny public table, not a liver work-up. "
            "Hepatology/GI is the usual *domain*. See a licensed clinician. We do not name doctors."
        ),
        model_prefix="hepatitis",
        features=HEPATITIS_FEATURES,
        min_filled=10,
        notes="UCI encoding: Class 1=die, 2=live.",
    ),
}

ALLOWED_KEYS = tuple(SCHEMAS.keys())
