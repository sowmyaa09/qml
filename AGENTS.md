# AGENTS.md

Living notes for Cursor agents working in this repo. **Read this first. Update this file whenever architecture, commands, safety rules, or SIH status change** (dates + what changed). Do not treat README as the only source of truth if this file is newer.

**Last updated:** 2026-09-07

---

## What this project is

**Q-Care Detect** — SIH 2026 **SIH26139** (Egreen Quanta): *Hybrid Quantum Machine Learning Platform for Early Disease Detection* (software, MedTech).

It is a **research/educational prototype**, not a medical device. Public biomedical **benchmarks** only. Output language: **research risk classification**, never diagnosis or treatment.

Repo: `c:\Projects\qml` (remote `https://github.com/sowmyaa09/qml`).

---

## Hard rules (do not violate)

- Always: **Research risk classification - not for clinical use.** Educational only; not a medical device.
- Do **not** claim QML is automatically more accurate. On Wisconsin (this machine), **classical LR beat VQC/QSVC on F1**; VQC was much slower. That is an acceptable research outcome.
- Do **not** fuse tables/images into one “what disease do I have?” oracle.
- Do **not** add a general symptom checker, scanned-EHR diagnosis, or LLM-invented ICD lists with fake confidence.
- Do **not** invent or rank “best doctors in town.” Specialty *domain* hints only.
- Do **not** build multi-disease confidence for a person, comorbidity scores, or “more tests would find X.” Refused repeatedly on 2026-09-07: each model only sees its own table's columns and label, so a joint per-person answer would be fabricated. `predict_proba` + band + threshold on **one** label is the allowed form of “decision support.”
- Do **not** concatenate Kaggle **copies** of Wisconsin (same 569 rows) to “get more samples” — that is leakage. Extra WDBC-30-feature rows **do not exist** publicly.
- Before adding any "bigger" mirror, run `python -m src.audit_datasets`. Measured 2026-09-07: `heart_disease` (johnsmith88) is **70.5% duplicate rows** (723/1025) and its RF scored a fake **1.000**; deduped it is 302 rows / F1 0.788. `load_tabular_dataset(..., drop_duplicates=True)` is the default — keep it. Genuine growth = **different patients** (`heart_uci_pooled` = 4 UCI cohorts, 918 rows, RF F1 0.868).
- Do **not** train QML on 30 raw columns or on images (near-term circuits). QML v1 = **selected 4–8 Wisconsin features**, Qiskit **Aer / statevector**.
- Do **not** download NIH-scale archives (~40 GB). Image experiments stay laptop-sized.
- Do **not** commit `.env`, API keys, or treat gitignored `models/` / `outputs/` as if they were in git (fresh clone needs retraining).
- Extra datasets = **separate** `train_*` experiments, one table/one task. Genuine large unique-person tables already in-tree: `cardio` (~69k), diabetes BRFSS 2015 (~253k), `brfss_heart` (~320k CDC 2020). Do **not** add EEG Eye State as “15k patients” (one recording).

---

## User / environment

- Windows, PowerShell. Beginner: do not mix Python `import` into PowerShell; use `python -m src....` from project root with **`.venv`**.
- GPU: CUDA PyTorch was used for WBC/MSK CNNs when available.
- `random_state=42`, stratified 80/20. Malignant / disease-present = **positive class 1** on Wisconsin (`y = (sklearn_target == 0).astype(int)`).

---

## Layout

```
src/          train_classical, train_phase2, train_qml, train_phase4,
              train_qml_ablation, train_qml_table, make_judge_sheet,
              decision_support, explain, train_tune,
              train_diabetes, train_tabular, train_wbc, train_msk,
              research_map, nvidia_client, api_server, catalog_schemas, ...
app/streamlit_app.py
tests/
models/       gitignored joblib/pt
outputs/      figures, metrics, reports (mostly gitignored)
.env.example  NVIDIA_API_KEY (copy to .env, never commit)
```

---

## Commands (assignment core)

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.train_classical
python -m src.train_phase2
python -m src.train_qml --with-qnn
python -m src.train_qml_significance
python -m src.train_qml_ablation
python -m src.train_qml_table coimbra
python -m src.train_phase4
python -m src.make_judge_sheet
streamlit run app/streamlit_app.py
pytest
```

QML: `FidelityStatevectorKernel` for QSVC (not shot-based `FidelityQuantumKernel` — that hung). VQC default: ZZFeatureMap/RealAmplitudes **reps=2**, COBYLA **maxiter=60** (~600 s here). Also trains **RBF SVM** on the same k columns as the honest kernel control. `--with-qnn` adds `EstimatorQNN` + `NeuralNetworkClassifier` (fit on **±1** labels via `labels_to_pm1`; rank with `qnn_ranking_scores`, no `predict_proba`). Do not assume pickle of VQC works. `--skip-vqc` for a faster kernel-only run; `--skip-calibration` skips the Platt-scaled QSVC refits.

**Statistics before claims.** `src/significance.py` = stratified bootstrap CIs, paired bootstrap of the difference, McNemar (paired predictions), DeLong (paired AUC). `train_qml_significance` reads `qml_test_scores.csv` and rebuilds predictions at each model's own cutoff, so **VQC/QNN are never refitted**. Measured 2026-09-07: QSVC 0.950 [0.895, 0.988] vs RBF 0.951 [0.897, 0.988], McNemar **p=1.000** — indistinguishable; VQC/QNN separated at p<0.001 (worse). Repeated CV 5x5 (preprocessing inside each fold): LR 0.931, RBF 0.927, RF 0.926, QSVC 0.909. Do **not** report a p-value from CV folds (they share rows). Pitch **cost**, not accuracy.

Decision support = **one table, one label**: `src/decision_support.py` (probability band, threshold sweep, `*_test_scores.csv` written by `evaluate_models`). Calibration/Brier only for real probabilities; `decision_function` models are excluded unless Platt-scaled. Explainability = `src/explain.py` (classical coefficients + one worked row); circuits are **not** explained as feature importances.

Optional: `python -m src.train_diabetes` | `python -m src.train_tabular --list|all|<key>` | `python -m src.train_wbc` | `python -m src.train_msk fracture|spine`

Research mapper API: `uvicorn src.api_server:app --reload --port 8000`  
Needs `.env` with `NVIDIA_API_KEY`. Default chat id: **`meta/muse-glimmer-30b`** (HTTP 200 on this key, 2026-09-06). DeepSeek V4 / Nemotron Ultra / Gemma 4 **timed out** rather than 403 with the refreshed key; `deepseek-ai/deepseek-r1` is **404**. Mapper still falls back to local `feature: number` regex if NIM fails. `%` only from `predict_proba`/`decision_function` when enough fields exist. Catalog keys: `wisconsin`, `wisconsin_reduced`, `diabetes`, `cardio`, `stroke`, `coimbra`, `framingham`, `hepatitis`. Extra train-only tables: `seizure`, `seer_breast`, `cervical`, `pcos`, `brfss_heart` (EEG/SEER/PCOS/BRFSS-heart are not mapper schemas).

---

## Status vs SIH delivery table

| Area | Status |
|------|--------|
| D1–D12 docs, pipeline, LR/RF, eval, CLI, tests, SelectKBest k=6, VQC+QSVC, benchmark, explainability, Streamlit | **Done** |
| D13 FastAPI | Local research-mapper API + `GET /v1/catalog`; not a hosted clinical API |
| Extra public tables / optional MSK CNNs | Done as separate tracks |
| QNN | Done as an optional track: `train_qml --with-qnn` (EstimatorQNN) |
| Decision support (PS wording: disease probability scores, risk stratification, threshold tuning) | Done **per table**: band + threshold sweep + calibration. Never cross-disease |
| Qubit ablation (k=4/6/8) + second hybrid table (Coimbra) | Done |
| Reviewer sheet | `python -m src.make_judge_sheet` → `outputs/reports/judge_sheet.md` |
| Real QPU | Not used (simulator allowed) |

Phase 2 kept features (typical): mean perimeter, mean concave points, worst radius, worst perimeter, worst area, worst concave points.

PRD.md may lag the code; README + this file are more current.

---

## When implementing

- Keep compact RF + `joblib` `compress=3` on large tables.
- `src/utils.py` forces the **Agg** matplotlib backend. Do not remove it: with a Tk backend, long Qiskit fits died with `Tcl_AsyncDelete: async handler deleted by the wrong thread` (2026-09-07).
- Qiskit ML 0.9 **ignores** the `callback=` argument on the COBYLA path. Use `recording_cobyla(maxiter, history)` (a `Minimizer` wrapper) if you need an optimizer trace.
- Feature selection **train-only**.
- Streamlit: disclaimer on every page; mapper is research-only.
- New disease table: `tabular_datasets.py` + train command + optional `catalog_schemas.py` if the mapper should score it.
- After meaningful product/safety/command changes: **edit this AGENTS.md** (date, bullets).

---

## Changelog (agents)

- **2026-09-07:** Added `brfss_heart` (CDC 2020 BRFSS heart-disease survey, ~320k unique respondents) as a **separate** classical table. Size does not prevent copies; EEG “15k rows” is often one person. QSVC refuses tables with more than 5000 rows (`MAX_QML_ROWS`) so a 400-row subsample is not sold as a hybrid experiment.
- **2026-09-07:** Duplicate-row audit (`src/audit_datasets.py`) + default dedup in the loader; found `heart_disease` was 70.5% copies (RF was a fake 1.000). Added `heart_uci_pooled` (4 real cohorts, 918 rows) via new `pooled_urls`/`pooled_columns` spec fields, retrained all tables, and generalized the significance CLI with `--prefix` (QSVC's F1 edge on pooled heart is **not** significant: McNemar p=1.000).
- **2026-09-07:** Added significance layer (`src/significance.py`, `train_qml_significance`, `QuantileClipper` for leak-free CV pipelines) + Streamlit/judge-sheet sections. Result: QSVC is statistically **indistinguishable** from LR/RF/RBF on this split; VQC/QNN are genuinely worse.
- **2026-09-07:** Added decision support (band + threshold sweep + `*_test_scores.csv`), calibration/Brier, QNN track, k=4/6/8 QSVC ablation, second hybrid table (`train_qml_table coimbra`), richer Phase 4 explainability, reviewer sheet, Streamlit **Decision support / Explainability / Demo script** pages, `GET /v1/catalog`. User asked several times for multi-disease confidence + "more tests would find X" advisory; **refused** (see hard rules).
- **2026-09-07:** Train-only quantile clip, balanced LR, CV tune on small tables, cardio impossible-BP row drop. Retrain classical / phase2 / QML / extra tables. Still not a fused diagnosis product.
- **2026-09-06:** Refreshed NVIDIA key: **`meta/muse-glimmer-30b` works** (JSON in `content` if `max_tokens` is large enough; otherwise only `reasoning_content`). DeepSeek V4 / Nemotron Ultra / Gemma 4 hang; DeepSeek R1 not in catalog.
- **2026-09-06:** Phase 3 rebuilt: RBF SVM kernel baseline, VQC reps=2 / COBYLA 60, circuit notes, `phase3_qml.md`, no double-fit timings, Streamlit QML page expanded. Mapper uses local regex fallback when NIM fails.
- **2026-09-04:** Created this file. Phases 1–5 + extras + NVIDIA research mapper in tree. Wisconsin QML did not beat classical F1.
- **2026-09-04:** Default `NVIDIA_MODEL` is `deepseek-ai/deepseek-v4-pro-0813` (NVIDIA sample). Current `.env` key still returns **403** on that model; generate the key on that model’s page at build.nvidia.com.
