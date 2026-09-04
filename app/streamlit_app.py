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
    "Research notes mapper",
    "Extra research tables",
    "Image experiments",
    "How to read metrics",
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
        "Hybrid models (VQC, QSVC) run on a **simulator** using the Phase 2 "
        "selected columns. Quantum is **not** assumed to win."
    )
    frame = load_metrics_csv("qml_vs_classical_metrics.csv")
    if frame is None:
        st.warning("Quantum results not generated yet. Run `python -m src.train_qml`.")
        return
    metric_cards(frame)
    st.dataframe(frame, use_container_width=True)
    show_png("qml_roc_curve_comparison.png")
    show_png("qml_model_metric_comparison.png")
    report = _paths()["reports"] / "hybrid_comparison.md"
    if report.is_file():
        st.subheader("Written comparison")
        st.markdown(report.read_text(encoding="utf-8"))


def page_extra_tables() -> None:
    st.title("Extra research tables")
    st.markdown(
        "Each CSV is its own experiment. This page is **not** a combined diagnosis tool."
    )
    metrics_dir = _paths()["metrics"]
    files = sorted(metrics_dir.glob("*_classical_model_metrics.csv"))
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
            st.warning(row.get("message", "Insufficient fields — no %."))
        else:
            st.metric(
                "Research positive-class probability for this public table "
                "(not a diagnosis)",
                f"{pct}%",
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
        "Research notes mapper": page_research_mapper,
        "Extra research tables": page_extra_tables,
        "Image experiments": page_images,
        "How to read metrics": page_metrics_help,
        "About and limits": page_about,
    }
    dispatch[page]()


if __name__ == "__main__":
    main()
