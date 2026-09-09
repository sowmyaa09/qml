"""Write explanation.pdf — project briefing for the team. Not a clinical document."""

from __future__ import annotations

from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from src.utils import get_project_root, RESEARCH_DISCLAIMER


NAVY = colors.HexColor("#0a122a")
TEAL = colors.HexColor("#0f766e")
SLATE = colors.HexColor("#334155")
WARN = colors.HexColor("#9a3412")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ExTitle",
            parent=base["Heading1"],
            fontSize=18,
            textColor=NAVY,
            spaceAfter=6,
            leading=22,
        ),
        "h2": ParagraphStyle(
            "ExH2",
            parent=base["Heading2"],
            fontSize=13,
            textColor=TEAL,
            spaceBefore=14,
            spaceAfter=6,
            leading=16,
        ),
        "h3": ParagraphStyle(
            "ExH3",
            parent=base["Heading3"],
            fontSize=11,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=4,
            leading=14,
        ),
        "body": ParagraphStyle(
            "ExBody",
            parent=base["Normal"],
            fontSize=10,
            textColor=SLATE,
            leading=14,
            spaceAfter=8,
        ),
        "warn": ParagraphStyle(
            "ExWarn",
            parent=base["Normal"],
            fontSize=9,
            textColor=WARN,
            leading=12,
            spaceAfter=10,
        ),
        "small": ParagraphStyle(
            "ExSmall",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#64748b"),
            leading=11,
        ),
    }


def _bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=12) for item in items],
        bulletType="bullet",
        start="•",
        leftIndent=18,
        spaceAfter=8,
    )


def build_explanation_pdf(output_path=None) -> str:
    root = get_project_root()
    path = root / "explanation.pdf" if output_path is None else output_path
    styles = _styles()

    story = [
        Paragraph("Q-Care Detect / LAKSHYA — Project explanation", styles["title"]),
        Paragraph(
            f"SIH 2026 problem SIH26139 (Egreen Quanta). Written {date.today().isoformat()}. "
            "Research and education only.",
            styles["small"],
        ),
        Spacer(1, 6),
        Paragraph(RESEARCH_DISCLAIMER, styles["warn"]),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1"), spaceAfter=10),
        Paragraph("1. What this project is", styles["h2"]),
        Paragraph(
            "This repo is a <b>hybrid quantum–classical machine learning research platform</b> "
            "for public biomedical <b>benchmark tables</b>. The assignment theme is early disease "
            "detection; the software does <b>research risk classification on one table at a time</b>. "
            "It is not a medical device, not a diagnosis tool, and not a symptom checker. "
            "The public UI is branded <b>LAKSHYA</b> (<font face='Courier'>stitchfrontend/</font>).",
            styles["body"],
        ),
        Paragraph(
            "Typical flow: load a public table → classical cleaning, stratified 80/20 split "
            "(seed 42), scaling and feature selection → train classical baselines and small "
            "simulator QML models on the same reduced columns → compare F1, AUC, runtime, and "
            "paired statistics. Each model only sees that table’s columns and one label.",
            styles["body"],
        ),
        Paragraph("2. Are we using QML, classical ML, or hybrid ML?", styles["h2"]),
        Paragraph(
            "We use <b>hybrid ML</b>: most of the pipeline is classical; a <b>small quantum "
            "(or quantum-inspired) block</b> runs on a <b>classical simulator</b> (Qiskit Aer "
            "statevector). We are <b>not</b> running a hospital quantum computer, and we are "
            "<b>not</b> training a quantum model on 30 raw Wisconsin columns or on images.",
            styles["body"],
        ),
        Paragraph("Why hybrid (not “pure QML”)", styles["h3"]),
        Paragraph(
            "Near-term circuits have few qubits and shallow depth. Encoding dozens of raw labs "
            "into a circuit is a poor fit. So classical code reduces the table to about "
            "<b>4–8 selected features</b> (one qubit per feature in v1). That is the hybrid "
            "split: computers do load, clip, scale, SelectKBest, and evaluation; the quantum "
            "library builds a small circuit or kernel on those k numbers.",
            styles["body"],
        ),
        Paragraph("Why not claim “QML is more accurate”", styles["h3"]),
        Paragraph(
            "On Wisconsin on this machine, <b>classical logistic regression beat VQC/QSVC on F1</b>. "
            "QSVC was statistically <b>indistinguishable</b> from an RBF SVM on the same k columns "
            "(McNemar p = 1.000). VQC/QNN were worse. That is an acceptable research outcome. "
            "Pitch <b>architecture and compute cost</b>, not a quantum accuracy win.",
            styles["body"],
        ),
        Paragraph("3. How the hybrid models work", styles["h2"]),
        Paragraph(
            "Shared front end for QML v1: train-only feature selection (typical kept Wisconsin "
            "features include mean perimeter, mean concave points, worst radius, worst perimeter, "
            "worst area, worst concave points). Values are scaled. Then one of:",
            styles["body"],
        ),
        Paragraph("Quantum kernel SVM (QSVC)", styles["h3"]),
        Paragraph(
            "A <b>ZZFeatureMap</b> encodes the k numbers as rotation angles and adds ZZ "
            "entangling gates (reps = 2 by default). "
            "<b>FidelityStatevectorKernel</b> computes the overlap of those quantum states "
            "(exact simulator math, not noisy shots — shot-based kernels hung here). "
            "A classical SVM then uses that kernel matrix like any other kernel SVM. "
            "The honest control is an <b>RBF SVM on the same k columns</b>: if QSVC ≈ RBF, "
            "the quantum kernel is not buying extra accuracy on this table.",
            styles["body"],
        ),
        Paragraph("Variational quantum classifier (VQC)", styles["h3"]),
        Paragraph(
            "Same feature map, plus a trainable <b>RealAmplitudes</b> ansatz. A classical "
            "optimizer (<b>COBYLA</b>, maxiter 60 by default) updates circuit parameters to "
            "separate the two classes. This is hybrid because the cost function is evaluated "
            "from the circuit, but the optimizer and data pipeline are classical. VQC is slow "
            "on the simulator compared with logistic regression.",
            styles["body"],
        ),
        Paragraph("Optional QNN", styles["h3"]),
        Paragraph(
            "<b>EstimatorQNN</b> + <b>NeuralNetworkClassifier</b> (fit on ±1 labels). Ranking "
            "uses raw expectation values, not calibrated probabilities. Optional via "
            "<font face='Courier'>python -m src.train_qml --with-qnn</font>.",
            styles["body"],
        ),
        Paragraph("What stays classical", styles["h3"]),
        _bullets(
            [
                "Logistic regression and random forest on full or reduced tables.",
                "Large tables (cardio, BRFSS, etc.) stay classical; QSVC refuses tables over 5000 rows.",
                "Optional laptop CNNs (WBC / MSK images) are PyTorch, not QML.",
                "Decision support = probability band + threshold on <b>one</b> label only.",
            ],
            styles["body"],
        ),
        Paragraph("4. Technology stack", styles["h2"]),
        Paragraph("Data and classical ML", styles["h3"]),
        _bullets(
            [
                "Python 3, pandas, NumPy, scikit-learn, joblib, matplotlib (Agg backend).",
                "Public tables (sklearn Wisconsin, UCI/Kaggle-style sets). Duplicate rows dropped by default.",
            ],
            styles["body"],
        ),
        Paragraph("Hybrid QML (simulator)", styles["h3"]),
        _bullets(
            [
                "Qiskit, Qiskit Aer, Qiskit Machine Learning, Qiskit Algorithms.",
                "No real QPU in this delivery; Aer statevector is allowed.",
            ],
            styles["body"],
        ),
        Paragraph("Optional deep learning", styles["h3"]),
        Paragraph(
            "PyTorch / torchvision for small image experiments when CUDA is available. "
            "Not fused with tabular QML into one diagnosis.",
            styles["body"],
        ),
        Paragraph("Apps and API", styles["h3"]),
        _bullets(
            [
                "<b>LAKSHYA:</b> Vite + React + TypeScript + Tailwind in <font face='Courier'>stitchfrontend/</font>; FastAPI serves the production build.",
                "<b>API:</b> FastAPI + Uvicorn — catalog, research-score, paste-a-record, interview, locked PDF.",
                "<b>Streamlit:</b> research dashboard (<font face='Courier'>app/streamlit_app.py</font>).",
                "<b>PDF:</b> reportlab + pypdf (generated open-password; name/DOB are labels only).",
            ],
            styles["body"],
        ),
        Paragraph("Optional cloud pieces", styles["h3"]),
        _bullets(
            [
                "NVIDIA NIM (OpenAI-compatible) to extract <font face='Courier'>field: number</font> pairs into one selected table — not a disease picker.",
                "Supabase can store a fingerprint of PDF unlock keys; the PDF still works without it.",
            ],
            styles["body"],
        ),
        Paragraph("5. What we refuse (product boundaries)", styles["h2"]),
        _bullets(
            [
                "No fused “what disease do I have?” score across tables.",
                "No general symptom checker or invented ICD lists.",
                "No ranking of named doctors; specialty <b>domain hints</b> only.",
                "No concatenating duplicate Wisconsin copies to fake more patients.",
            ],
            styles["body"],
        ),
        Paragraph("6. How to run (short)", styles["h2"]),
        Paragraph(
            "Activate <font face='Courier'>.venv</font>. Train: "
            "<font face='Courier'>python -m src.train_classical</font>, "
            "<font face='Courier'>python -m src.train_phase2</font>, "
            "<font face='Courier'>python -m src.train_qml --with-qnn</font>. "
            "UI: <font face='Courier'>cd stitchfrontend; npm install; npm run build</font> then "
            "<font face='Courier'>uvicorn src.api_server:app --reload --port 8000</font>. "
            "Tests: <font face='Courier'>pytest</font>.",
            styles["body"],
        ),
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1"), spaceAfter=8),
        Paragraph(
            "Regenerate this file: python -m src.generate_explanation_pdf",
            styles["small"],
        ),
    ]

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Q-Care Detect project explanation",
        author="Q-Care Detect research prototype",
    )
    doc.build(story)
    return str(path)


if __name__ == "__main__":
    out = build_explanation_pdf()
    print(out)
