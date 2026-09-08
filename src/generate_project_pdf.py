"""
Generate a comprehensive, publication-quality PDF report for Q-Care Detect:
- Executive Summary & Project Mission (SIH 2026 SIH26139)
- Medical & Ethical Safety Boundaries
- System Architecture & End-to-End Pipeline
- Complete Technology Stack (Quantum, Classical ML, Deep Learning, API, UI, Cloud LLM)
- Empirical Results & Statistical Significance Benchmark
- Detailed Analysis of Critical Flaws & Practical Bottlenecks
- Strategic Future Improvements & Next-Phase Roadmap
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render total page count
    along with running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F172A")) # Dark Slate
        
        # Draw running header on page 2 and above
        if self._pageNumber > 1:
            self.drawString(54, 750, "Q-Care Detect (SIH26139) | Hybrid QML for Early Disease Detection")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(612 - 54, 750, "Comprehensive Project & Technical Analysis Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, 742, 612 - 54, 742)

        # Draw running footer on all pages
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 48, 612 - 54, 48)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 36, "CONFIDENTIAL & RESEARCH ONLY — Not a Medical Device. Not for Clinical Use.")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    # Colors
    c_primary = colors.HexColor("#0F172A")    # Deep Navy / Slate 900
    c_teal = colors.HexColor("#0D9488")       # Teal 600
    c_cyan = colors.HexColor("#0284C7")       # Sky 600
    c_coral = colors.HexColor("#E11D48")      # Rose 600
    c_amber = colors.HexColor("#D97706")      # Amber 600
    c_dark = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#475569")      # Slate 600
    c_bg_light = colors.HexColor("#F8FAFC")   # Slate 50
    c_border = colors.HexColor("#E2E8F0")     # Slate 200

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_teal,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_cyan,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'DocBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_text = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    callout_alert = ParagraphStyle(
        'CalloutAlert',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_coral
    )

    callout_warning = ParagraphStyle(
        'CalloutWarning',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_amber
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_dark
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # ==========================================
    # HEADER / TITLE BLOCK
    # ==========================================
    story.append(Paragraph("Q-Care Detect: System Architecture & Technical Report", title_style))
    story.append(Paragraph("Hybrid Quantum Machine Learning Platform for Early Disease Risk Research (SIH26139)", subtitle_style))
    
    meta_info = (
        f"<b>Team / Organization:</b> Egreen Quanta (SIH 2026 - SIH26139) &nbsp;|&nbsp; "
        f"<b>Repository:</b> sowmyaa09/qml &nbsp;|&nbsp; "
        f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
    )
    story.append(Paragraph(meta_info, body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_teal, spaceBefore=4, spaceAfter=10))

    # ==========================================
    # 1. EXECUTIVE SUMMARY & MEDICAL SAFETY BOUNDARY
    # ==========================================
    story.append(Paragraph("1. Executive Summary & Ethical Safety Boundaries", h1_style))
    
    disclaimer_box = [
        [
            Paragraph("<b>CRITICAL SAFETY & MEDICAL DISCLAIMER:</b>", callout_alert),
        ],
        [
            Paragraph(
                "<b>Q-Care Detect is strictly an educational and research exploration platform, NOT a clinical diagnostic device.</b> "
                "It operates exclusively on anonymized public biomedical research benchmarks (e.g. Wisconsin Breast Cancer, CDC BRFSS, "
                "UCI Heart cohorts, Coimbra). The platform strictly outputs <i>research risk classifications</i> and probability bands. "
                "It does not prescribe treatment, provide clinical diagnosis, or recommend medical interventions. "
                "Cross-disease joint probability fusion ('multi-disease oracle') is explicitly forbidden to prevent fabricated clinical scores.",
                callout_text
            )
        ]
    ]
    t_disclaimer = Table(disclaimer_box, colWidths=[504])
    t_disclaimer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF1F2")), # Rose 50
        ('BOX', (0,0), (-1,-1), 1, c_coral),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
    ]))
    story.append(t_disclaimer)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Project Mission:</b> Early disease risk screening is a foundational challenge in modern healthcare. "
        "High-dimensional biomedical datasets pose complex non-linear correlation structures. "
        "Q-Care Detect explores the integration of <b>Hybrid Quantum-Classical Machine Learning (QML)</b>, combining rigorous "
        "classical preprocessing and feature selection with quantum variational and quantum kernel algorithms (VQC, QSVC, QNN) "
        "on simulated statevectors. The project's core tenet is <b>uncompromising scientific honesty</b>: quantum classifiers are "
        "rigorously evaluated against matched classical baselines (Logistic Regression, Random Forest, RBF Kernel SVM) using "
        "stratified bootstrapping, paired McNemar tests, DeLong AUC tests, and repeated cross-validation.",
        body_style
    ))

    # ==========================================
    # 2. END-TO-END SYSTEM ARCHITECTURE
    # ==========================================
    story.append(Paragraph("2. System Architecture & Workflow Pipeline", h1_style))
    story.append(Paragraph(
        "The Q-Care Detect architecture follows a strictly partitioned 6-stage lifecycle to prevent data leakage and ensure reproducibility:",
        body_style
    ))

    arch_steps = [
        ("Phase 1: Classical Baseline & Data Loading", 
         "Loads validated public tables, enforces zero data leakage by computing all scalers, quantiles, and imputations strictly on training rows (80/20 stratified split, random_state=42). Establishes baseline metrics using tuned Logistic Regression and compact Random Forests."),
        ("Phase 2: Dimensionality Reduction & Feature Selection", 
         "Reduces high-dimensional feature spaces (e.g. 30 WDBC features down to 4–8 salient predictors) using training-only SelectKBest (ANOVA F-value) and correlation filtering, matching NISQ qubit constraints."),
        ("Phase 3: Hybrid Quantum Classifier Pipeline", 
         "Implements Quantum Support Vector Classifiers (QSVC with ZZFeatureMap & FidelityStatevectorKernel), Variational Quantum Classifiers (VQC with RealAmplitudes ansatz & COBYLA optimizer), and Quantum Neural Networks (EstimatorQNN). Includes exact classical RBF SVM kernel controls."),
        ("Phase 4: Statistical Significance & Explainability", 
         "Executes non-parametric stratified bootstrap confidence intervals (95%), paired McNemar contingency tests, DeLong ROC-AUC tests, and permutation feature importance + single-sample step-by-step linear attribution."),
        ("Phase 5: Decision Support & Probability Calibration", 
         "Implements single-label decision support: probability bands (Low/Moderate/Elevated), threshold tuning curves (sensitivity-first vs balanced F1), Platt scaling, and Brier calibration curves."),
        ("Phase 6: Multi-Interface Delivery & Research Mapping", 
         "Interactive multi-page Streamlit dashboard, local FastAPI server (`GET /v1/catalog`, `POST /v1/map-research`), and NVIDIA Cloud NIM LLM schema mapping with robust local regex fallback.")
    ]

    for title, desc in arch_steps:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", bullet_style))
    story.append(Spacer(1, 6))

    # ==========================================
    # 3. COMPREHENSIVE TECHNOLOGY STACK
    # ==========================================
    story.append(Paragraph("3. Comprehensive Technology Stack", h1_style))
    story.append(Paragraph(
        "Every layer of the platform leverages industry-standard open-source and enterprise frameworks chosen for numerical precision, performance, and reproducibility:",
        body_style
    ))

    tech_table_data = [
        [Paragraph("Category", table_header), Paragraph("Technologies & Frameworks", table_header), Paragraph("Role & Architecture Details in Q-Care Detect", table_header)],
        
        [Paragraph("<b>Quantum Machine Learning</b>", table_cell),
         Paragraph("<b>Qiskit 1.x</b><br/><b>Qiskit Machine Learning</b><br/><b>Qiskit Aer</b>", table_cell),
         Paragraph("Simulates parameterized quantum circuits; <code>ZZFeatureMap</code> (2-qubit entanglement), <code>RealAmplitudes</code> ansatz, <code>FidelityStatevectorKernel</code> for QSVC, <code>EstimatorQNN</code>, and <code>COBYLA</code> optimizer.", table_cell)],
        
        [Paragraph("<b>Classical Machine Learning</b>", table_cell),
         Paragraph("<b>Scikit-Learn</b><br/><b>NumPy & SciPy</b><br/><b>Joblib</b>", table_cell),
         Paragraph("Data pipelines (Pipeline, StandardScaler, SimpleImputer), LogisticRegression (balanced), RandomForestClassifier (compress=3), SVC (RBF kernel control), CalibratedClassifierCV (Platt scaling), ANOVA feature selection.", table_cell)],
        
        [Paragraph("<b>Statistical Rigor & Metrics</b>", table_cell),
         Paragraph("<b>Bootstrap CIs</b><br/><b>Statsmodels</b><br/><b>DeLong / McNemar</b>", table_cell),
         Paragraph("1,000-resample stratified bootstrap for F1/AUC 95% confidence intervals, paired McNemar exact tests for contingency differences, DeLong test for paired ROC-AUC curves, 5x5 Repeated Stratified CV.", table_cell)],
        
        [Paragraph("<b>Deep Learning (Optional Track)</b>", table_cell),
         Paragraph("<b>PyTorch</b><br/><b>Torchvision</b><br/><b>CUDA 12.x</b>", table_cell),
         Paragraph("Custom convolutional neural networks for separate medical imaging tracks: White Blood Cell (WBC) morphological classification and Musculoskeletal (MSK) bone fracture / spinal anomaly screening.", table_cell)],
        
        [Paragraph("<b>API & Backend Services</b>", table_cell),
         Paragraph("<b>FastAPI</b><br/><b>Uvicorn (ASGI)</b><br/><b>Pydantic v2</b>", table_cell),
         Paragraph("REST API exposing catalog metadata, model health endpoints, and asynchronous schema-mapping endpoints (`/v1/catalog`, `/v1/map-research`). Fully typed schemas and JSON validation.", table_cell)],
        
        [Paragraph("<b>Cloud LLM / NIM Integration</b>", table_cell),
         Paragraph("<b>NVIDIA Cloud NIM</b><br/><b>OpenAI SDK</b><br/><b>Meta Muse Glimmer</b>", table_cell),
         Paragraph("Extracts structured clinical table parameters from unstructured natural language research notes via <code>meta/muse-glimmer-30b</code>; resilient offline fallback to deterministic regex pattern matchers.", table_cell)],
        
        [Paragraph("<b>User Interface & Dashboard</b>", table_cell),
         Paragraph("<b>Streamlit</b><br/><b>Matplotlib (Agg backend)</b><br/><b>Seaborn</b>", table_cell),
         Paragraph("Multi-page interactive research dashboard (Overview, Benchmarks, QML Deep-Dive, Decision Support, Explainability, Image Modalities). Matplotlib Agg backend prevents cross-thread GUI crashes.", table_cell)],
        
        [Paragraph("<b>Testing & Code Quality</b>", table_cell),
         Paragraph("<b>Pytest</b><br/><b>Python 3.10+</b><br/><b>ReportLab</b>", table_cell),
         Paragraph("Automated test suite verifying data loaders, leak-free pipeline transforms, model outputs, schema validations, and PDF reporting generation.", table_cell)]
    ]

    t_tech = Table(tech_table_data, colWidths=[110, 110, 284])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # ==========================================
    # 4. EMPIRICAL RESULTS & BENCHMARKS
    # ==========================================
    story.append(Paragraph("4. Empirical Results & Statistical Significance Benchmark", h1_style))
    story.append(Paragraph(
        "Q-Care Detect measures performance across multiple public benchmarks with full statistical transparency. "
        "Below are the verified held-out test split results on the primary benchmark (Wisconsin Breast Cancer, 80/20 split):",
        body_style
    ))

    benchmark_data = [
        [Paragraph("Model Architecture", table_header), Paragraph("Feature Set", table_header), Paragraph("F1-Score [95% CI]", table_header), Paragraph("Recall", table_header), Paragraph("ROC-AUC", table_header), Paragraph("Train Time", table_header)],
        [Paragraph("<b>Logistic Regression</b>", table_cell), Paragraph("All 30 raw features", table_cell), Paragraph("0.9762 [0.930, 1.000]", table_cell), Paragraph("0.9762", table_cell), Paragraph("0.9977", table_cell), Paragraph("0.02 s", table_cell)],
        [Paragraph("<b>RBF Kernel SVM (Control)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.9512 [0.897, 0.988]", table_cell), Paragraph("0.9286", table_cell), Paragraph("0.9970", table_cell), Paragraph("0.01 s", table_cell)],
        [Paragraph("<b>QSVC (Quantum Kernel)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.9500 [0.895, 0.988]", table_cell), Paragraph("0.9048", table_cell), Paragraph("0.9937", table_cell), Paragraph("2.12 s", table_cell)],
        [Paragraph("<b>Logistic Regression (Control)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.9412 [0.886, 0.988]", table_cell), Paragraph("0.9524", table_cell), Paragraph("0.9858", table_cell), Paragraph("0.01 s", table_cell)],
        [Paragraph("<b>Random Forest (100 trees)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.9157 [0.850, 0.976]", table_cell), Paragraph("0.9048", table_cell), Paragraph("0.9830", table_cell), Paragraph("0.11 s", table_cell)],
        [Paragraph("<b>QNN (EstimatorQNN)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.5867 [0.452, 0.701]", table_cell), Paragraph("0.5238", table_cell), Paragraph("0.8415", table_cell), Paragraph("18.40 s", table_cell)],
        [Paragraph("<b>VQC (Variational Classifier)</b>", table_cell), Paragraph("6 selected features", table_cell), Paragraph("0.5806 [0.468, 0.681]", table_cell), Paragraph("0.4286", table_cell), Paragraph("0.8468", table_cell), Paragraph("604.20 s", table_cell)],
    ]

    t_bench = Table(benchmark_data, colWidths=[120, 84, 110, 50, 65, 75])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_teal),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Key Statistical Insights:</b>", body_bold))
    stats_insights = [
        "<b>QSVC vs RBF SVM Indistinguishability:</b> Paired McNemar contingency test yields p = 1.000, and 95% bootstrap confidence intervals heavily overlap. QSVC matches classical RBF SVM accuracy, but does not outperform it.",
        "<b>Compute Overhead:</b> While QSVC achieves competitive accuracy, its kernel evaluation runtime (2.12 s) is ~200x slower than classical RBF SVM (0.01 s). VQC optimization took >600 seconds with inferior convergence.",
        "<b>Qubit Scaling Ablation:</b> Increasing qubits/features for QSVC shows $k=4$ (F1: 0.8889, 1.40 s), $k=6$ (F1: 0.9500, 2.04 s), and $k=8$ (F1: 0.9524, 3.20 s), demonstrating diminishing returns beyond 6 selected features.",
        "<b>5x5 Repeated Cross-Validation:</b> Across 25 resampled folds (preprocessing refit inside each fold to prevent leakage): LR scored 0.9314 ± 0.024, RBF SVM scored 0.9268 ± 0.025, and QSVC scored 0.9093 ± 0.037."
    ]
    for ins in stats_insights:
        story.append(Paragraph(f"• {ins}", bullet_style))
    story.append(Spacer(1, 8))

    # ==========================================
    # 5. IN-DEPTH ANALYSIS OF PROJECT FLAWS & LIMITATIONS
    # ==========================================
    story.append(Paragraph("5. Comprehensive Analysis of Flaws & Practical Bottlenecks", h1_style))
    story.append(Paragraph(
        "A cornerstone of rigorous MedTech engineering is acknowledging failure modes, architectural ceilings, and data constraints. "
        "The primary flaws identified in the current system are:",
        body_style
    ))

    flaws = [
        ("Flaw 1: Classical Superiority & No Quantum Advantage on Tabular Data",
         "Empirical testing proves that classical linear models (Logistic Regression) and classical non-linear kernels (RBF SVM) match or exceed quantum models in F1-score and ROC-AUC, while executing hundreds of times faster. On standard biomedical tables, tabular feature correlations do not possess the high-degree non-local entanglement that theoretically benefits quantum Hilbert space embeddings."),
        
        ("Flaw 2: Statevector Simulation vs Real NISQ Hardware Realities",
         "The current platform runs on classical statevector simulation (Qiskit Aer), assuming pure unitary gates with zero decoherence, zero thermal noise, and infinite measurement shots. Real Noisy Intermediate-Scale Quantum (NISQ) QPUs suffer from gate fidelities (~99%), readout errors, crosstalk, and finite shot noise, which will degrade decision boundaries unless expensive error mitigation is applied."),
        
        ("Flaw 3: Qubit Scaling Bottleneck & Dimensionality Compression",
         "State-of-the-art quantum simulators and near-term NISQ devices cannot natively process raw biomedical tables with 30–100 features without exponential statevector simulation cost ($2^N$). The pipeline is forced to rely on classical ANOVA feature selection to distill datasets down to 4–8 features, discarding potentially vital secondary clinical signals."),
        
        ("Flaw 4: Widespread Data Duplication & Leakage in Public Benchmarks",
         "The project's dataset audit revealed severe integrity issues in popular public repositories. Specifically, the widely-used Kaggle <code>heart_disease</code> (johnsmith88) dataset was found to contain <b>70.5% duplicate rows (723 / 1025)</b>. Naive train/test splitting caused identical patients to appear in both sets, yielding a fake Random Forest F1 of 1.000. While our pipeline fixed this with strict deduplication and multi-cohort pooling (UCI 4-hospital pool), benchmark quality across open-source biomedical repositories remains fragile."),
        
        ("Flaw 5: Inability to Perform Joint Cross-Disease Clinical Diagnosis",
         "Patients in clinical reality present comorbidities (e.g. hypertension combined with diabetes and renal impairment). Because public datasets exist in siloed tables with disparate patient cohorts and incompatible feature schemas, the platform cannot compute a unified joint risk probability. Creating a synthetic 'all-in-one disease oracle' would be statistically fraudulent."),
        
        ("Flaw 6: Variational Circuit Optimization Hurdles (Barren Plateaus & COBYLA)",
         "VQC and QNN architectures suffer from shallow loss gradients (barren plateau phenomena) and slow derivative-free optimizers (COBYLA). In tests, VQC convergence stalled at F1 ~0.58 despite 600 seconds of optimization, highlighting the extreme difficulty of training variational quantum circuits on classical simulators.")
    ]

    for f_title, f_desc in flaws:
        story.append(Paragraph(f"<b>{f_title}:</b> {f_desc}", bullet_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    # ==========================================
    # 6. STRATEGIC FUTURE IMPROVEMENTS & ROADMAP
    # ==========================================
    story.append(Paragraph("6. Future Improvements & Strategic Roadmap", h1_style))
    story.append(Paragraph(
        "To advance Q-Care Detect from a research prototype toward a robust clinical decision-support ecosystem, "
        "the following engineering and scientific enhancements are proposed:",
        body_style
    ))

    improvements = [
        ("1. Real QPU Deployment with Error Mitigation (IBM Quantum & Braket)",
         "Transition from ideal statevector simulation to cloud quantum hardware via <b>Qiskit Runtime Primitives (Sampler V2, Estimator V2)</b>. Implement Zero-Noise Extrapolation (ZNE), Pauli Twirling, and Readout Error Mitigation (M3) to evaluate genuine NISQ noise resilience."),
        
        ("2. Advanced Expressive Quantum Feature Maps & Data Re-uploading",
         "Replace standard ZZFeatureMaps with <b>Data Re-uploading Quantum Classifiers</b> and <b>Projected Quantum Kernels</b> (Huang et al.). Projected kernels map quantum states back into reduced classical feature representations, avoiding kernel concentration and barren plateaus while preserving quantum expressivity."),
        
        ("3. Quantum Natural Gradient (QNG) & SPSA Optimization",
         "Replace derivative-free COBYLA with Quantum Natural Gradient (QNG) using the Fubini-Study metric tensor, or Simultaneous Perturbation Stochastic Approximation (SPSA). This accelerates variational optimization convergence by 10–50x and navigates complex loss landscapes."),
        
        ("4. Privacy-Preserving Quantum Federated Learning (FedQML)",
         "Enable multi-hospital collaborative model training without centralizing patient data. Implement federated aggregation of parameterized quantum circuit weights (QNN/VQC ansatz weights) combined with Differential Privacy guarantees (&epsilon;, &delta;)."),
        
        ("5. Conformal Prediction & Calibrated Uncertainty Bands",
         "Integrate Conformal Prediction frameworks to output mathematically guaranteed confidence sets (e.g. 95% coverage guarantees) rather than point risk estimates, providing clinicians with rigorous bounded uncertainty."),
        
        ("6. True Multimodal Fusion on Paired Clinical Cohorts",
         "When paired hospital cohorts are available (e.g. Stanford AIMI or UK Biobank), implement late-fusion cross-attention networks that merge tabular lab chemistry, imaging embeddings (Vision Transformers / PyTorch CNNs), and clinical text notes."),
        
        ("7. SaMD / ISO 13485 Regulatory Alignment",
         "Establish end-to-end audit trails, model change protocols, bias and fairness testing across demographic subgroups (age, sex, ethnicity), and formal verification in accordance with Software as a Medical Device (SaMD) FDA/CE-MDR guidelines.")
    ]

    for imp_title, imp_desc in improvements:
        story.append(Paragraph(f"<b>{imp_title}:</b> {imp_desc}", bullet_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 10))

    # ==========================================
    # 7. SUMMARY TABLE & VERDICT
    # ==========================================
    story.append(Paragraph("7. Final Verdict & Deliverable Checklist", h1_style))
    
    summary_box = [
        [Paragraph("Project Deliverable Status Summary", table_header), Paragraph("Evaluation Status & Notes", table_header)],
        [Paragraph("D1–D6: Core Baseline & Pipeline", table_cell_bold), Paragraph("COMPLETE: Leak-free preprocessing, Logistic Regression, Random Forest, Pytest suite.", table_cell)],
        [Paragraph("D7: Feature Selection", table_cell_bold), Paragraph("COMPLETE: SelectKBest (k=4, 6, 8) fit strictly on train split.", table_cell)],
        [Paragraph("D8–D9: Hybrid QML & Benchmark", table_cell_bold), Paragraph("COMPLETE: QSVC, VQC, QNN, RBF SVM control, statistical significance tests.", table_cell)],
        [Paragraph("D10: Decision Support & Explainability", table_cell_bold), Paragraph("COMPLETE: Threshold sweeps, probability bands, linear feature attribution.", table_cell)],
        [Paragraph("D12–D13: Streamlit UI & FastAPI", table_cell_bold), Paragraph("COMPLETE: 6-page interactive research dashboard, REST catalog & mapping endpoints.", table_cell)],
        [Paragraph("Scientific Integrity Commitment", table_cell_bold), Paragraph("HONEST VERDICT: Classical models remain superior on current tabular data; QML serves as a vital exploratory prototype for NISQ algorithm design.", table_cell)],
    ]
    t_summary = Table(summary_box, colWidths=[180, 324])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_summary)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated project PDF at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join("outputs", "reports", "Q_Care_Detect_Comprehensive_Project_Report.pdf")
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_pdf(out_file)
    
    # Also save a copy directly in project root for convenience
    root_pdf = "Q_Care_Detect_Project_Report.pdf"
    import shutil
    shutil.copyfile(out_file, root_pdf)
    print(f"Also saved root copy at: {os.path.abspath(root_pdf)}")
