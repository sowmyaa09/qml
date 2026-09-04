# AGENTS.md

Living notes for Cursor agents working in this repo. **Read this first. Update this file whenever architecture, commands, safety rules, or SIH status change** (dates + what changed). Do not treat README as the only source of truth if this file is newer.

**Last updated:** 2026-09-04

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
- Do **not** concatenate Kaggle **copies** of Wisconsin (same 569 rows) to “get more samples” — that is leakage. Extra WDBC-30-feature rows **do not exist** publicly.
- Do **not** train QML on 30 raw columns or on images (near-term circuits). QML v1 = **selected 4–8 Wisconsin features**, Qiskit **Aer / statevector**.
- Do **not** download NIH-scale archives (~40 GB). Image experiments stay laptop-sized.
- Do **not** commit `.env`, API keys, or treat gitignored `models/` / `outputs/` as if they were in git (fresh clone needs retraining).
- Extra datasets = **separate** `train_*` experiments, one table/one task.

---

## User / environment

- Windows, PowerShell. Beginner: do not mix Python `import` into PowerShell; use `python -m src....` from project root with **`.venv`**.
- GPU: CUDA PyTorch was used for WBC/MSK CNNs when available.
- `random_state=42`, stratified 80/20. Malignant / disease-present = **positive class 1** on Wisconsin (`y = (sklearn_target == 0).astype(int)`).

---

## Layout

```
src/          train_classical, train_phase2, train_qml, train_phase4,
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
python -m src.train_qml
python -m src.train_phase4
streamlit run app/streamlit_app.py
pytest
```

QML: `FidelityStatevectorKernel` for QSVC (not shot-based `FidelityQuantumKernel` — that hung). VQC COBYLA maxiter=40. Do not assume pickle of VQC works.

Optional: `python -m src.train_diabetes` | `python -m src.train_tabular --list|all|<key>` | `python -m src.train_wbc` | `python -m src.train_msk fracture|spine`

Research mapper API: `uvicorn src.api_server:app --reload --port 8000`  
Needs `.env` with `NVIDIA_API_KEY`. Mapper **only** fills catalog fields (`wisconsin`, `wisconsin_reduced`, `diabetes`, `cardio`, `stroke`); `%` only from `predict_proba` when enough fields exist.

---

## Status vs SIH delivery table

| Area | Status |
|------|--------|
| D1–D12 docs, pipeline, LR/RF, eval, CLI, tests, SelectKBest k=6, VQC+QSVC, benchmark, explainability, Streamlit | **Done** |
| D13 FastAPI | Local research-mapper API exists; not a hosted clinical API |
| Extra public tables / optional MSK CNNs | Done as separate tracks |
| QNN | Not required (PS: “or equivalent”) |
| Real QPU | Not used (simulator allowed) |

Phase 2 kept features (typical): mean perimeter, mean concave points, worst radius, worst perimeter, worst area, worst concave points.

PRD.md may lag the code; README + this file are more current.

---

## When implementing

- Keep compact RF + `joblib` `compress=3` on large tables.
- Feature selection **train-only**.
- Streamlit: disclaimer on every page; mapper is research-only.
- New disease table: `tabular_datasets.py` + train command + optional `catalog_schemas.py` if the mapper should score it.
- After meaningful product/safety/command changes: **edit this AGENTS.md** (date, bullets).

---

## Changelog (agents)

- **2026-09-04:** Created this file. Phases 1–5 + extras + NVIDIA research mapper in tree. Wisconsin QML did not beat classical F1.
- **2026-09-04:** Default `NVIDIA_MODEL` is `deepseek-ai/deepseek-v4-pro-0813` (NVIDIA sample). Current `.env` key still returns **403** on that model; generate the key on that model’s page at build.nvidia.com.
