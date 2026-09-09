"""Q-Care Detect — local Streamlit research comparison UI.

Run from the project root:

    streamlit run app/streamlit_app.py

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils import LONG_DISCLAIMER, RESEARCH_DISCLAIMER, get_project_root

st.set_page_config(page_title="Q-Care Detect (research)", layout="wide")

BANNER = (
    "This project is for educational and research purposes only. "
    "It is not a medical device and must not be used for clinical "
    "diagnosis or treatment decisions."
)

PAGES = (
    "Home",
    "Data overview",
    "Classical results",
    "QML comparison",
    "Decision support",
    "Explainability",
    "Research notes mapper",
    "Extra research tables",
    "Image experiments",
    "How to read metrics",
    "Demo script",
    "About and limits",
)

SCENARIOS = {
    "Wisconsin breast cancer (assignment core)": {
        "metrics": "classical_model_metrics.csv",
        "prefix": "",
        "note": "sklearn public table. 1 = malignant on this benchmark only.",
        "empty": "Run `python -m src.train_classical` first.",
    },
    "Wisconsin reduced features (Phase 2)": {
        "metrics": "phase2_reduced_classical_model_metrics.csv",
        "prefix": "phase2_reduced",
        "note": "Same split, k selected columns for near-term QML.",
        "empty": "Run `python -m src.train_phase2` first.",
    },
    "Diabetes BRFSS survey": {
        "metrics": "diabetes_classical_model_metrics.csv",
        "prefix": "diabetes",
        "note": "Survey label, not a lab diagnosis.",
        "empty": "Run `python -m src.train_diabetes` first.",
    },
    "Cardio table": {
        "metrics": "cardio_classical_model_metrics.csv",
        "prefix": "cardio",
        "note": "Separate Kaggle cardio experiment.",
        "empty": "Run `python -m src.train_tabular cardio` first.",
    },
    "Stroke table": {
        "metrics": "stroke_classical_model_metrics.csv",
        "prefix": "stroke",
        "note": "Separate Kaggle stroke experiment.",
        "empty": "Run `python -m src.train_tabular stroke` first.",
    },
}


def _paths():
    root = get_project_root()
    return {
        "root": root,
        "metrics": root / "outputs" / "metrics",
        "figures": root / "outputs" / "figures",
        "reports": root / "outputs" / "reports",
    }


def disclaimer_banner() -> None:
    st.warning(BANNER)
    st.caption(RESEARCH_DISCLAIMER)


def load_metrics_csv(name: str) -> pd.DataFrame | None:
    path = _paths()["metrics"] / name
    if not path.is_file():
        return None
    return pd.read_csv(path)


def show_png(stem_or_name: str) -> None:
    figures = _paths()["figures"]
    path = figures / stem_or_name
    if path.is_file():
        st.image(str(path), use_container_width=True)
    else:
        st.info(f"Figure not generated yet: `{path.name}`")


def metric_cards(frame: pd.DataFrame) -> None:
    cols = st.columns(max(len(frame), 1))
    for i, (_, row) in enumerate(frame.iterrows()):
        with cols[i]:
            st.subheader(str(row.get("model", f"model {i}")))
            for key in ("accuracy", "recall", "f1", "roc_auc", "precision", "specificity"):
                if key in row and pd.notna(row[key]):
                    st.metric(key, f"{float(row[key]):.3f}")


def page_home() -> None:
    st.title("Q-Care Detect")
    st.markdown(
        "A **research** comparison of classical machine learning and "
        "(when trained) hybrid quantum classifiers on **public** biomedical tables."
    )
    st.markdown(
        "- Not a clinic portal.\n"
        "- Not a symptom checker.\n"
        "- Extra datasets are **separate experiments**, not one model for all diseases."
    )
    st.markdown("**Current assignment core:** Wisconsin breast cancer, then QML on a few selected features.")
    st.markdown("Open **Classical results**, **QML comparison**, or **Research notes mapper** in the sidebar.")


def page_data() -> None:
    st.title("Data overview")
    st.markdown(
        """
The assignment core uses sklearn's **Wisconsin Diagnostic Breast Cancer** table
(public, 569 rows, 30 numeric features). Original sklearn labels are
`0 = malignant`, `1 = benign`. This project converts so that **1 = malignant**
(positive class for metrics).

There are **no patient names** and **no hospital EHR dumps**. File upload is disabled.

Other catalog tables (diabetes survey, cardio, stroke, …) appear under
**Extra research tables**. Image experiments (WBC cells, optional fracture/spine)
are a different kind of benchmark — they do not name a person's disease.
"""
    )
    features = _paths()["reports"] / "phase2_selected_features.json"
    if features.is_file():
        st.subheader("Phase 2 selected features")
        st.json(features.read_text(encoding="utf-8"))
    else:
        st.info("Run `python -m src.train_phase2` to see the selected-feature JSON.")


def page_classical() -> None:
    st.title("Classical results")
    st.caption("Public test split only. " + RESEARCH_DISCLAIMER)
    choice = st.selectbox("Research scenario", list(SCENARIOS.keys()))
    spec = SCENARIOS[choice]
    st.markdown(spec["note"])
    frame = load_metrics_csv(spec["metrics"])
    if frame is None:
        st.error(spec["empty"])
        return
    metric_cards(frame)
    st.dataframe(frame, use_container_width=True)
    prefix = spec["prefix"]
    stem = f"{prefix}_" if prefix else ""
    col1, col2 = st.columns(2)
    with col1:
        show_png(f"{stem}logistic_regression_confusion_matrix.png")
    with col2:
        show_png(f"{stem}random_forest_confusion_matrix.png")
    show_png(f"{stem}roc_curve_comparison.png")
    show_png(f"{stem}model_metric_comparison.png")
    st.caption("Scores are for this test split only. They are not a medical ranking.")


def page_qml() -> None:
    st.title("QML comparison")
    st.caption(RESEARCH_DISCLAIMER)
    st.markdown(
        "Hybrid models (VQC, QSVC) run on a **classical simulator** using the "
        "Phase 2 selected columns. An **RBF SVM** on the same columns is the "
        "fair kernel baseline. Quantum is **not** assumed to win."
    )
    frame = load_metrics_csv("qml_vs_classical_metrics.csv")
    if frame is None:
        st.warning("Quantum results not generated yet. Run `python -m src.train_qml`.")
        return
    metric_cards(frame)
    st.dataframe(frame, use_container_width=True)
    show_png("qml_roc_curve_comparison.png")
    show_png("qml_model_metric_comparison.png")
    show_png("qml_vqc_optimizer_trace.png")
    show_png("qml_qnn_optimizer_trace.png")

    st.subheader("Is the gap real? (confidence intervals and paired tests)")
    intervals = load_metrics_csv("qml_significance_bootstrap.csv")
    pairs = load_metrics_csv("qml_significance_pairs.csv")
    if intervals is None or pairs is None:
        st.info(
            "Run `python -m src.train_qml_significance` for bootstrap intervals, "
            "McNemar and DeLong tests."
        )
    else:
        show_png("qml_significance_intervals.png")
        st.dataframe(
            intervals[intervals["metric"] == "f1"].reset_index(drop=True),
            use_container_width=True,
        )
        st.dataframe(pairs, use_container_width=True)
        undecided = int(pairs["f1_ci_crosses_zero"].sum())
        st.markdown(
            f"**{undecided} of {len(pairs)}** quantum-vs-classical pairs have an F1 "
            "difference interval that includes zero, meaning this split cannot "
            "separate them. `mcnemar_p` uses only the rows where exactly one model "
            "is correct; `delong_p` compares the two ROC-AUCs on the same rows."
        )
        cv = load_metrics_csv("qml_repeated_cv.csv")
        if cv is not None:
            st.markdown("**Repeated stratified cross-validation (5 x 5 folds)**")
            st.dataframe(cv, use_container_width=True)
            st.caption(
                "Clipping, selection and scaling are refit inside every fold. No "
                "p-value is computed from these folds: they share training rows, "
                "so a naive paired test would be over-confident."
            )
        report = _paths()["reports"] / "phase3_significance.md"
        if report.is_file():
            with st.expander("Significance report"):
                st.markdown(report.read_text(encoding="utf-8"))

    ablation = load_metrics_csv("qml_ablation_k.csv")
    st.subheader("Ablation — qubits vs quantum-kernel quality")
    if ablation is None:
        st.info("Run `python -m src.train_qml_ablation` to sweep k = 4, 6, 8.")
    else:
        show_png("qml_ablation_k.png")
        st.dataframe(ablation, use_container_width=True)
        st.caption(
            "One qubit per selected column. The RBF SVM row is the control: if a "
            "classical kernel matches QSVC at the same k, the quantum kernel is "
            "not adding value here."
        )

    second = sorted(_paths()["metrics"].glob("*_qml_metrics.csv"))
    if second:
        st.subheader("Second hybrid experiment (separate table)")
        pick = st.selectbox("Hybrid table", [p.name for p in second])
        st.dataframe(pd.read_csv(_paths()["metrics"] / pick), use_container_width=True)
        key = pick.replace("_qml_metrics.csv", "")
        report_path = _paths()["reports"] / f"phase3_qml_{key}.md"
        if report_path.is_file():
            with st.expander(f"{key} hybrid report"):
                st.markdown(report_path.read_text(encoding="utf-8"))
        st.caption(
            "A different table with different columns. It is not merged with "
            "Wisconsin and does not produce a combined disease score."
        )

    notes = _paths()["reports"] / "phase3_circuit_notes.txt"
    if notes.is_file():
        with st.expander("Circuit notes (simulator)"):
            st.text(notes.read_text(encoding="utf-8")[:8000])
    phase3 = _paths()["reports"] / "phase3_qml.md"
    if phase3.is_file():
        st.subheader("Phase 3 report")
        st.markdown(phase3.read_text(encoding="utf-8"))
    report = _paths()["reports"] / "hybrid_comparison.md"
    if report.is_file():
        st.subheader("Phase 4 written comparison")
        st.markdown(report.read_text(encoding="utf-8"))


SCORE_FILE_LABELS = {
    "test_scores.csv": "Wisconsin — all 30 features (Phase 1)",
    "phase2_full_test_scores.csv": "Wisconsin — 30 features (Phase 2 control)",
    "phase2_reduced_test_scores.csv": "Wisconsin — selected features (Phase 2)",
    "qml_test_scores.csv": "Wisconsin — classical vs QML (Phase 3)",
    "diabetes_test_scores.csv": "Diabetes BRFSS survey",
}


def _score_file_label(name: str) -> str:
    if name in SCORE_FILE_LABELS:
        return SCORE_FILE_LABELS[name]
    stem = name.replace("_test_scores.csv", "").replace("test_scores.csv", "")
    if stem.endswith("_qml"):
        return f"{stem[:-4]} — hybrid QML experiment"
    return f"{stem} — classical experiment"


def page_decision_support() -> None:
    st.title("Decision support (research thresholds)")
    st.caption(RESEARCH_DISCLAIMER)
    st.markdown(
        "A trained model outputs a **probability for the label of its own table**. "
        "This page shows that score, a research **band**, and what happens to "
        "recall and false positives when you move the **threshold**."
    )
    st.warning(
        "This is not triage. It does not rank diseases, suggest tests, or say "
        "anything about a person. Every number below comes from one held-out "
        "split of one public benchmark."
    )

    from src.decision_support import (
        band_legend,
        is_probability_like,
        threshold_metrics,
        threshold_sweep,
    )

    metrics_dir = _paths()["metrics"]
    files = sorted(metrics_dir.glob("*test_scores.csv"))
    if not files:
        st.info(
            "No held-out scores saved yet. Run `python -m src.train_classical` "
            "or `python -m src.train_qml` first."
        )
        return

    labels = {_score_file_label(p.name): p for p in files}
    choice = st.selectbox("Experiment", list(labels.keys()))
    frame = pd.read_csv(labels[choice])
    models = sorted(frame["model"].unique())
    model = st.selectbox("Model", models)
    subset = frame[frame["model"] == model]
    scores = subset["score"].to_numpy(dtype=float)
    truth = subset["y_true"].to_numpy(dtype=int)
    probability_like = is_probability_like(scores)

    if probability_like:
        st.caption("Scores are probabilities from `predict_proba`. " + band_legend())
    else:
        st.caption(
            "This model ranks with `decision_function`, so the score is **not** a "
            "probability. The threshold is a raw decision score."
        )

    lo, hi = float(scores.min()), float(scores.max())
    default = 0.5 if probability_like else float((lo + hi) / 2)
    threshold = st.slider(
        "Decision threshold for the positive class",
        min_value=float(round(lo, 4)),
        max_value=float(round(hi, 4)),
        value=float(min(max(default, lo), hi)),
        step=float(max((hi - lo) / 100, 1e-4)),
    )

    at = threshold_metrics(truth, scores, threshold)
    cols = st.columns(4)
    cols[0].metric("Recall (sensitivity)", f"{at['recall']:.3f}")
    cols[1].metric("Specificity", f"{at['specificity']:.3f}")
    cols[2].metric("Precision", f"{at['precision']:.3f}")
    cols[3].metric("F1", f"{at['f1']:.3f}")

    counts = st.columns(4)
    counts[0].metric("Caught positives", at["true_positives"])
    counts[1].metric("Missed positives", at["false_negatives"])
    counts[2].metric("False alarms", at["false_positives"])
    counts[3].metric("Correct negatives", at["true_negatives"])

    st.markdown(
        f"At this threshold the model misses **{at['false_negatives']}** positive "
        f"rows and raises **{at['false_positives']}** false alarms on "
        f"{len(truth)} held-out rows."
    )

    sweep = threshold_sweep(truth, scores, steps=41)
    st.subheader("Threshold sweep")
    st.line_chart(
        sweep.set_index("threshold")[["recall", "specificity", "precision", "f1"]]
    )
    with st.expander("Sweep table"):
        st.dataframe(sweep, use_container_width=True)

    if probability_like:
        st.subheader("Band of a single score")
        probability = st.slider(
            "Research probability for this table's positive class",
            0.0,
            1.0,
            0.5,
            0.01,
        )
        from src.decision_support import risk_band

        st.info(
            f"p = {probability:.2f} falls in the **{risk_band(probability)}** "
            "for this public table. Not a diagnosis."
        )

    options = load_metrics_csv("qml_threshold_options.csv")
    if options is not None:
        st.subheader("Precomputed threshold options (Phase 3)")
        st.dataframe(options, use_container_width=True)

    show_png("qml_calibration_curve.png")
    st.caption(
        "A reliability curve only makes sense for real probabilities. Models "
        "scored by `decision_function` are left out unless Platt-scaled."
    )


def page_explainability() -> None:
    st.title("Explainability")
    st.caption(RESEARCH_DISCLAIMER)
    from src.explain import QML_EXPLAINABILITY_LIMITS

    st.markdown(
        "We explain the **classical** model trained on the same selected columns "
        "as the quantum models, then state the circuit limits plainly."
    )
    show_png("phase4_permutation_importance.png")

    coefficients = load_metrics_csv("phase4_lr_coefficients.csv")
    if coefficients is None:
        st.info("Run `python -m src.train_phase4` to build the coefficient tables.")
    else:
        st.subheader("Standardized logistic-regression coefficients")
        st.dataframe(coefficients, use_container_width=True)
        st.caption(
            "Sign shows which class a column pushes toward on this benchmark. "
            "It is not a statement about causing disease."
        )

    contributions = load_metrics_csv("phase4_lr_row_contributions.csv")
    if contributions is not None:
        st.subheader("Worked example: why one row's score moved")
        st.dataframe(contributions, use_container_width=True)
        st.caption("contribution = standardized value x coefficient, for one test row.")

    importance = load_metrics_csv("phase4_feature_importance.csv")
    if importance is not None:
        st.subheader("Permutation importance (held-out rows)")
        st.dataframe(importance, use_container_width=True)

    st.subheader("Why we do not 'explain' the circuits")
    st.info(QML_EXPLAINABILITY_LIMITS)


def page_demo_script() -> None:
    st.title("Demo script (3 minutes)")
    st.caption(RESEARCH_DISCLAIMER)
    st.markdown(
        """
1. **Frame it (20s).** Hybrid quantum-classical research platform on public
   biomedical benchmarks. Say the disclaimer out loud: research risk
   classification, not for clinical use, not a medical device.
2. **Classical baseline (30s).** *Classical results* → Wisconsin. Point at
   recall and ROC-AUC, and note that the split seed is fixed at 42 and every
   transform is fit on training rows only.
3. **Hybrid QML (45s).** *QML comparison* → the same six selected columns feed
   VQC, QSVC, a QNN, and an **RBF SVM control**. Show the metric table with
   the runtime column.
4. **Say who won (20s).** On this table the classical and kernel models hold
   the F1 lead and train far faster. That is a measured result, not a failure.
5. **Ablation (20s).** Qubits versus quantum-kernel quality: more qubits is
   not automatically better, and cost climbs.
6. **Decision support (25s).** Move the threshold; watch missed positives
   trade against false alarms. Probability, band, threshold — no disease
   ranking.
7. **Explainability (20s).** Permutation importance plus one worked row for
   the classical model, and the honest statement that circuit weights are not
   feature importances.
8. **Close (10s).** Second hybrid table (Coimbra), the reviewer sheet, and the
   list of things this project refuses to do: no symptom checker, no
   multi-disease score for a person, no test advice, no named doctors.
"""
    )
    sheet = _paths()["reports"] / "judge_sheet.md"
    if sheet.is_file():
        st.subheader("Reviewer sheet")
        st.markdown(sheet.read_text(encoding="utf-8"))
    else:
        st.info("Run `python -m src.make_judge_sheet` to generate the reviewer sheet.")


def page_extra_tables() -> None:
    st.title("Extra research tables")
    st.markdown(
        "Each CSV is its own experiment. This page is **not** a combined diagnosis tool. "
        "Large unique-person tables (`cardio`, diabetes BRFSS, `brfss_heart`) stay "
        "classical; row count is not the same as unique patients."
    )
    metrics_dir = _paths()["metrics"]
    # Phase 2/3 artifacts share this filename pattern; they live on their own pages.
    internal = {
        "qml_classical_model_metrics.csv",
        "phase2_full_classical_model_metrics.csv",
        "phase2_reduced_classical_model_metrics.csv",
    }
    files = [
        p
        for p in sorted(metrics_dir.glob("*_classical_model_metrics.csv"))
        if p.name not in internal and not p.name.endswith("_qml_classical_model_metrics.csv")
    ]
    if not files:
        st.info(
            "No extra-table metrics yet. Try `python -m src.train_tabular cardio` "
            "or `python -m src.train_diabetes`."
        )
        return
    names = [p.name for p in files]
    pick = st.selectbox("Metrics file", names)
    frame = load_metrics_csv(pick)
    if frame is not None:
        st.dataframe(frame, use_container_width=True)
        prefix = pick.replace("_classical_model_metrics.csv", "")
        col1, col2 = st.columns(2)
        with col1:
            show_png(f"{prefix}_logistic_regression_confusion_matrix.png")
        with col2:
            show_png(f"{prefix}_random_forest_confusion_matrix.png")


def page_images() -> None:
    st.title("Image experiments")
    st.markdown(
        "Separate CNN demos (cell type, optional bone/spine X-rays). "
        "Not QML. Not all injuries. Not a radiology product."
    )
    for name in (
        "wbc_cnn_metrics.csv",
        "msk_fracture_metrics.csv",
        "msk_spine_metrics.csv",
    ):
        frame = load_metrics_csv(name)
        st.subheader(name)
        if frame is None:
            st.info(f"Not generated yet: `{name}`")
        else:
            st.dataframe(frame, use_container_width=True)
    show_png("wbc_cnn_confusion_matrix.png")
    show_png("msk_fracture_confusion_matrix.png")
    show_png("msk_spine_confusion_matrix.png")


def page_metrics_help() -> None:
    st.title("How to read metrics")
    st.markdown(
        """
- **Accuracy** — overall fraction correct. Can look high while missing the positive class.
- **Precision** — of predicted positives, how many were actually positive on this table.
- **Recall / sensitivity** — of true positives, how many were caught.
- **Specificity** — of true negatives, how many were called negative (`TN / (TN+FP)`).
- **F1** — balance of precision and recall.
- **ROC-AUC** — ranking quality from a score such as `predict_proba[:, 1]`.
- **Brier score** — how well probabilities match observed frequency (lower is better).
- **Threshold** — the cut-off where a score becomes a predicted 1. Lowering it
  catches more positives and raises more false alarms.

These are **research scores on a public split**. They are not a clinical test.
"""
    )


def page_research_mapper() -> None:
    st.title("Research notes mapper")
    st.caption(RESEARCH_DISCLAIMER)
    st.markdown(
        "Paste **synthetic** notes or a **text PDF** of numeric fields that match "
        "a public catalog table. NVIDIA NIM (if configured) translates wording "
        "into **machine fields**. Saved models may return a **research %** only "
        "when enough of **that table’s** columns are filled."
    )
    st.markdown(
        "- Not a diagnosis. Not a symptom checker for all diseases.\n"
        "- Unmapped symptoms stay in a list; they do **not** become extra diseases.\n"
        "- We do **not** name or rank doctors. Seek licensed local care yourself."
    )

    if "mapper_notes" not in st.session_state:
        st.session_state.mapper_notes = ""
    if "mapper_last" not in st.session_state:
        st.session_state.mapper_last = None

    uploaded = st.file_uploader(
        "Optional text PDF (scans with no text will be empty)",
        type=["pdf"],
        key="mapper_pdf",
    )
    if st.button("Append PDF text to notes") and uploaded is not None:
        from src.research_map import extract_pdf_text

        pdf_text = extract_pdf_text(uploaded.getvalue())
        if not pdf_text:
            st.warning(
                "No selectable text in that PDF (often a scan). Paste numbers instead."
            )
        else:
            st.session_state.mapper_notes = (
                (st.session_state.mapper_notes + "\n" + pdf_text).strip()
            )
            st.rerun()

    st.session_state.mapper_notes = st.text_area(
        "Running notes (add more and map again to fill fields)",
        value=st.session_state.mapper_notes,
        height=180,
    )
    extra = st.text_input("Add more notes this turn")
    col_a, col_b = st.columns(2)
    with col_a:
        map_clicked = st.button("Map notes to catalog fields")
    with col_b:
        if st.button("Clear notes"):
            st.session_state.mapper_notes = ""
            st.session_state.mapper_last = None
            st.rerun()

    if map_clicked:
        combined = st.session_state.mapper_notes.strip()
        if extra.strip():
            combined = (combined + "\n" + extra.strip()).strip()
            st.session_state.mapper_notes = combined
        if not combined:
            st.error("Enter notes first.")
        else:
            from src.nvidia_client import NvidiaConfigError
            from src.research_map import map_and_score

            try:
                st.session_state.mapper_last = map_and_score(combined)
            except NvidiaConfigError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Mapping failed: {exc}")

    payload = st.session_state.mapper_last
    if not payload:
        return

    st.subheader("Results")
    st.caption(payload.get("disclaimer", RESEARCH_DISCLAIMER))
    source = payload.get("mapper_source")
    if source == "local_regex":
        st.info(
            "Mapped with the **local field extractor** (NVIDIA chat was unavailable). "
            "Use `feature: number` lines. This is not an LLM diagnosis."
        )
    elif source == "nvidia":
        used = payload.get("nvidia_model_used")
        st.caption(
            f"NIM field extraction model: {used}" if used else "NIM field extraction."
        )
    st.info(payload.get("consultancy", ""))
    unmapped = payload.get("unmapped_phrases") or []
    if unmapped:
        st.markdown("**Phrases not mapped to a catalog field:** " + ", ".join(unmapped))

    for row in payload.get("results") or []:
        title = row.get("title", row.get("key"))
        st.markdown(f"#### {title}")
        cov = row.get("coverage_percent")
        st.write(f"Field coverage: **{cov}%** (not a disease %)")
        pct = row.get("research_positive_percent")
        if pct is None:
            st.warning(row.get("message", "Not enough of this table’s own numbers yet — no research score."))
        else:
            st.metric(
                "Research score / 100 for this table only (not a diagnosis)",
                f"{pct}",
            )
            st.caption(row.get("message", ""))
        missing = row.get("missing") or []
        if missing:
            show = missing[:12]
            more = f" (+{len(missing) - 12} more)" if len(missing) > 12 else ""
            st.markdown("Add notes that fill: `" + "`, `".join(show) + "`" + more)
        st.markdown(row.get("specialty_hint", ""))
        st.divider()


def page_about() -> None:
    st.title("About and limits")
    st.markdown(
        """
- Educational / research software only.
- Do not treat outputs as diagnosis, treatment, or “you have X”.
- The **Research notes mapper** only fills fields for **existing public tables**.
- It does not recommend named doctors. Search licensed care in your area yourself.
- No hospital EHR dumps. Text PDFs are parsed only for catalog field names.
- Hybrid QML uses a **few** selected features because near-term circuits are small.
- Extra disease **names** in a toy symptom CSV are not medicine at scale.
- Bone-break / spine image trainers (if present) cover **that dataset’s labels only**.
- Quantum models may win, tie, or lose; runtime is part of the comparison.
"""
    )
    st.markdown(LONG_DISCLAIMER)


def main() -> None:
    disclaimer_banner()
    page = st.sidebar.radio("Pages", PAGES)
    st.sidebar.caption(RESEARCH_DISCLAIMER)
    dispatch = {
        "Home": page_home,
        "Data overview": page_data,
        "Classical results": page_classical,
        "QML comparison": page_qml,
        "Decision support": page_decision_support,
        "Explainability": page_explainability,
        "Research notes mapper": page_research_mapper,
        "Extra research tables": page_extra_tables,
        "Image experiments": page_images,
        "How to read metrics": page_metrics_help,
        "Demo script": page_demo_script,
        "About and limits": page_about,
    }
    dispatch[page]()


if __name__ == "__main__":
    main()
