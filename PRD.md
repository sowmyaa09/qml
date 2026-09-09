# Product Requirements Document (PRD)

**Product name:** Q-Care Detect — Hybrid Quantum Machine Learning Platform for Early Disease Detection  
**Document type:** Product Requirements Document  
**Version:** 0.3  
**Status:** Active. Phases 1–6 implemented (classical, QML, explainability, Streamlit, LAKSHYA UI, local FastAPI).  
**Audience:** Project owner, reviewers, future contributors

This PRD is the source of truth for **what** we build. It maps the assignment problem statement onto a **research prototype** with explicit safety limits. For day-to-day commands and SIH status, [README.md](README.md) and [AGENTS.md](AGENTS.md) may be newer than this file after code changes.

---

## 0. Official problem statement

The following is the assignment brief. Section 1 explains how this product **implements** it without becoming a medical device.

### Background

Early and accurate detection of diseases significantly improves treatment outcomes and reduces healthcare costs. Classical machine learning models have achieved notable success in medical diagnosis; however, they often face limitations when dealing with high-dimensional, noisy, and complex biomedical data (e.g., genomics, medical imaging, and electronic health records).

Quantum machine learning (QML) offers the potential to capture intricate patterns through quantum superposition and entanglement. Due to current hardware constraints, a hybrid quantum-classical approach provides a practical pathway to leverage quantum advantages while remaining executable on existing quantum simulators and near-term quantum devices.

### Description

This problem focuses on designing and developing a hybrid quantum machine learning platform for early disease detection. The platform will integrate classical pre-processing and feature engineering with quantum-enhanced learning models (such as quantum support vector machines, quantum neural networks, or variational quantum classifiers). It will be applied to biomedical datasets for the early identification of diseases (e.g., cancer, cardiovascular disorders, or neurological conditions). The system should support data ingestion, hybrid model training, prediction, explainability, and performance evaluation against purely classical baselines.

### Objectives

- Design a hybrid quantum-classical machine learning architecture suitable for early disease detection.
- Develop quantum-enhanced classification/regression models that can process high-dimensional biomedical data.
- Improve detection accuracy, sensitivity, and specificity compared with classical machine learning baselines.
- Ensure the platform is scalable, interpretable, and compatible with near-term quantum hardware and simulators.
- Incorporate data pre-processing, feature selection, and model explainability modules.
- Benchmark the hybrid approach against classical models in terms of accuracy, computational efficiency, and generalization performance.

### Expected solution (assignment)

A fully functional hybrid quantum machine learning software platform capable of performing early disease detection on real or benchmark biomedical datasets. The solution must include data handling pipelines, hybrid quantum-classical model implementation, training and inference workflows, performance evaluation, explainability features, and comprehensive documentation.

### How this PRD interprets the brief

| Assignment phrase | Product interpretation |
|-------------------|------------------------|
| Medical diagnosis / early identification | **Research binary (or later multi-class) risk classification** on public labels. Never a clinical diagnosis. |
| Real or benchmark biomedical datasets | **Public benchmarks first** (sklearn Wisconsin). Additional **public** cancer / cardio / neuro tables as **separate** experiments. No identifiable hospital EHR unless a future legal/ethics addendum exists. |
| Improve accuracy vs classical | **Goal to measure.** Report win/tie/loss. Do not ship a claim that QML is better. |
| High-dimensional genomics / imaging / EHR | **Out of scope for v1.** v1 is tabular. High dimension is reduced classically to 4–8 features before QML. Imaging/genomics would be a later, separate track. |
| Quantum neural networks | Optional track: `EstimatorQNN` via `python -m src.train_qml --with-qnn`. |
| Regression | Not in v1. Classification only unless a later phase adds it. |
| Fully functional platform | Phased delivery (see [Delivery table](#2-delivery-table-expected-deliverables)). Phase 1 is classical-only by design. |

---

## 1. Vision, product type, and users

### 1.1 Vision

A **hybrid quantum-classical research platform** that:

1. Ingests public biomedical tables.
2. Pre-processes and selects features on a classical CPU.
3. Trains classical baselines and (later) hybrid QML models on simulators.
4. Evaluates with the same metrics and split.
5. Explains results at a research level.
6. Optionally shows a non-clinical comparison UI.

### 1.2 Product type

**Is:** academic/research prototype, teaching codebase, classical-vs-QML bench.

**Is not:** medical device, clinical decision support, patient portal, symptom checker that tells a user which disease they have, FDA-validated software.

### 1.3 Users

| User | Needs |
|------|--------|
| Student / beginner | Runnable CLI, plain-language docs, disclaimers |
| Reviewer | Reproducible splits, metrics CSV, honest QML comparison |
| Phase 5 UI visitor | Comparison of models, never a personal diagnosis |

No clinician-user or patient-user in this product definition.

---

## 2. Delivery table (expected deliverables)

This is the checklist for the assignment’s “expected solution.”

| ID | Deliverable | Description | Acceptance (research) | Phase | Status |
|----|-------------|-------------|------------------------|-------|--------|
| D1 | Documentation | README, this PRD, safety language, architecture | Reviewer can understand scope and limits | Docs | **Done** (v0.2) |
| D2 | Data ingestion | Load public dataset(s); inspect; consistent `1` = disease-present | Pipeline runs without hospital files | 1 (+ later datasets in 2+) | **Done** (Wisconsin) |
| D3 | Pre-processing | Stratified split; scaler on train only for linear models | No test leakage | 1 | **Done** |
| D4 | Classical baselines | Logistic Regression + Random Forest | Saved models + metrics | 1 | **Done** |
| D5 | Training workflow | CLI train + persist artifacts | `python -m src.train_classical` | 1 | **Done** |
| D6 | Inference workflow | `predict` / `predict_proba` on held-out test rows | Probabilities used for ROC-AUC | 1 | **Done** |
| D7 | Performance evaluation | Accuracy, precision, recall/sensitivity, specificity, F1, ROC-AUC, confusion matrix, plots | CSV + PNGs written | 1 | **Done** |
| D8 | Tests | Dataset load, split preserves classes, metrics in [0, 1] | `pytest` passes | 1 | **Done** |
| D9 | Feature engineering / selection | Reduce dimensionality for near-term QML (~4–8 features) | Documented method; same split seed | 2 | **Done** (`python -m src.train_phase2`; SelectKBest k=6 default) |
| D10 | Hybrid QML implementation | VQC and QSVC (simulator); optional QNN; RBF SVM kernel control | Runnable without paid quantum cloud | 3 | **Done** (`python -m src.train_qml --with-qnn`) |
| D11 | Hybrid training + inference | Train QML, save artifacts, predict on test | Same test indices as classical where possible | 3 | **Done** (`.joblib` under `models/`; `decision_support` + API scoring) |
| D12 | Benchmark vs classical | Metrics + wall-clock time + generalization (test set) | Table of classical vs QML; no forced winner | 3 | **Done** (+ significance: `python -m src.train_qml_significance`; ablation + second table optional) |
| D13 | Near-term compatibility | Aer simulator; circuit depth/qubits documented; optional real-backend later | Runs on laptop simulator | 3 | **Done** (Qiskit Aer statevector; no real QPU required) |
| D14 | Explainability | Classical coefficients + permutation importance; QML limits documented | Research report, not a clinical explanation | 4 | **Done** (`python -m src.train_phase4`; `src/explain.py`) |
| D15 | Reports | `outputs/reports/` comparison write-up | Includes disclaimer | 4 | **Done** (`python -m src.make_judge_sheet`; phase reports under `outputs/reports/`) |
| D16 | UI | Streamlit + LAKSHYA web UI (React/Vite) | Disclaimer on every page; no patient upload | 5 | **Done** (`streamlit run app/streamlit_app.py`; `stitchfrontend/` built and served by FastAPI) |
| D17 | Optional API | FastAPI for research inference and catalog | Local only; not a hosted clinical API | 6 | **Done** (`uvicorn src.api_server:app --reload --port 8000`) |

**Minimum viable “assignment solution”:** D1–D13 — **complete**. D14–D16 (explainability + usable software) — **complete**. D17 (API) — **complete** (local). Extras beyond this table: decision-support bands/calibration, locked research PDF, NVIDIA schema mapper, 22 catalog datasets, optional PyTorch image tracks.

---

## 3. Safety, ethics, and language

Applies to code, notebooks, README, UI, plots, and reports.

**Required disclaimer:**

> This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.

**Required label on predictions and scores:**

**Research risk classification - not for clinical use.**

| Use | Do not use |
|-----|------------|
| Research risk classification | Diagnosis / you have cancer |
| Predicted class on a public benchmark | Patient portal / medical record |
| Sensitivity on the test set | Screening tool for clinics |
| Public benchmark | Hospital identifiable data |

Do not claim quantum advantage unless a scoped experiment shows it. Never generalize to clinical care.

**Data ethics:** public benchmarks only for current versions. No names, MRNs, or scraped private health data.

---

## 4. Goals and non-goals

### 4.1 Goals

| ID | Goal |
|----|------|
| G1 | Hybrid architecture: classical pre-process/select → quantum classifier (simulator). |
| G2 | Classical baseline **before** QML (Phase 1 done). |
| G3 | Full metric set including sensitivity and specificity. |
| G4 | No data leakage. |
| G5 | Fair QML vs classical benchmark (accuracy, time, test generalization). |
| G6 | Feature selection so QML fits near-term qubit counts. |
| G7 | Explainability at research level. |
| G8 | Beginner-readable code; `random_state=42`. |
| G9 | Language: research classification, never diagnosis. |

### 4.2 Non-goals

| ID | Non-goal |
|----|----------|
| NG1 | Telling a user which disease they have from typed symptoms. |
| NG2 | Merging unrelated disease CSVs into one diagnostic model. |
| NG3 | Clinical or hospital deployment. |
| NG4 | Promising QML beats classical. |
| NG5 | Full genomics / 3D imaging / production EHR in v1. |
| NG6 | Auth, patient database, Docker in early phases. |
| NG7 | Real QPU / paid quantum cloud as a requirement for delivery. |

---

## 5. Data requirements

### 5.1 v1 dataset (Phase 1)

sklearn Wisconsin Diagnostic Breast Cancer (`load_breast_cancer(as_frame=True)`).

- `X = data.data` (30 numeric features).
- `y_binary = (data.target == 0).astype(int)` → **1 = malignant**.

**Why:** public, small, beginner-safe. Feature count will be reduced in Phase 2 for QML.

### 5.2 Split

`train_test_split(..., test_size=0.20, random_state=42, stratify=y_binary)`.

### 5.3 Later public datasets (optional, separate experiments)

The brief mentions cancer, cardiovascular, neurological conditions. Allowed **only** as additional **public** tables, **one experiment each** (same pipeline, different files). Not a single symptom-to-disease oracle.

Hospital data stays out of scope without a new ethics/legal section.

---

## 6. Hybrid architecture

```text
                    Biomedical public table
                              |
                    Data ingestion (D2)
                              |
              Classical pre-process + split (D3)
                              |
              Feature selection 4-8 cols (D9)
                     /                  \
                    /                    \
         Classical LR / RF (D4)     Hybrid VQC / QSVC (D10)
                    \                    /
                     \                  /
                   Shared evaluation (D7, D12)
                              |
                    Explainability (D14)
                              |
                      Optional UI (D16)
```

**Why hybrid (beginner):** a quantum circuit on a simulator cannot ingest 30–10,000 raw features. Classical steps **compress** the problem. The quantum model learns on a **small** vector. That matches near-term hardware.

**Models (Phase 3, implemented):** QSVC (`FidelityStatevectorKernel` + `ZZFeatureMap`), VQC (`RealAmplitudes` + COBYLA), optional EstimatorQNN (`--with-qnn`), plus RBF SVM on the same k features as an honest kernel control.

**Hardware:** Qiskit Aer statevector simulator on a laptop. Real QPU not used; optional later.

---

## 7. Phased functional requirements

### 7.1 Phase 1 — Classical baseline (implemented)

Logistic Regression: `Pipeline([("scaler", StandardScaler()), ("classifier", LogisticRegression(max_iter=5000, random_state=42))])`.

Random Forest: `RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")` — no scaler.

Entry: `python -m src.train_classical`.

Packages: pandas, numpy, scikit-learn, matplotlib, seaborn, joblib, pytest, jupyter.

### 7.2 Phase 2 — Feature selection and reproducibility (implemented)

`python -m src.train_phase2`. SelectKBest (ANOVA F-value) on train only; default k=6. Classical metrics on full vs reduced set on the same test rows.

### 7.3 Phase 3 — Hybrid QML (implemented)

`python -m src.train_qml` (+ `--with-qnn` optional). VQC + QSVC + RBF control on reduced features. Significance layer: `python -m src.train_qml_significance`. Optional: `train_qml_ablation`, `train_qml_table coimbra`. Report runtime; do not claim quantum is better by default.

### 7.4 Phase 4 — Explainability and reports (implemented)

`python -m src.train_phase4`: logistic coefficients, permutation importance, one worked row, QML limits in `src/explain.py`. Reports via `make_judge_sheet` and `outputs/reports/`.

### 7.5 Phase 5 — UI (implemented)

Streamlit (`app/streamlit_app.py`): Home, data, classical, QML, decision support, explainability, mapper, extra tables. **LAKSHYA** React UI (`stitchfrontend/`) served from FastAPI at `http://127.0.0.1:8000`. Research comparison only.

### 7.6 Phase 6 — FastAPI (implemented, local)

`src/api_server.py`: `/health`, `/v1/catalog`, `/v1/research-score`, `/v1/research-record`, `/v1/research-report`, `/v1/interview`, static LAKSHYA build. Optional Supabase for PDF unlock keys. Not clinical deployment.

---

## 8. Metrics and fair comparison

Positive class = disease present (`1`) on the active dataset.

- Sensitivity / recall = `TP / (TP + FN)`
- Specificity = `TN / (TN + FP)` from `confusion_matrix(...).ravel()`
- ROC-AUC from `predict_proba(X_test)[:, 1]`

| Rule | Why |
|------|-----|
| Same train/test split | Fairness |
| Same label definition | Comparable metrics |
| Document feature-count differences | 30-feature RF vs 4-qubit VQC is not the same experiment unless labeled |
| Report runtime | Assignment asks computational efficiency |
| Test-set scores only | Generalization (within this public set) |

---

## 9. Technical architecture (code)

### 9.1 Core modules

| Module | Role |
|--------|------|
| `src/utils.py` | Paths, folders, disclaimers, Agg matplotlib |
| `src/data_loader.py` | Wisconsin load + relabel + inspect |
| `src/tabular_datasets.py` | Extra public tables (22 catalog keys) |
| `src/preprocessing.py` | Stratified split |
| `src/feature_selection.py` | SelectKBest for QML |
| `src/evaluate.py` | Metrics, plots, CSV, summary |
| `src/train_classical.py` | Phase 1 CLI |
| `src/train_phase2.py` | Feature selection + reduced classical |
| `src/train_qml.py` | VQC, QSVC, optional QNN |
| `src/qml_models.py` | Qiskit circuit builders |
| `src/significance.py` | Bootstrap, McNemar, DeLong |
| `src/decision_support.py` | Bands, threshold sweep, calibration |
| `src/explain.py` | Coefficients, row attribution, QML limits |
| `src/train_phase4.py` | Explainability + comparison report |
| `src/make_judge_sheet.py` | Reviewer markdown sheet |
| `src/research_map.py` | Schema mapping + scoring |
| `src/api_server.py` | FastAPI + static LAKSHYA |
| `app/streamlit_app.py` | Streamlit research UI |
| `stitchfrontend/` | LAKSHYA React/Vite/Tailwind UI |

### 9.2 Typical artifacts (after training)

| Location | Description |
|----------|-------------|
| `models/*.joblib` | Classical, QML, tabular models |
| `outputs/metrics/*.csv` | Per-model metrics and test scores |
| `outputs/figures/*.png` | Confusion matrices, ROC, calibration |
| `outputs/reports/` | Phase notes, judge sheet, comparison write-ups |

Artifacts are gitignored; fresh clones must re-run training commands.

---

## 10. Frontend — implemented

**Status: implemented.** Two interfaces: Streamlit (research dashboard) and LAKSHYA (React/Vite, served by FastAPI).

### 10.1 Purpose

Show the **research platform**: data → classical vs hybrid QML → metrics → decision support. Not a clinic.

Must: disclaimer first; comparison-first layout; empty states if QML not trained.

Must not: hospital EHR diagnosis workflow; patient file upload as clinical intake; “You have cancer”; fake quantum scores; multi-disease fused diagnosis.

### 10.2 Design principles

Safety banner on every page. Plain language. Calm academic visual tone. Color not the only signal.

### 10.3 Tools

- **Streamlit:** `streamlit run app/streamlit_app.py`
- **LAKSHYA:** `cd stitchfrontend; npm install; npm run build` then open `http://127.0.0.1:8000` with API running
- Dev proxy: `npm run dev` on port 3000 (proxies `/v1`, `/health` to 8000)

### 10.4 Sitemap (Streamlit)

```text
Home
Data overview
Classical results
QML comparison
Decision support
Explainability
Research notes mapper
Extra research tables
Demo script
About and limits
```

Disclaimer on all pages. LAKSHYA adds Story Pitch, Data Library, Simulator, Score Sheet, Classical Baselines, QML Studio views.

### 10.5 Home wireframe

Banner (educational; not a device; research risk classification). Product name. One paragraph: hybrid QML **research** platform for early disease-**risk** benchmarks. Links to data and results. Footer: not for clinical decisions.

### 10.6 Classical / QML comparison layout

Two (or more) model cards: accuracy, precision, recall, specificity, F1, ROC-AUC. Confusion matrices. Shared ROC. Bar chart. Caption: public test set only.

### 10.7 Components

Required: disclaimer, metric cards, CSV-backed table, plot images.  
Forbidden: hospital CSV upload, login, “diagnose this patient.”

### 10.8 Copy

Required: educational disclaimer; “Research risk classification - not for clinical use.”; scores are not clinical performance.

Forbidden: diagnose, treatment plan, patient portal, “quantum proven better,” SAFE/CANCER stamps.

### 10.9 Visual and interaction

Light theme, wide layout, captions on images. Load `outputs/` artifacts; if missing, tell the user which CLI to run. Do not retrain on every rerun. No silent network exfiltration.

### 10.10 Frontend out of scope

Auth, patient DB, cloud (unless Phase 6), native mobile, clinician submit-a-case workflows.

### 10.11 Frontend success

User understands this is not diagnostic. Can compare classical vs (later) QML with the same metric names.

Full generation prompt: [task.md](task.md).

---

## 11. Success criteria

### 11.1 Now

- [x] README + PRD match the hybrid QML **platform** assignment, with safety mapping.
- [x] Delivery table exists.
- [x] Phase 1 CLI, artifacts, tests.

### 11.2 Assignment-complete

- [x] D9–D13 (feature select + QML + benchmark on simulator).
- [x] D14–D15 (explainability + report).
- [x] D16 (UI) — Streamlit + LAKSHYA.
- [x] D17 (local FastAPI).
- [x] No surface presents a clinical diagnosis (research risk classification only).

---

## 12. Open questions

| Topic | Question |
|-------|----------|
| Feature selection | **Resolved:** SelectKBest (ANOVA), k=6 default; ablation at k=4/6/8 |
| QML stack | **Resolved:** Qiskit 1.x + Aer statevector; no real QPU |
| Extra datasets | **Resolved:** 22 catalog schemas; large tables classical-only; QSVC capped at 5000 rows |
| QNN | **Resolved:** optional `--with-qnn` track |
| Regression | Not in scope unless a public regression benchmark is added |
| Hosted deploy | Local only; cloud clinical API out of scope |

---

## 13. Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-28 | Initial PRD (classical-first teaching project). |
| 0.2 | 2026-08-29 | Full assignment problem statement; delivery table; hybrid platform architecture; Phase 1 marked done. |
| 0.3 | 2026-09-09 | D9–D17 marked **Done**; phases 2–6, LAKSHYA UI, FastAPI, significance, decision support documented. |

---

## 14. Next action

1. Fresh clone: run training commands in [README.md](README.md) / [AGENTS.md](AGENTS.md) to regenerate `models/` and `outputs/`.  
2. Demo: `uvicorn src.api_server:app --reload --port 8000` + LAKSHYA build, or `streamlit run app/streamlit_app.py`.  
3. Reviewer pack: `python -m src.make_judge_sheet`; team briefing: `python -m src.generate_explanation_pdf`.  
4. Do **not** add symptom-to-disease diagnosis, multi-disease fusion, or clinical deployment claims.
