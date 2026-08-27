# Product Requirements Document (PRD)

**Product name:** Q-Care Detect — Hybrid Quantum Machine Learning Platform for Early Disease Detection  
**Document type:** Product Requirements Document  
**Version:** 0.1 (documentation only)  
**Status:** Active for planning; software not implemented yet  
**Audience:** Project owner (beginner) and future contributors

This PRD describes **what** the product should do and **why**. It is not source code. Implementation happens phase by phase. Frontend is specified in [Section 10](#10-frontend--design-and-skeleton) and must **not** be built until Phase 5.

---

## 1. Vision and problem

### 1.1 Vision

Build a **research and educational** platform that compares:

- classical machine learning models, and
- hybrid quantum-classical machine learning models

on **binary disease-risk classification** using **public benchmark data**.

The platform should help a beginner understand:

- how a clean ML pipeline is structured,
- why evaluation needs more than accuracy,
- why train/test splits and scaling rules matter,
- and how a quantum model can be compared **fairly** to a classical model — not marketed as automatically superior.

### 1.2 Problem

Tutorials often:

- report only accuracy,
- mix training and test information (data leakage),
- jump to quantum libraries before a classical baseline exists,
- or present medical-sounding outputs that a reader could mistake for a diagnosis.

Q-Care Detect exists to avoid those mistakes in a small, reproducible project.

### 1.3 Product type

This is **not**:

- a medical device,
- a clinical decision-support system,
- a hospital integration,
- a patient portal.

This **is**:

- an academic/research prototype,
- a teaching codebase,
- a comparison bench for classical ML vs QML on a public dataset.

---

## 2. Goals and non-goals

### 2.1 Goals

| ID | Goal |
|----|------|
| G1 | Provide a reproducible classical baseline (Phase 1) before any quantum work. |
| G2 | Evaluate models with a full metric set: accuracy, precision, recall/sensitivity, specificity, F1, ROC-AUC, confusion matrix. |
| G3 | Keep malignant as the positive class after label conversion. |
| G4 | Prevent data leakage (split first; fit scalers on train only). |
| G5 | Later, compare hybrid QML (VQC, QSVC) to classical models with the same split and metrics. |
| G6 | Always label outputs as research risk classification, never diagnosis. |
| G7 | Stay beginner-readable: clear names, functions, docstrings, pathlib, no unnecessary complexity. |

### 2.2 Non-goals (do not build these in early phases)

| ID | Non-goal |
|----|----------|
| NG1 | Clinical diagnosis, treatment advice, or “patient result” workflows. |
| NG2 | Real hospital or patient-identifiable data. |
| NG3 | Claiming quantum models are automatically better. |
| NG4 | Frontend, cloud deployment, authentication, database, or public API in Phases 1–4. |
| NG5 | Installing Qiskit or training quantum models before Phase 3. |
| NG6 | Docker, Kubernetes, or production MLOps in Phase 1. |
| NG7 | Unnecessary boilerplate files not required by the current phase. |

---

## 3. Safety, ethics, and language rules

These rules apply to code, notebooks, README, UI copy, plots, and reports.

### 3.1 Required disclaimer

Use this text in the README and in any user-facing surface:

> This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.

### 3.2 Required prediction label

Every prediction, metric summary, plot title area, and future UI result must include:

**Research risk classification — not for clinical use.**

### 3.3 Language — required vs forbidden

| Use these | Do not use these |
|-----------|------------------|
| Research risk classification | Diagnosis / diagnosed |
| Predicted class (malignant vs benign) on a public benchmark | Patient is sick / patient is healthy |
| Model comparison / research prototype | Medical device / FDA / clinically validated (unless independently true, which this project is not) |
| Sensitivity / recall on the test set | Screening tool for clinics |
| Public benchmark dataset | Hospital records / my patients |

Do **not** claim quantum advantage unless a later, carefully designed experiment actually shows a specific, scoped result — and even then, do not generalize to clinical care.

### 3.4 Data ethics

- Initial versions: **public benchmark data only** (sklearn Wisconsin Diagnostic Breast Cancer).
- No names, medical record numbers, photos, or hospital exports.
- No scraping of private health information.

---

## 4. Users

| User | Needs | Does not need |
|------|--------|----------------|
| **Student / beginner** | Step-by-step explanations, a single terminal command to run the baseline, plots that are easy to read | Production deployment, login, GPU cluster |
| **Researcher / reviewer** | Reproducible split (`random_state=42`), saved metrics CSV, fair comparison protocol | A clinical UI |
| **Future UI visitor (Phase 5)** | Plain-language comparison of models, always-visible disclaimer | Ability to upload real patient files |

There is no “clinician user” and no “patient user” in this product definition.

---

## 5. Data requirements

### 5.1 Initial dataset

**Source:** scikit-learn built-in Wisconsin Diagnostic Breast Cancer dataset.

**Required load pattern:**

```python
from sklearn.datasets import load_breast_cancer
data = load_breast_cancer(as_frame=True)
X = data.data
# Original target: 0 = malignant, 1 = benign
y_binary = (data.target == 0).astype(int)
# After conversion: 1 = malignant / disease present, 0 = benign / disease absent
```

| Property | Value |
|----------|--------|
| Type | Tabular, numeric features |
| Feature count (raw) | 30 |
| Task | Binary classification |
| Positive class after conversion | Malignant (1) |
| Identifiable patients | No (public toy/benchmark set) |

**Why this dataset:** small, structured, easy to load, suitable for a beginner prototype. Later phases reduce features to **4–8** so a quantum model can use them (quantum circuits do not handle 30 raw features well in a beginner setup).

### 5.2 Train/test split (Phase 1)

```python
train_test_split(
    X,
    y_binary,
    test_size=0.20,
    random_state=42,
    stratify=y_binary,
)
```

- 80% training, 20% testing.
- Stratify so both classes appear in both sets.
- Same `random_state` everywhere it is supported (42).

### 5.3 Future data

Later optional public benchmarks may be added. Hospital data is out of scope unless a separate ethics and legal process exists — **not** part of this PRD.

---

## 6. Phased functional requirements

### 6.1 Phase 1 — Classical ML baseline (next implementation)

**Objective:** A clean, reproducible classical baseline. No Qiskit. No UI. No API.

The system shall:

1. Load the breast cancer dataset as specified in Section 5.
2. Inspect and print a beginner-friendly dataset summary (rows, columns, class counts).
3. Convert the target so malignant is the positive class.
4. Create the stratified 80/20 split (`random_state=42`).
5. Preprocess correctly:
   - `StandardScaler` for Logistic Regression only.
   - Fit scaler on **training data only** (via a scikit-learn `Pipeline`).
   - Random Forest: no scaler.
6. Train:
   - `LogisticRegression(max_iter=5000, random_state=42)` inside  
     `Pipeline([("scaler", StandardScaler()), ("classifier", LogisticRegression(...))])`
   - `RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")`
7. Evaluate both models with: accuracy, precision, recall/sensitivity, specificity, F1, ROC-AUC, confusion matrix.
8. Save visualizations:
   - confusion matrix heatmap per model,
   - ROC curve comparing both models,
   - bar chart of main metrics.
9. Save artifacts listed in Section 8.
10. Print a beginner-friendly summary of which model scored better **on this test set** and why, without claiming clinical superiority.

**Terminal entry point:**

```text
python -m src.train_classical
```

**Packages:** pandas, numpy, scikit-learn, matplotlib, seaborn, joblib, pytest, jupyter.

**Tests (minimum):**

1. Dataset loads successfully.
2. Train/test split preserves both target classes.
3. Metric evaluation returns values between 0 and 1.

**Code quality:** functions (not one script dump), type hints where reasonable, docstrings on public functions, pathlib (no hard-coded absolute paths), auto-create output directories, useful error messages, beginner-readable.

Phase 1 is **complete** only after the owner runs the pipeline and confirms with: **“Phase 1 is working.”**

### 6.2 Phase 2 — Evaluation, feature selection, reproducibility

Shall add (details to be refined when Phase 1 is done):

- Stronger reporting and plot polish as needed.
- Feature selection / reduction from 30 features to about **4–8** features for later QML.
- Reproducibility notes (seeds, package versions, how to rerun).

Do not start Phase 2 until Phase 1 is confirmed working.

### 6.3 Phase 3 — Hybrid QML (VQC and QSVC)

Shall add hybrid quantum-classical models using VQC and QSVC (Qiskit or agreed stack), on the reduced feature set, with the **same** split protocol and metrics as classical models.

Shall **not** claim quantum is better by default. Report wins, losses, and ties honestly (including runtime and instability).

Do not install Qiskit in Phase 1.

### 6.4 Phase 4 — Explainability and reports

Shall add explanations of *why* a model leaned toward a class (for example classical feature importance / SHAP-style methods if chosen) and a generated research-style report. Still not a clinical report.

### 6.5 Phase 5 — Simple Streamlit UI

Shall implement the frontend specified in [Section 10](#10-frontend--design-and-skeleton). Read-only exploration of existing results first; no hospital upload.

### 6.6 Phase 6 — Optional FastAPI and deployment

Optional. Only if explicitly requested. Not required for the research prototype to be valid.

---

## 7. Metrics and fair comparison

### 7.1 Positive class

Malignant = positive (`1`).

- **True Positive:** malignant predicted malignant  
- **False Negative:** malignant predicted benign  
- **Sensitivity / Recall:** `TP / (TP + FN)`  
- **Specificity:** `TN / (TN + FP)` from  
  `tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()`

### 7.2 ROC-AUC

Must use probabilities, not hard labels:

```python
y_prob = model.predict_proba(X_test)[:, 1]
```

### 7.3 Fairness of comparison (all phases)

To compare Model A and Model B:

| Rule | Why |
|------|-----|
| Same train/test split | Otherwise you are not comparing models; you are comparing luck |
| Same label definition | Positive class must mean the same thing |
| Same metric definitions | Recall vs accuracy arguments stay honest |
| Same feature set when claiming a head-to-head | A 30-feature RF vs a 4-qubit VQC is a different experiment unless labeled as such |
| Report limitations | Small public dataset ≠ clinical performance |

Phase 3 must document when QML uses fewer features than the classical 30-feature baseline.

---

## 8. Technical architecture

### 8.1 Now (v0.1)

```text
qml/
├── README.md    # beginner how-to
└── PRD.md       # this document
```

### 8.2 Target after Phase 1 (planned)

See README “Planned folder structure.” Core modules:

| Module | Responsibility |
|--------|----------------|
| `src/utils.py` | Project root, pathlib paths, create output folders |
| `src/data_loader.py` | Load dataset, relabel target, inspect |
| `src/preprocessing.py` | Stratified split |
| `src/evaluate.py` | Metrics, plots, CSV, beginner summary text |
| `src/train_classical.py` | CLI entry: train, save `.joblib`, evaluate |

Random Forest is **not** scaled. Logistic Regression **is** scaled inside a Pipeline.

### 8.3 Planned Phase 1 artifacts

| File | Description |
|------|-------------|
| `outputs/metrics/classical_model_metrics.csv` | Metric table |
| `outputs/figures/logistic_regression_confusion_matrix.png` | LR confusion heatmap |
| `outputs/figures/random_forest_confusion_matrix.png` | RF confusion heatmap |
| `outputs/figures/roc_curve_comparison.png` | Both models on one ROC plot |
| `outputs/figures/model_metric_comparison.png` | Bar chart of main metrics |
| `models/logistic_regression_model.joblib` | Saved LR pipeline |
| `models/random_forest_model.joblib` | Saved RF |

### 8.4 Later architecture (not now)

- Phase 3: additional `src` modules for QML; Qiskit in `requirements` only then.  
- Phase 5: Streamlit app, likely `app/` or `src/app.py`.  
- Phase 6: optional FastAPI; still no requirement for a database in the research prototype.

---

## 9. Success criteria

### 9.1 Documentation (this version)

- [x] README exists and is beginner-friendly.  
- [x] PRD exists, includes safety rules, phases, and a frontend section.  
- [ ] Owner has read both files and agrees they match the intended project.

### 9.2 Phase 1 software (future)

- [ ] `python -m src.train_classical` runs from the project root.  
- [ ] All artifact files in Section 8.3 exist after a run.  
- [ ] Tests pass (`pytest`).  
- [ ] Disclaimer text appears in printed output.  
- [ ] Owner confirms: **“Phase 1 is working.”**

### 9.3 Product-level (later)

- Classical and QML results can be compared on agreed metrics without changing the label definition.  
- No screen or report presents a diagnosis.

---

## 10. Frontend — design and skeleton

**Status: specification only. Do not implement until Phase 5.**

This section tells a future implementer **how to design** the UI and what the **basic skeleton** is. It does not authorize building React, Streamlit, or any webpage in Phase 1.

### 10.1 Purpose of the UI

The UI exists so a beginner can **see** the research comparison without running Python in their head.

It must:

- show disclaimers first,
- show classical (and later quantum) metrics side by side,
- explain plots in short sentences,
- make it obvious this is a classroom/research tool.

It must **not**:

- look like a hospital EHR or emergency dashboard,
- accept real patient records,
- print “You have cancer” / “You are safe,”
- hide uncertainty or test-set limitations.

### 10.2 Design principles

| Principle | What to do |
|-----------|------------|
| **Safety first** | Persistent banner: educational only; not a medical device; research risk classification |
| **Comparison first** | The main page is “Model A vs Model B,” not a single scary score |
| **Plain language** | Tooltips or one-line definitions next to Accuracy, Recall, etc. |
| **Academic, calm visual tone** | Neutral background, readable type, no red siren “ALERT” styling for predicted class |
| **One primary action per page** | Example: “Show classical results” — not ten competing buttons |
| **Color is not the only signal** | Confusion matrices and ROC still readable if printed in grayscale |
| **Honest empty states** | If Phase 3 is not run yet, say “Quantum results not generated yet” instead of fake numbers |

### 10.3 Tool choice (Phase 5)

**Streamlit** — Python-only, fits this repo, no separate JavaScript app in the first UI.

Out of scope for Phase 5: custom React SPA, authentication, cloud hosting, payment, user accounts.

### 10.4 Information architecture (sitemap)

```text
Q-Care Detect (Streamlit)
├── Home
├── Data overview
├── Classical results
├── QML comparison      (visible but disabled or placeholder until Phase 3+5)
├── How to read metrics
└── About and limits
```

| Page | Job | Must show disclaimer? |
|------|-----|------------------------|
| **Home** | What the project is, current phase, link to run instructions | Yes |
| **Data overview** | Dataset name, row/column counts, class balance, “public benchmark only,” label conversion explained | Yes |
| **Classical results** | LR vs RF cards, metrics table, two confusion matrices, shared ROC, bar chart | Yes |
| **QML comparison** | Same metric layout for VQC / QSVC vs classical; note feature-count differences | Yes |
| **How to read metrics** | Beginner definitions (same spirit as README) | Yes |
| **About and limits** | Not for clinical use; small dataset; no quantum-auto-win claim | Yes |

### 10.5 Page skeleton — Home

```text
+--------------------------------------------------+
| BANNER: Educational research only. Not a device. |
| Research risk classification — not for clinical  |
| use.                                             |
+--------------------------------------------------+
| Q-Care Detect                                    |
| Short paragraph: compare classical vs QML.       |
| Current phase badge: e.g. "Phase 1 planned"      |
| [Open data overview]  [Open classical results]   |
| Footer: never used for diagnosis.                |
+--------------------------------------------------+
```

### 10.6 Page skeleton — Classical results (main comparison layout)

This is the primary wireframe for Phase 5.

```text
+----------------------------------------------------------+
| BANNER (always visible while scrolling if Streamlit      |
| allows; otherwise repeat at top of page)                 |
+----------------------------------------------------------+
| Title: Classical model comparison                        |
| Subtitle: Wisconsin Diagnostic Breast Cancer (public)    |
| Caption: Test set only. Not for clinical use.            |
+---------------------------+------------------------------+
| Logistic Regression       | Random Forest                |
| Accuracy …                | Accuracy …                   |
| Precision …               | Precision …                  |
| Recall …                  | Recall …                     |
| Specificity …             | Specificity …                |
| F1 …                      | F1 …                         |
| ROC-AUC …                 | ROC-AUC …                    |
+---------------------------+------------------------------+
| Confusion matrix (LR)     | Confusion matrix (RF)        |
+---------------------------+------------------------------+
| ROC curve (both models, one plot)                        |
| Metric bar chart                                         |
+----------------------------------------------------------+
| Beginner note: which model looked stronger on THIS       |
| test split and which metric you should not over-trust.   |
+----------------------------------------------------------+
```

### 10.7 Page skeleton — Data overview

- Dataset official name and sklearn source.  
- Number of samples and features.  
- Count of malignant vs benign **after** relabeling.  
- Sentence: original sklearn `0` was malignant; we mapped malignant to `1`.  
- No patient IDs (there are none).  
- Optional: simple histogram or table of a few feature names — educational, not diagnostic.

### 10.8 Component checklist (Phase 5)

| Component | Required |
|-----------|----------|
| Disclaimer banner | Yes, all pages |
| “Research risk classification — not for clinical use.” | Yes, on every results view |
| Metric cards (one per model) | Yes |
| Metrics table (CSV-backed once Phase 1 exists) | Yes |
| Confusion matrix images | Yes |
| ROC comparison image | Yes |
| Metric bar chart | Yes |
| Download metrics CSV | Nice-to-have |
| File uploader for hospital CSV | **No** |
| Login | **No** |
| “Diagnose this patient” form | **No** |

### 10.9 Copy rules for the UI

**Required snippets**

- “This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.”
- “Research risk classification — not for clinical use.”
- “Scores are computed on a held-out public test split. They are not clinical performance.”

**Forbidden UI copy**

- Diagnose, diagnosis, treatment plan, prescribe  
- Patient portal, medical record, upload hospital data  
- “Quantum proven better,” “replaces a doctor,” “FDA cleared”  
- Green/red “SAFE” / “CANCER” stamps on a single prediction as if it were a lab result

**Tone:** calm, specific, slightly academic. Short sentences. Define jargon next to the first use.

### 10.10 Visual design notes (basic)

- **Typography:** large enough body text; avoid tiny metric footnotes as the only disclaimer.  
- **Layout:** generous spacing; two columns on desktop for model cards; stack on a narrow window.  
- **Plots:** reuse Phase 1 PNGs first (simplest). Interactive Plotly can wait.  
- **Theme:** light, neutral; one accent color for charts — not blood-red “clinical alert” palettes.  
- **Accessibility:** text alternatives for plots (“Confusion matrix for logistic regression on the test set”). Do not encode class only as color.

### 10.11 Interaction rules

- Default page: Home.  
- Classical results should load **saved artifacts** from `outputs/` and `models/` when they exist; if missing, show: “Run `python -m src.train_classical` first.”  
- Do not retrain a heavy model on every Streamlit rerun unless the user clicks an explicit “Retrain” (Phase 5 can stay read-only).  
- No hidden network calls to send data off the machine in Phase 5.

### 10.12 What frontend is explicitly out of scope

- Authentication and user accounts  
- Databases of patients  
- Cloud deployment (Phase 6 is optional and separate)  
- Mobile native apps  
- Real-time camera or wearable input  
- Any workflow that looks like submitting a case to a clinician

### 10.13 Frontend success criteria (Phase 5 only)

- A new user can open Streamlit, read the disclaimer, and understand they are not using a diagnostic product.  
- They can compare LR vs RF on the same screen.  
- Later, they can compare classical vs QML with the same metric names.  
- No page omits the research-use label.

---

## 11. Open questions (decide later, not in Phase 1)

| Topic | Question |
|-------|----------|
| Feature selection method | Which algorithm reduces 30 features to 4–8 (mutual information, model-based importance, domain list)? |
| QML backend | Exact Qiskit / Aer versions and simulator vs hardware (hardware not required for the prototype). |
| Class weight on Logistic Regression | Phase 1 spec does not set `class_weight` on LR; only RF is `"balanced"`. Revisit in Phase 2 if class imbalance analysis says so. |
| Streamlit hosting | Local only vs optional later deploy (Phase 6). |
| Extra datasets | Whether to add a second public dataset after breast cancer. |

---

## 12. Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-28 | Initial PRD: full roadmap, safety rules, Phase 1 requirements, frontend design skeleton. Software not implemented. |

---

## 13. Next action

1. Read [README.md](README.md) and this PRD.  
2. When ready for code, implement **Phase 1 only** (classical baseline).  
3. Do not start Phase 2 or Phase 3 until you confirm: **“Phase 1 is working.”**  
4. Do not build the frontend until Phase 5 is explicitly started.
