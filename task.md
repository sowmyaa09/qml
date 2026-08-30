# Frontend build task — Q-Care Detect

**This file is frontend-only.** It does not cover training models, Qiskit, FastAPI, Docker, login, or a database.

Use this document when you are ready to **generate or implement the user interface**. Full product rules live in [PRD.md](PRD.md) Section 10. Project background lives in [README.md](README.md).

---

## What you are building

A **local Streamlit app** so a beginner can look at research results without reading Python files.

The app compares machine learning models on a **public** breast-cancer benchmark. It is **not** a clinic tool.

**Tech stack (required — do not change unless the project owner says so):**

| Layer | Choice |
|--------|--------|
| UI framework | **Streamlit** (Python) |
| Charts / images | Streamlit `st.image` for saved PNGs; optional `st.dataframe` for CSV |
| Data the UI reads | Files under `outputs/` (metrics CSV + figure PNGs). If those files do not exist yet, show a clear empty state |
| Styling | Streamlit layout + light custom CSS only if needed. No React, Next.js, Vue, or separate Node app |
| Hosting | Local only: `streamlit run ...` |
| Auth / DB / cloud | **None** |

---

## How to build it (human checklist)

Do these in order when you implement the UI (not before the owner asks):

1. Create `app/streamlit_app.py` (or `src/app.py`) as the Streamlit entry point.
2. Add a **sidebar** with page names: Home, Data overview, Classical results, QML comparison, How to read metrics, About and limits.
3. Put the **disclaimer banner on every page**.
4. Home: purpose, “not a medical device,” current phase, links to other pages.
5. Data overview: sklearn Wisconsin dataset, 30 features, label conversion (1 = malignant), public data only. No file upload.
6. Classical results: two metric cards (Logistic Regression vs Random Forest), confusion matrices, ROC image, bar chart. Load from `outputs/` when present.
7. QML comparison: **placeholder** until quantum results exist (“Quantum results not generated yet”). Do not invent numbers.
8. How to read metrics: short definitions (accuracy, precision, recall, specificity, F1, ROC-AUC).
9. About: limits, no “quantum is automatically better,” not for clinical use.
10. Run locally: `streamlit run app/streamlit_app.py`

**Empty state:** if `outputs/metrics/classical_model_metrics.csv` is missing, say: run `python -m src.train_classical` first. Do not crash.

---

## Safety rules (must appear in the generated UI)

- This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.
- Every results view: **Research risk classification — not for clinical use.**
- Never say diagnosis, treat, patient portal, or “you have cancer.”
- No hospital CSV upload. No login. No fake clinical stamps (SAFE / CANCER).

---

## Pages (skeleton)

```text
Q-Care Detect (Streamlit)
├── Home
├── Data overview
├── Classical results      ← main comparison screen
├── QML comparison         ← placeholder until QML exists
├── How to read metrics
└── About and limits
```

**Classical results layout (most important screen):**

```text
Disclaimer banner (full width)
Title + “public test set only”
[ Logistic Regression metrics ] [ Random Forest metrics ]
[ LR confusion PNG ]            [ RF confusion PNG ]
ROC comparison PNG (full width)
Metric bar chart PNG (full width)
Short beginner note: scores are for THIS test split only
```

Visual tone: calm, academic, light background. Not a hospital dashboard. Not red-alert “clinical” styling.

---

## How to use the prompt below

1. Open Cursor (or another coding assistant) in this repo.
2. Copy **everything inside the box** in the next section (from `BEGIN FRONTEND PROMPT` to `END FRONTEND PROMPT`).
3. Paste it as a new chat message.
4. Add one line if you want: `Implement this now in the qml repo.`
5. Do **not** ask the assistant to train models or install Qiskit in the same request.

---

## Copy-paste prompt (generate the frontend)

Copy from the next line through `END FRONTEND PROMPT`.

```text
BEGIN FRONTEND PROMPT

You are a senior Python + Streamlit engineer. I am a beginner.

Build ONLY the frontend for this project. Do not train ML models. Do not install Qiskit. Do not add FastAPI, Docker, authentication, a database, or cloud deployment. Do not create a React/Next.js/Vue app.

PROJECT
Q-Care Detect — research/educational UI that shows a comparison of classical ML models (and later hybrid QML) on a public benchmark. This is NOT a medical device.

TECH STACK (mandatory)
- Streamlit (Python)
- Read local files with pathlib (no hard-coded absolute paths)
- pandas only to display a metrics CSV if it exists
- Display PNG plots with st.image
- No Plotly requirement (optional later)
- Entry point: app/streamlit_app.py
- Multipage: use st.sidebar radio or Streamlit pages in app/pages/ — pick one pattern and keep it simple
- Add streamlit to requirements if a requirements.txt exists; if it does not exist, create a small requirements-frontend.txt with streamlit and pandas only

SAFETY COPY (must appear)
1) Banner on EVERY page:
“This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.”
2) On every results-related page also show:
“Research risk classification — not for clinical use.”
3) Also show:
“Scores are computed on a held-out public test split. They are not clinical performance.”

FORBIDDEN
- Words: diagnosis, diagnose, treatment, prescribe, patient portal, medical record
- File uploader for hospital/patient data
- Login, signup, cookies for accounts
- Claiming quantum models are automatically better
- Green/red SAFE vs CANCER stamps
- Inventing metric numbers if files are missing
- Calling predictions a diagnosis

PAGES TO IMPLEMENT
1) Home
   - Project name: Q-Care Detect
   - One short paragraph: compares classical ML vs later hybrid QML for binary disease-RISK classification on public data
   - Current status note: UI may exist before models; if outputs are missing, say so honestly
   - Buttons or links to Data overview and Classical results
   - Footer: never used for diagnosis (rephrase without the forbidden word: “never used for clinical decisions”)

2) Data overview
   - Dataset: scikit-learn Wisconsin Diagnostic Breast Cancer (public)
   - 30 numeric features; binary labels
   - Explain label conversion in simple words:
     original sklearn target 0 = malignant, 1 = benign;
     this project uses 1 = malignant / disease present, 0 = benign / disease absent
   - Say there are no patient names or hospital IDs
   - Optional: list a few feature names as educational text, not as a diagnostic form
   - NO user input to classify a person

3) Classical results (main page)
   - Two columns: Logistic Regression vs Random Forest
   - Metrics: Accuracy, Precision, Recall/Sensitivity, Specificity, F1-score, ROC-AUC
   - Load outputs/metrics/classical_model_metrics.csv if present
   - Images if present:
     outputs/figures/logistic_regression_confusion_matrix.png
     outputs/figures/random_forest_confusion_matrix.png
     outputs/figures/roc_curve_comparison.png
     outputs/figures/model_metric_comparison.png
   - If files missing: friendly message “Run python -m src.train_classical from the project root first.” Do not crash
   - Beginner caption: which model looks stronger on THIS test split is not a clinical conclusion
   - Optional: download button for the CSV if the file exists

4) QML comparison
   - Placeholder page
   - Explain future VQC and QSVC comparison using the SAME metric names
   - Text: “Quantum results not generated yet. Phase 3 is not built. We do not assume quantum is better.”
   - No fake charts

5) How to read metrics
   - Simple definitions:
     Accuracy = overall fraction correct (can hide misses)
     Precision = of predicted malignant, how many were malignant
     Recall/Sensitivity = of true malignant, how many were caught (TP/(TP+FN))
     Specificity = of true benign, how many were called benign (TN/(TN+FP))
     F1 = balance of precision and recall
     ROC-AUC = ranking quality from probabilities, not a diagnosis
   - Confusion matrix: TP, FP, FN, TN in one short paragraph
   - Malignant is the positive class

6) About and limits
   - Educational/research only
   - Small public dataset ≠ hospital performance
   - No quantum auto-win claim
   - No API, no cloud, no patient data

DESIGN
- Calm academic look: light background, readable font, generous spacing
- Not a hospital EHR, not emergency-red alerts
- Disclaimer at the top of every page (st.warning or a custom banner)
- Wide layout: st.set_page_config(layout="wide")
- Two columns for model cards on Classical results
- Alt text / captions on images
- Color not the only meaning

BEHAVIOR
- Default page: Home
- Do not retrain models on Streamlit rerun
- Do not send data to the internet
- Create output/app folders only if needed for the UI; do not generate fake PNG/CSV artifacts

CODE QUALITY
- Beginner-readable functions
- Type hints where reasonable
- Docstrings on public functions
- pathlib relative to project root
- Clear error messages
- No unnecessary complexity

DELIVER
- Complete Streamlit app that runs with: streamlit run app/streamlit_app.py
- Brief comment at top of the main file with how to run it
- Do not implement backend training in this task

END FRONTEND PROMPT
```

---

## After the UI is generated (owner checklist)

Run (when Streamlit is installed):

```powershell
cd c:\Projects\qml
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install streamlit pandas
streamlit run app/streamlit_app.py
```

Check:

- [ ] Disclaimer is on every page  
- [ ] No diagnosis language  
- [ ] No file upload for patients  
- [ ] Classical page does not crash if `outputs/` is empty  
- [ ] QML page is a placeholder, not fake scores  

When the training pipeline exists, run `python -m src.train_classical` once, refresh the app, and confirm plots and the metrics table appear.

---

## Related docs

| File | Use for |
|------|---------|
| [PRD.md](PRD.md) Section 10 | Full frontend spec (wireframes, components, out of scope) |
| [README.md](README.md) | Project purpose, metrics explained, medical disclaimer |
| This file (`task.md`) | Frontend-only build steps + generation prompt |
