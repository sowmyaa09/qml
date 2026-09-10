# Q-Care Detect

**Hybrid Quantum Machine Learning Platform for Early Disease Detection**

A research and educational software platform: **classical pre-processing and feature engineering** plus **hybrid quantum-classical models** (VQC, QSVC / quantum-inspired classifiers), benchmarked against **purely classical** models on **public biomedical datasets**.

This repository implements that problem as a **prototype you can run**, not as a hospital or diagnostic product.

> **Current status:** Phases 1–5 are implemented in code: classical baselines, feature selection, simulator QML (VQC/QSVC), extra public tables, optional MSK image trainers, a written comparison report, and a Streamlit research UI. Always: **research only, not clinical use.**

---

## Medical and ethical disclaimer

**This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.**

The assignment text talks about “early disease detection” and “medical diagnosis” as a **research theme**. In this codebase:

- Outputs are **research risk classification**, never a diagnosis.
- Every prediction surface must show: **Research risk classification - not for clinical use.**
- Do not treat model output as medical advice.
- Use **public benchmark data** only in the initial versions. No patient-identifiable or hospital EHR dumps.
- Do **not** claim quantum models are automatically better. “Improve accuracy vs classical” is a **hypothesis to measure**, not a guaranteed result.

---

## Problem statement (assignment)

### Background

Early and accurate detection of diseases can improve treatment outcomes and reduce healthcare costs in **clinical settings**. Classical machine learning has been successful on many biomedical tasks, but it can struggle with **high-dimensional, noisy, and complex** data (for example genomics, medical imaging, and electronic health records).

Quantum machine learning (QML) is studied because quantum states can, in principle, represent complex correlations (superposition and entanglement). **Today’s quantum hardware is limited**, so a **hybrid quantum-classical** design is the practical path: classical computers do loading, scaling, and feature selection; quantum circuits (or simulators) run a small learning model. That can run on **simulators** and, later, **near-term quantum devices**.

### Description

This project designs a **hybrid quantum machine learning platform** for **early disease-risk research** on biomedical **benchmarks**. The platform will:

- ingest public tabular (and later, if added, other public) biomedical datasets;
- apply classical pre-processing and feature engineering;
- train quantum-enhanced classifiers (quantum SVM / variational quantum classifier / related hybrid models);
- run inference and evaluation against classical baselines;
- add explainability and documentation.

Example **research domains** (separate experiments, not one “guess my disease” box): cancer-related benchmarks, cardiovascular tables, neurological public sets — only where data is public and licensed.

### Objectives

| ID | Objective | How this repo treats it |
|----|-----------|-------------------------|
| O1 | Design a hybrid quantum-classical architecture for early disease-risk **research** | Classical pipeline first; QML on reduced features (Phase 3) |
| O2 | Develop quantum-enhanced classification models for high-dimensional biomedical data | High dimension is handled **classically** (select 4–8 features); quantum part stays small (near-term hardware) |
| O3 | Improve accuracy, sensitivity, and specificity vs classical baselines | **Evaluate and report honestly.** QML may win, tie, or lose |
| O4 | Scalable, interpretable, compatible with simulators and near-term hardware | Simulators first; small circuits; explainability in Phase 4 |
| O5 | Pre-processing, feature selection, explainability | Phases 1–2 and 4 |
| O6 | Benchmark hybrid vs classical: accuracy, compute cost, generalization | Same split, same metrics, plus runtime |

---

## Delivery table (expected deliverables)

| # | Deliverable | What it is | Phase | Status |
|---|----------------|------------|-------|--------|
| D1 | Problem docs | This README + [PRD.md](PRD.md) (architecture, safety, frontend spec) | Docs | **Done** |
| D2 | Data handling pipeline | Load public data, inspect, relabel, stratified train/test, no leakage | 1 | **Done** (Wisconsin breast cancer via sklearn) |
| D3 | Classical baselines | Logistic Regression (scaled Pipeline) + Random Forest | 1 | **Done** |
| D4 | Evaluation module | Accuracy, precision, recall/sensitivity, specificity, F1, ROC-AUC, confusion matrices, plots, CSV | 1 | **Done** |
| D5 | Training / inference CLI | `python -m src.train_classical`; saved `.joblib` models | 1 | **Done** |
| D6 | Tests and reproducibility | `pytest`; `random_state=42`; documented commands | 1 | **Done** |
| D7 | Feature selection / engineering | Reduce ~30 features to ~4–8 for quantum circuits | 2 | **Done** (`python -m src.train_phase2`) |
| D8 | Hybrid QML models | VQC, QSVC, and a QNN track on simulators | 3 | **Done** (`python -m src.train_qml --with-qnn`) |
| D9 | QML vs classical benchmark | Same metrics + runtime; RBF SVM kernel control; no assumed quantum win | 3 | **Done** |
| D9b | Qubit ablation | QSVC at k = 4, 6, 8: F1 vs qubits vs seconds | 3 | **Done** (`python -m src.train_qml_ablation`) |
| D9c | Second hybrid table | QSVC on another small public table, kept separate | 3 | **Done** (`python -m src.train_qml_table coimbra`) |
| D10 | Explainability | Permutation importance, linear coefficients, one worked row; QML limits documented | 4 | **Done** (`python -m src.train_phase4`) |
| D10b | Prediction and decision support | Research probability, band, threshold tuning, calibration/Brier | 3–5 | **Done** (Streamlit **Decision support**) |
| D11 | Research report artifacts | Written comparison + reviewer sheet under `outputs/reports/` | 4 | **Done** (`python -m src.make_judge_sheet`) |
| D12 | User interface | Streamlit: comparison dashboard, disclaimer always on | 5 | **Done** (`streamlit run app/streamlit_app.py`) |
| D13 | Optional API / deploy | FastAPI research mapper + `GET /v1/catalog` | 6 | Local only |
| D14 | Comprehensive documentation | README, PRD, notebook, comments | Ongoing | In progress |

**Out of scope for this delivery:** clinical deployment, diagnosing a person from typed symptoms, fusing unrelated diseases into one “you have X” model, hospital EHR ingestion, claiming FDA/clinical validation.

---

## What is built today

| Item | Status |
|------|--------|
| README + PRD + frontend task prompt | Done |
| `src/` classical pipeline | Done — Phase 1 |
| Tests (`pytest`) | Done |
| Notebook `notebooks/01_classical_baseline.ipynb` | Done |
| Models and plots | Created when you run training |
| Qiskit / VQC / QSVC / QNN | Phase 3 — `python -m src.train_qml --with-qnn` |
| Qubit ablation + extra hybrid tables | `python -m src.train_qml_ablation`, `python -m src.train_qml_table coimbra`, `python -m src.train_qml_table ddd` |
| Decision support + explainability pages | Phase 5 — Streamlit sidebar |
| Reviewer sheet | `python -m src.make_judge_sheet` |
| Streamlit | Phase 5 — `streamlit run app/streamlit_app.py` |

---

## Hybrid architecture (simple picture)

```text
Public biomedical table
        |
        v
Classical: clean, split, scale, select features
        |
        +---> Classical models (LR, Random Forest)     [Phase 1]
        |
        +---> Hybrid QML (VQC, QSVC, QNN on simulator) [Phase 3]
        |
        v
Same metrics + plots + calibration + explainability
        |
        v
Threshold / band decision support for that one label
        |
        v
Optional UI showing a research comparison              [Phase 5]
```

Near-term quantum devices cannot take raw genomics or full EHR. This platform **shrinks** the problem classically, then runs a **small** quantum model. That is the hybrid design, not “one QML that detects every disease from symptoms.”

---

## Folder structure

```text
qml/
├── README.md
├── PRD.md
├── task.md
├── requirements.txt
├── .gitignore
├── data/raw/  data/processed/
├── notebooks/01_classical_baseline.ipynb
├── src/          (data_loader, preprocessing, train_classical, evaluate, utils)
├── models/
├── outputs/figures/  outputs/metrics/  outputs/reports/
└── tests/test_pipeline.py
```

---

## Roadmap

| Phase | What it is | Status |
|-------|------------|--------|
| **1** | Classical ML baseline | **Done** |
| **2** | Feature selection (~4–8 features), reproducibility | **Done** |
| **3** | Hybrid QML (VQC, QSVC), benchmark vs classical | **Done** (simulator) |
| **4** | Explainability and reports | **Done** |
| **5** | Streamlit UI | **Done** |
| **6** | Optional FastAPI / deployment | Optional |

---

## Installation

**Windows (PowerShell):**

```powershell
cd c:\Projects\qml
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd /path/to/qml
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## How to run (Phase 1)

```powershell
python -m src.train_classical
pytest
```

Optional notebook:

```powershell
jupyter notebook notebooks/01_classical_baseline.ipynb
```

**Phase 1 outputs:**

- `outputs/metrics/classical_model_metrics.csv`
- `outputs/figures/logistic_regression_confusion_matrix.png`
- `outputs/figures/random_forest_confusion_matrix.png`
- `outputs/figures/roc_curve_comparison.png`
- `outputs/figures/model_metric_comparison.png`
- `models/logistic_regression_model.joblib`
- `models/random_forest_model.joblib`

**First dataset:** sklearn Wisconsin Diagnostic Breast Cancer (public). Original labels `0 = malignant`, `1 = benign`. This project uses **1 = malignant** (positive class).

---

## Diabetes survey models (optional)

The interactive Python session does **not** save files. To write diabetes models to disk (uses your Kaggle cache; Random Forest can take several minutes):

```powershell
python -m src.train_diabetes
```

**Does not overwrite** breast-cancer files. Writes:

- `models/diabetes_logistic_regression_model.joblib`
- `models/diabetes_random_forest_model.joblib`
- `outputs/metrics/diabetes_classical_model_metrics.csv`
- `outputs/figures/diabetes_*.png`

Survey label only. Research risk classification - not for clinical use.

---

## White blood cell images (optional, separate from Phase 1)

This is a **different** experiment: a small CNN (~1 million weights) that labels **cell type** in a public microscope photo (5 classes). It does **not** replace `train_classical`, and it does **not** diagnose a person.

If PyTorch should use your NVIDIA GPU, install the CUDA wheel from [pytorch.org](https://pytorch.org) (Windows + Pip + CUDA), then:

```powershell
pip install kagglehub
python -m src.train_wbc
```

If the Kaggle images are not on disk yet, that command downloads `masoudnickparvar/white-blood-cells-dataset` (~500 MB).

**WBC outputs:**

- `models/wbc_cnn.pt`
- `outputs/metrics/wbc_cnn_metrics.csv`
- `outputs/figures/wbc_cnn_confusion_matrix.png`
- `outputs/figures/wbc_cnn_training_curves.png`

---

## What each metric means

Malignant is the **positive** class (`1`).

| Name | Meaning |
|------|---------|
| **TP / FN / TN / FP** | Hit / miss / correct benign / false alarm |
| **Accuracy** | Overall fraction correct (can hide misses) |
| **Precision** | Of predicted malignant, how many were malignant |
| **Recall / Sensitivity** | Of true malignant, how many were caught |
| **Specificity** | `TN / (TN + FP)` |
| **F1** | Balance of precision and recall |
| **ROC-AUC** | Ranking from `predict_proba[:, 1]`, not a clinical score |

Train/test split (80/20, stratified, `random_state=42`) exists so scores are on **unseen** rows. `StandardScaler` is used **only** for Logistic Regression, fit on **train** only (inside a Pipeline). Random Forest is not scaled.

---

## Phase 2 — feature selection

```powershell
python -m src.train_phase2
```

Fits `SelectKBest` (`mutual_info_classif`, `k=6`) on the **training** split only, retrains LR/RF on the reduced columns, and writes `outputs/reports/phase2_reproducibility.md`.

## Phase 3 — hybrid QML (simulator)

```powershell
pip install qiskit qiskit-aer qiskit-algorithms qiskit-machine-learning
python -m src.train_qml
python -m src.train_qml --with-qnn            # adds the EstimatorQNN track
python -m src.train_qml --skip-vqc            # fast kernel-only run
python -m src.train_qml_significance          # bootstrap CIs, McNemar, DeLong, repeated CV
python -m src.train_qml_ablation              # QSVC at k = 4, 6, 8
python -m src.train_qml_table coimbra         # second hybrid table
python -m src.train_qml_table ddd             # vertebral column (disk hernia / spondylolisthesis vs normal)
```

VQC (`ZZFeatureMap` + `RealAmplitudes`, COBYLA), QSVC (`FidelityStatevectorKernel`), and an optional **QNN** (`EstimatorQNN`, the PS's "or equivalent") on the **k=6** selected features, versus reduced logistic regression, random forest, and a classical **RBF SVM** control. Same split as Phase 1/2. MinMax scaling to `[0, 1]` is train-only.

Writes `outputs/metrics/qml_vs_classical_metrics.csv`, `qml_threshold_options.csv`, `qml_ablation_k.csv`, `outputs/reports/phase3_qml.md`, `phase3_ablation.md`, circuit notes, an optimizer trace, and a calibration curve (QSVC is Platt-scaled first, because `decision_function` is not a probability).

Quantum is **not** assumed to win; Wisconsin is often nearly linearly separable.

## Is the difference real? (statistics, not vibes)

The test split is **114 rows**, so a gap of a few thousandths of F1 is noise. `python -m src.train_qml_significance` quantifies it:

- **stratified bootstrap** 95% intervals per model (resampling within each class),
- **paired bootstrap** of the F1 *difference* (both models scored on the same resampled rows),
- **McNemar** on hard predictions and **DeLong** on the two ROC-AUCs,
- **repeated stratified CV** (5 × 5) with clipping, selection and scaling refit *inside every fold*.

Measured on this machine: QSVC F1 **0.950 [0.895, 0.988]** versus RBF SVM **0.951 [0.897, 0.988]**, McNemar **p = 1.000**, and every quantum-vs-classical F1 interval that involves QSVC contains zero. VQC and QNN are separated from the baselines (p < 0.001) — they are genuinely worse. So the honest claim is about **cost**, not accuracy.

Circuit models are not refitted here: predictions are recovered from the saved held-out scores at each estimator's own cutoff. VQC and QNN are excluded from cross-validation because 25 folds would take hours.

## Prediction and decision support

```powershell
python -m src.make_judge_sheet
streamlit run app/streamlit_app.py
```

The **Decision support** page shows the model's probability for **its own table's label**, a research band, and a **threshold slider** that trades recall against false positives on the held-out split. The **Explainability** page shows permutation importance, standardized coefficients, and one worked row.

This is deliberately **not** a differential diagnosis: there is no ranking across diseases, no test recommendation, and no combined per-person score. Each model only ever sees its own table's columns.

## Extra public tables (separate experiments)

```powershell
python -m src.train_tabular --list
python -m src.train_tabular cardio
python -m src.train_tabular all
```

One command = one table = one saved model. Not a fused “all diseases” product.

### Duplicate audit — why “more Kaggle CSVs” is usually not more data

```powershell
python -m src.audit_datasets
```

Public disease tables get re-uploaded constantly, and most “bigger” mirrors are the original rows repeated. An identical row landing in both train and test leaks the label. The audit measured it: **`heart_disease` (the `johnsmith88` mirror) is 70.5% duplicates** — 723 of 1025 rows repeat Cleveland's 302 patients. Its Random Forest previously scored a perfect **1.000** on every metric; after dropping duplicates it scores **F1 0.788**. `load_tabular_dataset` now drops exact duplicates by default.

Real growth needs **different patients**. `heart_uci_pooled` does that properly by combining the four UCI cohorts that share one schema:

| Cohort | Rows |
| --- | --- |
| Cleveland | 303 |
| Hungary | 294 |
| Switzerland | 123 |
| VA Long Beach | 200 |
| **Pooled (deduplicated)** | **918** |

```powershell
python -m src.train_tabular heart_uci_pooled
python -m src.train_qml_table heart_uci_pooled
```

That is 3× Cleveland alone, and it *helps honestly*: Random Forest reaches **F1 0.868 / ROC-AUC 0.919** on 918 real patients versus **F1 0.788** on the 302-row cohort. The site column is dropped from the features on purpose — prevalence differs sharply between hospitals, so a model given the cohort can just learn the site's base rate.

Row count is not the same as unique people. `cardio` is already ~69k after impossible-BP filters, and `python -m src.train_diabetes` uses ~253k BRFSS 2015 survey adults. A 15k EEG table is usually **one recording**, not 15k patients. The large unique-respondent table added here is CDC BRFSS **2020 heart-disease indicators** (`brfss_heart`, ~320k survey adults). It is **not** `cardio_train` and **not** the diabetes survey. Classical only:

```powershell
python -m src.train_tabular brfss_heart
python -m src.audit_datasets --keys brfss_heart cardio seizure
```

Added public tables (still separate): `coimbra`, `ddd`, `seizure`, `framingham`, `seer_breast`, `cervical`, `hepatitis`, `pcos`, `brfss_heart`.

```powershell
python -m src.train_tabular ddd
python -m src.train_tabular coimbra
python -m src.train_tabular seizure
python -m src.train_tabular framingham
python -m src.train_tabular seer_breast
python -m src.train_tabular cervical
python -m src.train_tabular hepatitis
python -m src.train_tabular pcos
python -m src.train_tabular brfss_heart
```

## Optional MSK images (not QML)

```powershell
python -m src.train_msk --list
python -m src.train_msk fracture --epochs 3 --max-per-class 200
python -m src.train_msk spine --epochs 3 --max-per-class 200
```

Labels exist only inside that Kaggle folder. Not all fractures or spinal injuries.

## LAKSHYA UI + API

The React app in `stitchfrontend/` talks to FastAPI. Build it, then start **one** server from the project root:

```powershell
cd stitchfrontend
npm install
npm run build
cd ..
.\.venv\Scripts\Activate.ps1
uvicorn src.api_server:app --reload --port 8000
```

Open `http://127.0.0.1:8000`. For live UI edits, run `npm run dev` in `stitchfrontend` (port 3000) with the API on 8000. Paste-a-record posts to `/v1/research-record`; locked PDF uses `/v1/research-report`. Train first:

```powershell
python -m src.train_phase2
python -m src.train_tabular heart_uci_pooled
python -m src.train_tabular pima
```

One table = one label. Not a multi-disease score.

Optional Streamlit research dashboard:

```powershell
streamlit run app/streamlit_app.py
```

## Research notes mapper (optional, NVIDIA NIM)

Translates **synthetic notes or a text PDF** into fields for **existing catalog tables**, then may show a **research positive-class %** from a saved `.joblib` if enough columns are filled. Tries NVIDIA NIM first (`NVIDIA_MODEL`, then fallbacks). If chat is 403/410, a **local `feature: number` extractor** still maps fields. Not a diagnosis. Not a doctor directory.

```powershell
copy .env.example .env
# Put NVIDIA_API_KEY in .env (never commit .env)

pip install fastapi uvicorn httpx pypdf python-dotenv openai
uvicorn src.api_server:app --reload --port 8000
```

In another terminal:

```powershell
streamlit run app/streamlit_app.py
```

Open **Research notes mapper**. Endpoints: `POST /v1/research-map`, `POST /v1/research-score`, `POST /v1/research-report`, `GET /health`.

**Locked research PDF** (not a medical record): on Paste a record, enter name and date of birth as labels, paste `field: number` lines, then **Generate locked PDF**. The file opens only with a **generated key** (shown once). Name/DOB are not the password.

Optional Supabase (server only):

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

Run [supabase/migrations/001_report_unlock_keys.sql](supabase/migrations/001_report_unlock_keys.sql) in the SQL editor. If these env vars are empty, the PDF still downloads and the key is shown once; nothing is stored.

Demo with made-up numbers that match a schema (for example Wisconsin FNA fields). Do not upload real hospital records.

UI design notes: [PRD.md](PRD.md) Section 10 and [task.md](task.md).
