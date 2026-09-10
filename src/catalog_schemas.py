"""Feature schemas for research-table scoring. Not a diagnosis catalog.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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

# Extra paste keys that still mean the same wisconsin_reduced columns.
FEATURE_NAME_ALIASES: dict[str, tuple[str, ...]] = {
    "mean perimeter": ("perimeter_mean", "mean_perimeter"),
    "mean concave points": (
        "concave points_mean",
        "mean_concave_points",
        "concave_points_mean",
    ),
    "worst radius": ("radius_worst", "worst_radius"),
    "worst perimeter": ("perimeter_worst", "worst_perimeter"),
    "worst area": ("area_worst", "worst_area"),
    "worst concave points": (
        "concave points_worst",
        "worst_concave_points",
        "concave_points_worst",
    ),
    "pelvic_tilt": ("pelvic_tilt numeric", "pelvic tilt"),
    "lumbar_lordosis_angle": ("lumbar lordosis angle",),
    "sacral_slope": ("sacral slope",),
    "pelvic_radius": ("pelvic radius",),
    "degree_spondylolisthesis": ("grade_of_spondylolisthesis", "spondylolisthesis"),
    "pelvic_incidence": ("pelvic incidence",),
}

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

DDD_FEATURES = (
    "pelvic_incidence",
    "pelvic_tilt",
    "lumbar_lordosis_angle",
    "sacral_slope",
    "pelvic_radius",
    "degree_spondylolisthesis",
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

PIMA_FEATURES = (
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
)

HEART_UCI_FEATURES = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
)

KIDNEY_FEATURES = (
    "age",
    "bp",
    "sg",
    "al",
    "su",
    "bgr",
    "bu",
    "sc",
    "sod",
    "pot",
    "hemo",
    "rbc_normal",
    "pc_normal",
    "pcc_present",
    "ba_present",
    "htn_yes",
    "dm_yes",
    "cad_yes",
    "appet_poor",
    "pe_yes",
    "ane_yes",
)

LIVER_FEATURES = (
    "Age",
    "Total_Bilirubin",
    "Direct_Bilirubin",
    "Alkaline_Phosphotase",
    "Alamine_Aminotransferase",
    "Aspartate_Aminotransferase",
    "Total_Protiens",
    "Albumin",
    "Albumin_and_Globulin_Ratio",
    "Gender_Male",
)

PARKINSON_FEATURES = (
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
    "RPDE",
    "DFA",
    "spread1",
    "spread2",
    "D2",
    "PPE",
)

THYROID_FEATURES = (
    "age",
    "sex",
    "on thyroxine",
    "query on thyroxine",
    "on antithyroid medication",
    "sick",
    "pregnant",
    "thyroid surgery",
    "I131 treatment",
    "query hypothyroid",
    "query hyperthyroid",
    "lithium",
    "goitre",
    "tumor",
    "hypopituitary",
    "psych",
    "TSH measured",
    "TSH",
    "T3 measured",
    "TT4 measured",
    "TT4",
    "T4U measured",
    "T4U",
    "FTI measured",
    "FTI",
)

HEART_FAILURE_FEATURES = (
    "age",
    "anaemia",
    "creatinine_phosphokinase",
    "diabetes",
    "ejection_fraction",
    "high_blood_pressure",
    "platelets",
    "serum_creatinine",
    "serum_sodium",
    "sex",
    "smoking",
    "time",
)

HEART_DISEASE_FEATURES = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
)

FETAL_FEATURES = (
    "baseline value",
    "accelerations",
    "fetal_movement",
    "uterine_contractions",
    "light_decelerations",
    "severe_decelerations",
    "prolongued_decelerations",
    "abnormal_short_term_variability",
    "mean_value_of_short_term_variability",
    "percentage_of_time_with_abnormal_long_term_variability",
    "mean_value_of_long_term_variability",
    "histogram_width",
    "histogram_min",
    "histogram_max",
    "histogram_number_of_peaks",
    "histogram_number_of_zeroes",
    "histogram_mode",
    "histogram_mean",
    "histogram_median",
    "histogram_variance",
    "histogram_tendency",
)

CERVICAL_FEATURES = (
    "Age",
    "Number of sexual partners",
    "First sexual intercourse",
    "Num of pregnancies",
    "Smokes",
    "Smokes (years)",
    "Smokes (packs/year)",
    "Hormonal Contraceptives",
    "Hormonal Contraceptives (years)",
    "IUD",
    "IUD (years)",
    "STDs",
    "STDs (number)",
    "STDs:condylomatosis",
    "STDs:cervical condylomatosis",
    "STDs:vaginal condylomatosis",
    "STDs:vulvo-perineal condylomatosis",
    "STDs:syphilis",
    "STDs:pelvic inflammatory disease",
    "STDs:genital herpes",
    "STDs:molluscum contagiosum",
    "STDs:AIDS",
    "STDs:HIV",
    "STDs:Hepatitis B",
    "STDs:HPV",
    "STDs: Number of diagnosis",
    "STDs: Time since first diagnosis",
    "STDs: Time since last diagnosis",
    "Dx:Cancer",
    "Dx:CIN",
    "Dx:HPV",
    "Dx",
)

PCOS_FEATURES = (
    "Age (yrs)",
    "Weight (Kg)",
    "Height(Cm)",
    "BMI",
    "Blood Group",
    "Pulse rate(bpm)",
    "RR (breaths/min)",
    "Hb(g/dl)",
    "Cycle(R/I)",
    "Cycle length(days)",
    "Marraige Status (Yrs)",
    "Pregnant(Y/N)",
    "No. of aborptions",
    "I   beta-HCG(mIU/mL)",
    "II    beta-HCG(mIU/mL)",
    "FSH(mIU/mL)",
    "LH(mIU/mL)",
    "FSH/LH",
    "Hip(inch)",
    "Waist(inch)",
    "Waist:Hip Ratio",
    "TSH (mIU/L)",
    "AMH(ng/mL)",
    "PRL(ng/mL)",
    "Vit D3 (ng/mL)",
    "PRG(ng/mL)",
    "RBS(mg/dl)",
    "Weight gain(Y/N)",
    "hair growth(Y/N)",
    "Skin darkening (Y/N)",
    "Hair loss(Y/N)",
    "Pimples(Y/N)",
    "Fast food (Y/N)",
    "Reg.Exercise(Y/N)",
    "BP _Systolic (mmHg)",
    "BP _Diastolic (mmHg)",
    "Follicle No. (L)",
    "Follicle No. (R)",
    "Avg. F size (L) (mm)",
    "Avg. F size (R) (mm)",
    "Endometrium (mm)",
)

SEER_BREAST_FEATURES = (
    "Age",
    "Tumor Size",
    "Regional Node Examined",
    "Reginol Node Positive",
    "Race_Other (American Indian/AK Native, Asian/Pacific Islander)",
    "Race_White",
    "Marital Status_Married (including common law)",
    "Marital Status_Separated",
    "Marital Status_Single (never married)",
    "Marital Status_Widowed",
    "T Stage_T2",
    "T Stage_T3",
    "T Stage_T4",
    "N Stage_N2",
    "N Stage_N3",
    "6th Stage_IIB",
    "6th Stage_IIIA",
    "6th Stage_IIIB",
    "6th Stage_IIIC",
    "Grade_Poorly differentiated; Grade III",
    "Grade_Undifferentiated; anaplastic; Grade IV",
    "Grade_Well differentiated; Grade I",
    "A Stage_Regional",
    "Estrogen Status_Positive",
    "Progesterone Status_Positive",
)

SEIZURE_FEATURES = tuple(f"X{i}" for i in range(1, 179))

BRFSS_HEART_FEATURES = (
    "BMI",
    "PhysicalHealth",
    "MentalHealth",
    "SleepTime",
    "Smoking_Yes",
    "AlcoholDrinking_Yes",
    "Stroke_Yes",
    "DiffWalking_Yes",
    "Sex_Male",
    "AgeCategory_25-29",
    "AgeCategory_30-34",
    "AgeCategory_35-39",
    "AgeCategory_40-44",
    "AgeCategory_45-49",
    "AgeCategory_50-54",
    "AgeCategory_55-59",
    "AgeCategory_60-64",
    "AgeCategory_65-69",
    "AgeCategory_70-74",
    "AgeCategory_75-79",
    "AgeCategory_80 or older",
    "Race_Asian",
    "Race_Black",
    "Race_Hispanic",
    "Race_Other",
    "Race_White",
    "Diabetic_No, borderline diabetes",
    "Diabetic_Yes",
    "Diabetic_Yes (during pregnancy)",
    "PhysicalActivity_Yes",
    "GenHealth_Fair",
    "GenHealth_Good",
    "GenHealth_Poor",
    "GenHealth_Very good",
    "Asthma_Yes",
    "KidneyDisease_Yes",
    "SkinCancer_Yes",
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
    "ddd": CatalogSchema(
        key="ddd",
        title="Lumbar/disc orthopedic table (UCI vertebral column)",
        positive_label="Abnormal class (disk hernia or spondylolisthesis) on this table only",
        specialty_hint=(
            "Six public biomechanical angles, not an MRI and not a DDD grade. "
            "Spine / orthopedics is the usual research domain. "
            "See a licensed clinician. We do not name doctors."
        ),
        model_prefix="ddd",
        features=DDD_FEATURES,
        min_filled=6,
        notes="All 6 pelvic/lumbar fields required. Not RSNA lumbar MRI.",
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
    "pima": CatalogSchema(
        key="pima",
        title="Pima Indians diabetes (small UCI table)",
        positive_label="Outcome=1 on this UCI table only",
        specialty_hint=(
            "Tiny public diabetes table, not a lab panel. "
            "See a licensed clinician. We do not name doctors."
        ),
        model_prefix="pima",
        features=PIMA_FEATURES,
        min_filled=5,
        notes="Eight numeric columns. Separate from the BRFSS diabetes survey.",
    ),
    "heart_uci_pooled": CatalogSchema(
        key="heart_uci_pooled",
        title="UCI heart disease, four cohorts pooled",
        positive_label="num>0 (disease present) on these UCI cohorts only",
        specialty_hint=(
            "Public multi-hospital table, not an ECG. "
            "Cardiology is the usual domain. See a licensed clinician. "
            "We do not rank doctors."
        ),
        model_prefix="heart_uci_pooled",
        features=HEART_UCI_FEATURES,
        min_filled=8,
        notes="Cleveland + Hungary + Switzerland + VA. Not the duplicated johnsmith88 mirror.",
    ),
    "kidney": CatalogSchema(
        key="kidney",
        title="Chronic kidney disease (public UCI/Kaggle mirror)",
        positive_label="ckd label in this table only",
        specialty_hint=(
            "Public kidney benchmark, not a clinical lab panel. "
            "Nephrology is the usual domain. See a licensed clinician. We do not name doctors."
        ),
        model_prefix="kidney",
        features=KIDNEY_FEATURES,
        min_filled=8,
        notes="Core clinical indicators including bp, sg, al, su, bgr, bu, sc, hemo.",
    ),
    "liver": CatalogSchema(
        key="liver",
        title="Indian liver patient records (public Kaggle/UCI)",
        positive_label="liver patient label in this table only",
        specialty_hint=(
            "Public liver records, not a diagnostic panel. "
            "Hepatology/Gastroenterology is the domain. See a licensed clinician."
        ),
        model_prefix="liver",
        features=LIVER_FEATURES,
        min_filled=6,
        notes="Bilirubin, liver enzymes, and protein markers.",
    ),
    "parkinson": CatalogSchema(
        key="parkinson",
        title="Parkinson's voice features (public UCI/Kaggle)",
        positive_label="status=1 (Parkinson's) on this benchmark only",
        specialty_hint=(
            "Biomedical voice acoustic measurements, not an exam. "
            "Neurology is the domain. See a licensed clinician."
        ),
        model_prefix="parkinson",
        features=PARKINSON_FEATURES,
        min_filled=8,
        notes="Vocal fundamental frequency, jitter, and shimmer variations.",
    ),
    "thyroid": CatalogSchema(
        key="thyroid",
        title="Thyroid disease recurrence (public Kaggle table)",
        positive_label="Recurred=Yes on this benchmark only",
        specialty_hint=(
            "Public thyroid records, not an endocrinology workup. "
            "Endocrinology is the domain. Consult a licensed clinician."
        ),
        model_prefix="thyroid",
        features=THYROID_FEATURES,
        min_filled=8,
        notes="Clinical history and thyroid hormone indicators (TSH, TT4, T3).",
    ),
    "heart_failure": CatalogSchema(
        key="heart_failure",
        title="Heart failure clinical records (Chicco & Jurman)",
        positive_label="DEATH_EVENT=1 on this benchmark only",
        specialty_hint=(
            "Survival risk factors in heart failure patients. "
            "Cardiology is the domain. See a licensed clinician."
        ),
        model_prefix="heart_failure",
        features=HEART_FAILURE_FEATURES,
        min_filled=6,
        notes="Ejection fraction, serum creatinine, and follow-up clinical indicators.",
    ),
    "heart_disease": CatalogSchema(
        key="heart_disease",
        title="Heart disease (UCI-style mirror, deduped)",
        positive_label="target=1 in this table only",
        specialty_hint=(
            "Deduped 302-row UCI mirror. Cardiology is the domain. See a licensed clinician."
        ),
        model_prefix="heart_disease",
        features=HEART_DISEASE_FEATURES,
        min_filled=7,
        notes="Deduped Kaggle mirror of UCI heart disease (302 unique patient rows).",
    ),
    "fetal": CatalogSchema(
        key="fetal",
        title="Fetal health classification (CTG cardiotocography)",
        positive_label="abnormal fetal state on this CTG benchmark",
        specialty_hint=(
            "Cardiotocography signal features, not an ultrasound or exam. "
            "Obstetrics / Maternal-Fetal Medicine is the domain."
        ),
        model_prefix="fetal",
        features=FETAL_FEATURES,
        min_filled=10,
        notes="CTG heart rate metrics, uterine contractions, and histogram attributes.",
    ),
    "cervical": CatalogSchema(
        key="cervical",
        title="Cervical cancer risk factors (UCI Biopsy benchmark)",
        positive_label="Biopsy=1 on this benchmark only",
        specialty_hint=(
            "Public epidemiology survey, not a screening test or biopsy. "
            "Gynecology / Oncology is the domain."
        ),
        model_prefix="cervical",
        features=CERVICAL_FEATURES,
        min_filled=8,
        notes="Demographic risk factors, contraceptive history, and clinical diagnoses.",
    ),
    "pcos": CatalogSchema(
        key="pcos",
        title="PCOS clinical indicators (Kaggle public dump)",
        positive_label="PCOS=Yes on this benchmark only",
        specialty_hint=(
            "Public clinical markers, not an ultrasound or endocrine panel. "
            "Gynecology / Endocrinology is the domain."
        ),
        model_prefix="pcos",
        features=PCOS_FEATURES,
        min_filled=12,
        notes="Metabolic, hormonal (FSH/LH/AMH), and physical signs.",
    ),
    "seer_breast": CatalogSchema(
        key="seer_breast",
        title="SEER breast cancer subset (survival status)",
        positive_label="Status=Dead in this SEER subset only",
        specialty_hint=(
            "SEER cancer registry demographics and staging. Oncology is the domain. See a licensed clinician."
        ),
        model_prefix="seer_breast",
        features=SEER_BREAST_FEATURES,
        min_filled=8,
        notes="Tumor staging, node count, and receptor status from SEER.",
    ),
    "seizure": CatalogSchema(
        key="seizure",
        title="Epileptic seizure recognition (EEG time-series chunks)",
        positive_label="y=1 seizure class in this table only",
        specialty_hint=(
            "EEG recording chunks, not a clinical EEG read. Neurology is the domain. See a licensed clinician."
        ),
        model_prefix="seizure",
        features=SEIZURE_FEATURES,
        min_filled=10,
        notes="178 EEG signal amplitudes per 1-second recording chunk.",
    ),
    "brfss_heart": CatalogSchema(
        key="brfss_heart",
        title="CDC BRFSS 2020 heart disease survey indicators (~320k rows)",
        positive_label="HeartDisease=Yes on this survey benchmark",
        specialty_hint=(
            "CDC BRFSS annual survey responses, not a clinical exam. Preventive Cardiology is the domain."
        ),
        model_prefix="brfss_heart",
        features=BRFSS_HEART_FEATURES,
        min_filled=10,
        notes="Self-reported health indicators and comorbidities from CDC BRFSS 2020.",
    ),
}

ALLOWED_KEYS = tuple(SCHEMAS.keys())

# When two schemas match equally (same columns), pick the more useful research table.
_TIE_PREFER = (
    "wisconsin_reduced",
    "heart_uci_pooled",
    "ddd",
    "pima",
)
_GENERIC_TOKENS = {
    "age",
    "sex",
    "bmi",
    "weight",
    "height",
    "glucose",
    "male",
    "class",
}


def _norm_field_token(name: str) -> str:
    return " ".join(str(name).strip().lower().replace("_", " ").split())


def _schema_tokens(schema: CatalogSchema) -> set[str]:
    tokens: set[str] = set()
    for feat in schema.features:
        tokens.add(_norm_field_token(feat))
        for alias in FEATURE_NAME_ALIASES.get(feat, ()):
            tokens.add(_norm_field_token(alias))
    return tokens


def _tokens_from_payload(features_or_text: dict[str, Any] | str) -> set[str]:
    import json
    import re

    found: set[str] = set()
    if isinstance(features_or_text, dict):
        for key in features_or_text:
            found.add(_norm_field_token(str(key)))
        return found
    raw = (features_or_text or "").strip()
    if raw.startswith("{") or raw.startswith("["):
        try:
            blob = json.loads(raw)
            if isinstance(blob, dict) and isinstance(blob.get("features"), dict):
                blob = blob["features"]
            if isinstance(blob, dict):
                for key in blob:
                    found.add(_norm_field_token(str(key)))
                if found:
                    return found
        except json.JSONDecodeError:
            found = set()
    for line in raw.splitlines():
        match = re.match(r"^(.+?)\s*[:=]\s*[-+]?\d", line.strip())
        if match:
            found.add(_norm_field_token(match.group(1)))
    return found


def auto_detect_schema(
    features_or_text: dict[str, Any] | str,
) -> tuple[str, float, CatalogSchema]:
    """Best-matching public table from column *names* only. Not a diagnosis."""
    key, _pct, schema, _confident, _count = auto_detect_schema_detailed(features_or_text)
    match_pct = _pct
    return key, match_pct, schema


def auto_detect_schema_detailed(
    features_or_text: dict[str, Any] | str,
) -> tuple[str, float, CatalogSchema, bool, int]:
    """Return (key, coverage %, schema, confident, match_count).

    Confidence requires several *named* columns of one schema. A single generic
    field such as age is not enough to switch tables. Score values are ignored.
    """
    found = _tokens_from_payload(features_or_text)
    best_key = "wisconsin_reduced"
    best_score = -1.0
    best_count = 0

    for key, schema in SCHEMAS.items():
        tokens = _schema_tokens(schema)
        matches = len(found & tokens)
        if matches <= 0:
            continue
        coverage = matches / max(len(schema.features), 1)
        matched = found & tokens
        specific_n = len({tok for tok in matched if tok not in _GENERIC_TOKENS})
        composite = matches * 10.0 + specific_n * 5.0 + coverage
        better = composite > best_score
        tied = abs(composite - best_score) < 1e-9
        if tied:
            prefer_new = _TIE_PREFER.index(key) if key in _TIE_PREFER else 99
            prefer_old = _TIE_PREFER.index(best_key) if best_key in _TIE_PREFER else 99
            better = prefer_new < prefer_old
        if better:
            best_score = composite
            best_key = key
            best_count = matches

    schema = SCHEMAS[best_key]
    match_pct = (
        round((best_count / len(schema.features)) * 100.0, 1) if best_count else 0.0
    )
    coverage = best_count / max(len(schema.features), 1)
    matched = found & _schema_tokens(schema)
    specific_n = len({tok for tok in matched if tok not in _GENERIC_TOKENS})
    n_feat = len(schema.features)
    cap = min(schema.min_filled, 8)
    if best_count == 0:
        confident = False
    elif specific_n < 2 and best_count < schema.min_filled:
        confident = False
    elif n_feat > 40:
        confident = best_count >= min(schema.min_filled, 10)
    else:
        confident = (
            best_count >= schema.min_filled
            or best_count >= cap
            or (best_count >= 3 and coverage >= 0.35)
        )
    return best_key, match_pct, schema, confident, best_count


def resolve_catalog_key(
    requested: str | None, features_or_text: dict[str, Any] | str
) -> tuple[str, dict[str, Any]]:
    """Honor an explicit catalog key, or detect from field names (not scores)."""
    req = (requested or "auto").strip()
    if req and req.lower() not in {"auto", "*"}:
        if req not in SCHEMAS:
            raise KeyError(f"Unknown catalog key {req!r}")
        schema = SCHEMAS[req]
        return req, {
            "detected": False,
            "detect_confident": True,
            "catalog_key": req,
            "match_percentage": 100.0,
            "schema_title": schema.title,
        }
    key, pct, schema, confident, count = auto_detect_schema_detailed(features_or_text)
    return key, {
        "detected": True,
        "detect_confident": confident,
        "catalog_key": key if confident else None,
        "guess_catalog_key": key,
        "match_percentage": pct,
        "match_count": count,
        "schema_title": schema.title,
    }

