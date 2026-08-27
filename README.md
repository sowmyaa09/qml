# Q-Care Detect

**Hybrid Quantum Machine Learning Platform for Early Disease Detection**

Q-Care Detect is a research and educational software project. It compares **classical machine learning models** with **hybrid quantum-classical machine learning models** on a public medical benchmark dataset.

The goal is a **fair, reproducible comparison** — not a hospital product, and not a claim that quantum models are automatically better.

> **Current status:** This repository currently contains documentation only (`README.md` and `PRD.md`). The Python training pipeline, notebooks, and user interface are planned next. See [What is built today](#what-is-built-today).

---

## Medical and ethical disclaimer

**This project is for educational and research purposes only. It is not a medical device and must not be used for clinical diagnosis or treatment decisions.**

Additional rules this project will always follow:

- Predictions are **research risk classification**, never a diagnosis.
- Every prediction surface must show: **“Research risk classification — not for clinical use.”**
- Do not treat model output as medical advice.
- Do not use patient-identifiable or hospital data.
- Use only public benchmark datasets for the initial versions.
- Do not claim that quantum models are automatically better than classical models.

---

## Project purpose

Many machine learning tutorials stop at “the accuracy was high.” This project goes further, in a beginner-friendly way:

1. Train simple **classical** models (starting with Logistic Regression and Random Forest).
2. Measure them with several metrics, not just accuracy (because missing a malignant case is more serious than a wrong “benign” guess in a research comparison).
3. Later, train **hybrid quantum-classical** models (VQC and QSVC) on a **reduced** set of features.
4. Compare both families of models using the **same data split, same metrics, and same evaluation rules**.

The first dataset is scikit-learn’s built-in **Wisconsin Diagnostic Breast Cancer** dataset. It is small, public, fully numeric, and suitable for a prototype. Original labels are `0 = malignant` and `1 = benign`. The project will convert the target so that:

- **1 = malignant / disease present** (the positive class)
- **0 = benign / disease absent**

That conversion exists so “positive” means the medically important class when we compute recall, precision, and related metrics.

---

## What is built today

| Item | Status |
|------|--------|
| README (this file) | Done |
| Product Requirements Document ([PRD.md](PRD.md)) | Done |
| Python source code (`src/`) | Not yet |
| Tests | Not yet |
| Jupyter notebook | Not yet |
| Trained models and plots | Not yet |
| Quantum models (Qiskit) | Not yet — Phase 3 |
| Streamlit user interface | Not yet — Phase 5 |
| FastAPI / cloud / login / database | Not planned for early phases |

The full product plan, including a **frontend design skeleton**, lives in [PRD.md](PRD.md).

---

## Planned folder structure

When Phase 1 code is added, the repository is intended to look like this:

```text
quantum-disease-detection/
│
├── README.md
├── PRD.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── 01_classical_baseline.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── train_classical.py
│   ├── evaluate.py
│   └── utils.py
│
├── models/
│
├── outputs/
│   ├── figures/
│   ├── metrics/
│   └── reports/
│
└── tests/
    └── test_pipeline.py
```

You do not need this tree yet. It is listed so you can see where each piece will live.

**What each planned folder is for (plain language):**

| Path | Purpose |
|------|---------|
| `src/` | Reusable Python functions: load data, split, train, evaluate |
| `notebooks/` | Step-by-step learning notebook (optional; the main run path is the terminal) |
| `data/` | Placeholders for saved tables later (Phase 1 loads data from scikit-learn, not from hospital files) |
| `models/` | Saved trained models (`.joblib` files) |
| `outputs/figures/` | PNG plots (confusion matrices, ROC curve, metric bars) |
| `outputs/metrics/` | CSV table of scores |
| `outputs/reports/` | Written summaries in later phases |
| `tests/` | Automated checks so the pipeline does not silently break |

---

## Roadmap

| Phase | What it is | Status |
|-------|------------|--------|
| **1** | Classical ML baseline (Logistic Regression + Random Forest) | Planned next |
| **2** | Stronger evaluation, plots, feature selection (about 4–8 features), reproducibility | Later |
| **3** | Hybrid QML models (VQC and QSVC) | Later — do not install Qiskit until then |
| **4** | Explainability and report generation | Later |
| **5** | Simple Streamlit user interface | Later |
| **6** | Optional FastAPI backend and deployment | Optional / later |

We will not start Phase 2 until Phase 1 is working. We will not install Qiskit or build a UI during Phase 1.

---

## Installation (after Phase 1 code exists)

These commands will apply once `requirements.txt` and the `src/` package are added. They will not work on a documentation-only checkout.

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

If PowerShell blocks activation, you may need:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Planned packages include: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `joblib`, `pytest`, and `jupyter`.

---

## How to run the project (after Phase 1 code exists)

From the project root, with the virtual environment activated:

```powershell
python -m src.train_classical
```

This command is the intended main entry point. It should:

1. Load the breast cancer dataset.
2. Convert labels so malignant is the positive class.
3. Split data 80% train / 20% test (stratified, `random_state=42`).
4. Train Logistic Regression (with `StandardScaler` inside a Pipeline) and Random Forest.
5. Print metrics and a beginner-friendly comparison.
6. Save models, a metrics CSV, and PNG plots.

Run tests with:

```powershell
pytest
```

Open the learning notebook (optional) with:

```powershell
jupyter notebook notebooks/01_classical_baseline.ipynb
```

**Planned output files after a successful Phase 1 run:**

- `outputs/metrics/classical_model_metrics.csv`
- `outputs/figures/logistic_regression_confusion_matrix.png`
- `outputs/figures/random_forest_confusion_matrix.png`
- `outputs/figures/roc_curve_comparison.png`
- `outputs/figures/model_metric_comparison.png`
- `models/logistic_regression_model.joblib`
- `models/random_forest_model.joblib`

---

## What each metric means

Malignant is the **positive** class (`1`). Benign is the **negative** class (`0`).

Imagine the model looks at one row and says “malignant” or “benign”:

| Name | Meaning in this project |
|------|-------------------------|
| **True Positive (TP)** | Malignant sample predicted as malignant |
| **False Negative (FN)** | Malignant sample predicted as benign (a miss) |
| **True Negative (TN)** | Benign sample predicted as benign |
| **False Positive (FP)** | Benign sample predicted as malignant (a false alarm) |

**Accuracy** — overall fraction of predictions that match the true label. Easy to quote, but can look good even if the model misses many malignant cases when classes are uneven.

**Precision** — of the rows the model called malignant, how many really were malignant. High precision means fewer false alarms.

**Recall / Sensitivity** — of the rows that really were malignant, how many the model caught. High recall means fewer misses. In a disease-risk research setting, recall is often more important than looking “generally accurate.”

**Specificity** — of the rows that really were benign, how many the model correctly called benign. Computed from the confusion matrix:

```text
specificity = TN / (TN + FP)
```

**F1-score** — a single number that balances precision and recall. Useful when you do not want to look at only one of those two.

**ROC-AUC** — how well the model *ranks* malignant vs benign when it outputs a probability, not just a yes/no label. It must use predicted probabilities (`predict_proba`), not the final 0/1 class. A value near 0.5 is little better than chance; a value near 1.0 means strong ranking on the test set. High AUC on this small public dataset still does **not** mean the model is clinically valid.

**Confusion matrix** — a 2×2 table of TP, FP, FN, TN. Heatmaps make that table easy to see.

None of these metrics turn the project into a diagnostic tool. They only describe research performance on a public test split.

---

## Why we split data into training and test sets

If you train and score on the **same** rows, the model can memorize those rows. The score would look excellent and still fail on new rows.

So we:

1. **Train** on 80% of the rows (the model is allowed to learn from these).
2. **Test** on the remaining 20% (the model must not have used these while learning).

We use a **stratified** split so both classes (malignant and benign) appear in train and test in similar proportions. We set `random_state=42` so the split is **reproducible**: you and a classmate can get the same split.

Scaling (see below) is fit **only** on the training set. Using test-set statistics while training would leak information and make scores look better than a fair test.

---

## Why StandardScaler is used for Logistic Regression

The dataset has 30 numeric features on **different scales** (for example, a “mean area” number can be much larger than a “smoothness” number).

**Logistic Regression** draws a linear decision boundary. Large-scale features can dominate small-scale ones if you do not standardize. `StandardScaler` rewrites each feature so that, on the training data, it has mean 0 and variance 1. That puts features on a comparable footing.

We will wrap scaling and the classifier in a scikit-learn **Pipeline**:

```python
Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(...)),
])
```

The Pipeline fits the scaler on **training** data only, then applies the same transform to the test data. That is the correct, no-leakage pattern.

**Random Forest** does **not** need this scaler. It splits on thresholds (“is feature X above 12.3?”) and is not thrown off by different units the same way. Scaling it is unnecessary for a fair baseline and would mix two different design choices.

---

## Safety language you will see in the software

When code exists, printed summaries, plots, and any future UI must include:

**Research risk classification — not for clinical use.**

Never describe an output as a diagnosis, treatment recommendation, or patient result.

---

## Next steps

- **Phase 2** will add richer evaluation, saved plots you already get in Phase 1 plus feature selection (reducing roughly 30 features to about 4–8 so a quantum circuit can use them), and reproducibility details.
- **Phase 3** will add hybrid quantum-classical models (VQC and QSVC) and compare them **fairly** against the classical baseline — without assuming quantum wins.

Frontend design (pages, layout, copy rules) is specified in [PRD.md](PRD.md) under **Frontend**. That UI is **not** built until Phase 5.

When you are ready for code, the next implementation step is **Phase 1 only**: classical baseline, no Qiskit, no Streamlit.
