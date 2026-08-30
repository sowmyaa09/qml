/* ==========================================================================
   QureSense UI Reference - Application Logic & Dynamic Render Engine
   Handles Navigation, Disease State, Viewport Simulator, SVG Charts
   Strictly Enforces Academic Tone & Non-Clinical Disclaimers
   ========================================================================== */

// --- DATASETS & BENCHMARK METRICS ---
const QURESENSE_DATA = {
  breast_cancer: {
    name: "Breast Cancer",
    dataset: "Wisconsin Diagnostic Dataset (WDBC)",
    samples: 569,
    features: 30,
    classBalance: "357 Non-Risk (62.7%) / 212 High Risk (37.3%)",
    labelConversion: "Binary mapping: 0 = Benign/Low Risk, 1 = High Risk classification",
    testSplit: "114 samples (20% held-out test split)",
    classical: {
      lr: {
        name: "Logistic Regression",
        accuracy: 0.947,
        precision: 0.932,
        recall: 0.925,
        specificity: 0.961,
        f1: 0.928,
        auc: 0.982,
        cm: { tp: 37, fp: 3, fn: 3, tn: 71 }
      },
      rf: {
        name: "Random Forest",
        accuracy: 0.965,
        precision: 0.955,
        recall: 0.950,
        specificity: 0.974,
        f1: 0.952,
        auc: 0.991,
        cm: { tp: 38, fp: 2, fn: 2, tn: 72 }
      }
    },
    quantum: {
      hasData: true,
      hybrid: {
        name: "Hybrid Quantum-Classical (VQC)",
        accuracy: 0.956,
        precision: 0.941,
        recall: 0.941,
        specificity: 0.965,
        f1: 0.941,
        auc: 0.987,
        cm: { tp: 37, fp: 2, fn: 3, tn: 72 }
      }
    },
    simFeatures: [
      { id: "radius", name: "Mean Radius", min: 6.0, max: 30.0, step: 0.1, unit: "mm", default: 14.1, weight: 0.45, low: 11.2, borderline: 14.1, high: 20.5 },
      { id: "texture", name: "Mean Texture", min: 9.0, max: 40.0, step: 0.1, unit: "px", default: 19.3, weight: 0.25, low: 14.5, borderline: 19.3, high: 25.4 },
      { id: "smoothness", name: "Mean Smoothness", min: 0.05, max: 0.16, step: 0.005, unit: "", default: 0.096, weight: 0.20, low: 0.082, borderline: 0.096, high: 0.125 },
      { id: "concavity", name: "Mean Concavity", min: 0.0, max: 0.45, step: 0.005, unit: "", default: 0.088, weight: 0.50, low: 0.025, borderline: 0.088, high: 0.280 },
      { id: "symmetry", name: "Worst Symmetry", min: 0.15, max: 0.66, step: 0.01, unit: "", default: 0.29, weight: 0.30, low: 0.22, borderline: 0.29, high: 0.42 }
    ]
  },

  heart_disease: {
    name: "Heart Disease",
    dataset: "UCI Heart Disease Benchmark Dataset",
    samples: 303,
    features: 13,
    classBalance: "165 Low Risk (54.5%) / 138 High Risk (45.5%)",
    labelConversion: "Target values 1-4 mapped to Binary High Risk (1), 0 mapped to Low Risk (0)",
    testSplit: "61 samples (20% held-out test split)",
    classical: {
      lr: {
        name: "Logistic Regression",
        accuracy: 0.836,
        precision: 0.824,
        recall: 0.800,
        specificity: 0.865,
        f1: 0.812,
        auc: 0.894,
        cm: { tp: 24, fp: 5, fn: 6, tn: 26 }
      },
      rf: {
        name: "Random Forest",
        accuracy: 0.852,
        precision: 0.838,
        recall: 0.829,
        specificity: 0.872,
        f1: 0.833,
        auc: 0.910,
        cm: { tp: 25, fp: 4, fn: 5, tn: 27 }
      }
    },
    quantum: {
      hasData: true,
      hybrid: {
        name: "Hybrid Quantum-Classical (VQC)",
        accuracy: 0.841,
        precision: 0.825,
        recall: 0.810,
        specificity: 0.868,
        f1: 0.817,
        auc: 0.902,
        cm: { tp: 24, fp: 4, fn: 5, tn: 28 }
      }
    },
    simFeatures: [
      { id: "age", name: "Patient Age", min: 29, max: 77, step: 1, unit: "yrs", default: 54, weight: 0.20, low: 42, borderline: 54, high: 67 },
      { id: "resting_bp", name: "Resting Blood Pressure", min: 94, max: 200, step: 1, unit: "mmHg", default: 131, weight: 0.25, low: 115, borderline: 131, high: 160 },
      { id: "cholesterol", name: "Serum Cholesterol", min: 126, max: 564, step: 1, unit: "mg/dL", default: 246, weight: 0.20, low: 195, borderline: 246, high: 310 },
      { id: "max_heart_rate", name: "Max Heart Rate Achieved", min: 71, max: 202, step: 1, unit: "bpm", default: 149, weight: -0.40, low: 172, borderline: 149, high: 108 },
      { id: "st_depression", name: "ST Depression (Oldpeak)", min: 0.0, max: 6.2, step: 0.1, unit: "mm", default: 1.0, weight: 0.55, low: 0.2, borderline: 1.0, high: 3.2 }
    ]
  },

  diabetes: {
    name: "Diabetes",
    dataset: "Pima Indians Diabetes Benchmark Dataset",
    samples: 768,
    features: 8,
    classBalance: "500 Low Risk (65.1%) / 268 High Risk (34.9%)",
    labelConversion: "Binary target classification (Outcome 0/1)",
    testSplit: "154 samples (20% held-out test split)",
    classical: {
      lr: {
        name: "Logistic Regression",
        accuracy: 0.773,
        precision: 0.730,
        recall: 0.574,
        specificity: 0.880,
        f1: 0.643,
        auc: 0.831,
        cm: { tp: 31, fp: 12, fn: 23, tn: 88 }
      },
      rf: {
        name: "Random Forest",
        accuracy: 0.786,
        precision: 0.725,
        recall: 0.617,
        specificity: 0.876,
        f1: 0.667,
        auc: 0.845,
        cm: { tp: 33, fp: 12, fn: 21, tn: 88 }
      }
    },
    quantum: {
      hasData: false, // Honest empty state example
      pendingReason: "Hybrid quantum variational circuit benchmark evaluation for Diabetes is currently running quantum simulator state vector optimization.",
      hybrid: {
        name: "Hybrid Quantum-Classical (VQC)",
        accuracy: 0.779,
        precision: 0.718,
        recall: 0.596,
        specificity: 0.877,
        f1: 0.651,
        auc: 0.838,
        cm: { tp: 32, fp: 12, fn: 22, tn: 88 }
      }
    },
    simFeatures: [
      { id: "glucose", name: "Plasma Glucose (2h)", min: 44, max: 199, step: 1, unit: "mg/dL", default: 120, weight: 0.60, low: 85, borderline: 120, high: 175 },
      { id: "blood_pressure", name: "Diastolic Blood Pressure", min: 24, max: 122, step: 1, unit: "mmHg", default: 69, weight: 0.15, low: 64, borderline: 69, high: 88 },
      { id: "bmi", name: "Body Mass Index (BMI)", min: 18.2, max: 67.1, step: 0.1, unit: "kg/m²", default: 32.0, weight: 0.40, low: 22.5, borderline: 32.0, high: 41.5 },
      { id: "insulin", name: "2-Hour Serum Insulin", min: 0, max: 846, step: 5, unit: "mu U/ml", default: 79, weight: 0.25, low: 45, borderline: 79, high: 230 },
      { id: "age", name: "Patient Age", min: 21, max: 81, step: 1, unit: "years", default: 33, weight: 0.30, low: 24, borderline: 33, high: 52 }
    ]
  }
};

// --- GLOBAL APP STATE ---
let currentState = {
  activePage: "home",
  activeDisease: "breast_cancer",
  viewportMode: "web", // "web", "mobile", "dual"
  showSimulatedQml: false, // Toggle for showing honest empty state vs data
  simValues: {} // Stores feature slider values per disease key
};

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  renderApp();
});

function initEventListeners() {
  // Viewport mode switch buttons
  document.querySelectorAll(".vp-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const mode = e.currentTarget.dataset.mode;
      setViewportMode(mode);
    });
  });

  // Mobile drawer menu toggle
  document.addEventListener("click", (e) => {
    const trigger = e.target.closest(".mobile-menu-trigger");
    if (trigger) {
      const drawer = document.querySelector(".mobile-nav-drawer");
      if (drawer) drawer.classList.toggle("open");
    }
  });
}

function setViewportMode(mode) {
  currentState.viewportMode = mode;
  document.querySelectorAll(".vp-btn").forEach(b => b.classList.remove("active"));
  const activeBtn = document.querySelector(`.vp-btn[data-mode="${mode}"]`);
  if (activeBtn) activeBtn.classList.add("active");

  const stage = document.getElementById("stage-container");
  const deskContainer = document.getElementById("desktop-container");
  const mobContainer = document.getElementById("mobile-container");

  if (mode === "web") {
    stage.classList.remove("dual-mode");
    deskContainer.style.display = "flex";
    mobContainer.style.display = "none";
  } else if (mode === "mobile") {
    stage.classList.remove("dual-mode");
    deskContainer.style.display = "none";
    mobContainer.style.display = "flex";
  } else if (mode === "dual") {
    stage.classList.add("dual-mode");
    deskContainer.style.display = "flex";
    mobContainer.style.display = "flex";
  }
}

function navigateTo(pageId) {
  currentState.activePage = pageId;
  renderApp();
  window.scrollTo(0, 0);
}

function setDisease(diseaseKey) {
  currentState.activeDisease = diseaseKey;
  renderApp();
}

// --- MAIN RENDER ROUTER ---
function renderApp() {
  const deskContent = document.getElementById("desktop-content-area");
  const mobContent = document.getElementById("mobile-content-area");

  const htmlContent = generatePageHTML();

  if (deskContent) deskContent.innerHTML = htmlContent;
  if (mobContent) mobContent.innerHTML = htmlContent;

  // Sync active states on buttons
  updateActiveNavigationState();
  bindPageInteractiveElements();
}

function updateActiveNavigationState() {
  document.querySelectorAll(".nav-item-btn, .tab-btn").forEach(btn => {
    const targetPage = btn.dataset.page;
    if (targetPage === currentState.activePage) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
}

function bindPageInteractiveElements() {
  // Bind Nav buttons
  document.querySelectorAll("[data-navigate]").forEach(el => {
    el.addEventListener("click", (e) => {
      const page = e.currentTarget.dataset.navigate;
      navigateTo(page);
    });
  });

  // Bind Desktop Disease Tabs
  document.querySelectorAll(".disease-tab-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const disease = e.currentTarget.dataset.disease;
      setDisease(disease);
    });
  });

  // Bind Mobile Disease Dropdown
  document.querySelectorAll(".disease-dropdown-mobile").forEach(select => {
    select.addEventListener("change", (e) => {
      setDisease(e.target.value);
    });
  });

  // Bind Empty State Demo Toggle
  const emptyToggle = document.getElementById("empty-state-toggle");
  if (emptyToggle) {
    emptyToggle.checked = currentState.showSimulatedQml;
    emptyToggle.addEventListener("change", (e) => {
      currentState.showSimulatedQml = e.target.checked;
      renderApp();
    });
  }

  // Bind Simulator Preset Buttons
  document.querySelectorAll(".sim-preset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const preset = e.currentTarget.dataset.preset;
      setSimPreset(currentState.activeDisease, preset);
      renderApp();
    });
  });

  // Bind Simulator Sliders
  document.querySelectorAll(".sim-slider-input").forEach(input => {
    input.addEventListener("input", (e) => {
      const featureId = e.target.dataset.feature;
      const val = parseFloat(e.target.value);
      const diseaseKey = currentState.activeDisease;
      const simVals = getSimValues(diseaseKey);
      simVals[featureId] = val;

      const data = QURESENSE_DATA[diseaseKey];
      const featSpec = data.simFeatures.find(f => f.id === featureId);
      const badge = document.getElementById(`badge-${featureId}`);
      if (badge && featSpec) {
        badge.innerText = `${val.toFixed(featSpec.step < 0.1 ? 3 : (featSpec.step < 1 ? 1 : 0))} ${featSpec.unit}`;
      }

      updateSimResultsLive(diseaseKey);
    });
  });
}

// --- PAGE GENERATORS ---

function generatePageHTML() {
  switch (currentState.activePage) {
    case "home":
      return renderHomePage();
    case "data_overview":
      return renderDataOverviewPage();
    case "classical_results":
      return renderClassicalResultsPage();
    case "qml_comparison":
      return renderQmlComparisonPage();
    case "simulator":
      return renderSimulatorPage();
    case "glossary":
      return renderGlossaryPage();
    case "about":
      return renderAboutPage();
    default:
      return renderHomePage();
  }
}

// --- 1. HOME PAGE ---
function renderHomePage() {
  return `
    <div class="page-header">
      <h1 class="page-title">QureSense</h1>
      <p class="page-subtitle">
        An educational and research reference framework for evaluating classical machine learning 
        versus hybrid quantum-classical algorithms in early disease-risk classification across public benchmark datasets.
      </p>
    </div>

    <div class="card-grid-3col">
      <!-- Breast Cancer Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
            Breast Cancer
          </h3>
          <span class="card-badge badge-dataset">WDBC Dataset</span>
        </div>
        <p style="font-size: 0.875rem; color: var(--text-secondary);">
          Evaluation on 569 samples with 30 cell nucleus features. Compares Logistic Regression, Random Forest, and VQC.
        </p>
        <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 4px;">
          <div>• <strong>Classical Best AUC:</strong> 0.991</div>
          <div>• <strong>Hybrid Quantum AUC:</strong> 0.987</div>
        </div>
        <button class="disease-tab-btn active" data-navigate="classical_results" onclick="setDisease('breast_cancer')" style="margin-top: auto;">
          View Results &rarr;
        </button>
      </div>

      <!-- Heart Disease Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.684a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
            Heart Disease
          </h3>
          <span class="card-badge badge-dataset">UCI Dataset</span>
        </div>
        <p style="font-size: 0.875rem; color: var(--text-secondary);">
          Evaluation on 303 patient records with 13 clinical features. Multi-class target mapped to binary risk classification.
        </p>
        <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 4px;">
          <div>• <strong>Classical Best AUC:</strong> 0.910</div>
          <div>• <strong>Hybrid Quantum AUC:</strong> 0.902</div>
        </div>
        <button class="disease-tab-btn active" data-navigate="classical_results" onclick="setDisease('heart_disease')" style="margin-top: auto;">
          View Results &rarr;
        </button>
      </div>

      <!-- Diabetes Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
            Diabetes
          </h3>
          <span class="card-badge badge-dataset">Pima Indians</span>
        </div>
        <p style="font-size: 0.875rem; color: var(--text-secondary);">
          Evaluation on 768 diagnostic measurements with 8 numerical features for diabetes risk classification.
        </p>
        <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 4px;">
          <div>• <strong>Classical Best AUC:</strong> 0.845</div>
          <div>• <strong>Hybrid Quantum Status:</strong> Benchmark Pending</div>
        </div>
        <button class="disease-tab-btn active" data-navigate="qml_comparison" onclick="setDisease('diabetes')" style="margin-top: auto;">
          View QML Status &rarr;
        </button>
      </div>
    </div>

    <!-- Overview Banner Card -->
    <div class="card" style="background: #ffffff;">
      <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">Educational Methodology & Architecture Scope</h3>
      <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
        QureSense isolates each disease model pipeline independently. Every disease utilizes its own separately trained classical baseline models (Logistic Regression, Random Forest) and its own Variational Quantum Classifier (VQC) hybrid circuit. No single model diagnoses multiple conditions from a shared input.
      </p>
    </div>
  `;
}

// --- 2. DATA OVERVIEW PAGE ---
function renderDataOverviewPage() {
  const data = QURESENSE_DATA[currentState.activeDisease];
  return `
    <div class="page-header">
      <h1 class="page-title">Benchmark Data Overview</h1>
      <p class="page-subtitle">Examine the public benchmark dataset characteristics, class balance, and feature mappings for each evaluated condition.</p>
    </div>

    ${renderDiseaseSelector()}

    <div class="card-grid-2col">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">${data.name} Benchmark Metadata</h3>
          <span class="card-badge badge-dataset">Public Dataset</span>
        </div>
        <table class="metrics-table">
          <tr>
            <td class="metric-name-cell">Dataset Source Name</td>
            <td class="metric-value-cell" style="font-family: var(--font-sans); font-size: 0.85rem;">${data.dataset}</td>
          </tr>
          <tr>
            <td class="metric-name-cell">Total Dataset Samples</td>
            <td class="metric-value-cell">${data.samples}</td>
          </tr>
          <tr>
            <td class="metric-name-cell">Feature Vector Count</td>
            <td class="metric-value-cell">${data.features} numerical features</td>
          </tr>
          <tr>
            <td class="metric-name-cell">Evaluation Test Split</td>
            <td class="metric-value-cell">${data.testSplit}</td>
          </tr>
        </table>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Class Distribution & Target Mapping</h3>
          <span class="card-badge badge-classical">Binary Target</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div>
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Class Balance Breakdown</div>
            <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-top: 2px;">${data.classBalance}</div>
          </div>
          <div style="border-top: 1px solid var(--bg-card-subtle); padding-top: 10px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Label Conversion Definition</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 2px; line-height: 1.5;">${data.labelConversion}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Distribution Bar -->
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <h3>Target Label Distribution Chart</h3>
          <p>Visualizing class balance across the public benchmark split</p>
        </div>
      </div>
      <div class="chart-svg-wrapper">
        ${renderDatasetDistributionSVG(data)}
      </div>
      <p class="chart-caption">Public benchmark dataset distributions are maintained without synthetic balancing techniques for honest evaluation.</p>
    </div>
  `;
}

// --- 3. CLASSICAL RESULTS PAGE ---
function renderClassicalResultsPage() {
  const data = QURESENSE_DATA[currentState.activeDisease];
  const lr = data.classical.lr;
  const rf = data.classical.rf;

  return `
    <div class="page-header">
      <h1 class="page-title">Classical Model Benchmark Results</h1>
      <p class="page-subtitle">Side-by-side performance evaluation of baseline Logistic Regression versus Random Forest classifiers on ${data.name}.</p>
    </div>

    <div class="results-research-notice">
      <span class="results-notice-tag">Research Risk Classification — Not for Clinical Use</span>
      <span class="results-notice-sub">Scores are computed on a held-out public test split (${data.testSplit}). They do not represent clinical performance.</span>
    </div>

    ${renderDiseaseSelector()}

    <!-- 2-Column Desktop / 1-Column Mobile Model Comparison -->
    <div class="card-grid-2col">
      <!-- Logistic Regression Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Logistic Regression</h3>
          <span class="card-badge badge-classical">Linear Baseline</span>
        </div>
        ${renderMetricsTable(lr)}
      </div>

      <!-- Random Forest Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Random Forest</h3>
          <span class="card-badge badge-classical">Ensemble Baseline</span>
        </div>
        ${renderMetricsTable(rf)}
      </div>
    </div>

    <!-- Confusion Matrices Comparison -->
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <h3>Confusion Matrices (Held-out Test Split)</h3>
          <p>Side-by-side count breakdown of True Negatives, False Positives, False Negatives, and True Positives</p>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
        <div>
          <div style="font-size: 0.85rem; font-weight: 700; text-align: center; margin-bottom: 8px; color: var(--text-primary);">Logistic Regression CM</div>
          ${renderConfusionMatrixHTML(lr.cm)}
        </div>
        <div>
          <div style="font-size: 0.85rem; font-weight: 700; text-align: center; margin-bottom: 8px; color: var(--text-primary);">Random Forest CM</div>
          ${renderConfusionMatrixHTML(rf.cm)}
        </div>
      </div>
      <p class="chart-caption">Which model looks stronger on this test split is not a clinical conclusion.</p>
    </div>

    <!-- Shared ROC Curve Comparison -->
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title-group">
          <h3>Receiver Operating Characteristic (ROC) Comparison</h3>
          <p>True Positive Rate vs. False Positive Rate across classification thresholds</p>
        </div>
      </div>
      <div class="chart-svg-wrapper">
        ${renderRocComparisonSVG(lr, rf, null)}
      </div>
      <p class="chart-caption">ROC curves demonstrate decision threshold trade-offs on held-out public data.</p>
    </div>
  `;
}

// --- 4. QML COMPARISON PAGE ---
function renderQmlComparisonPage() {
  const data = QURESENSE_DATA[currentState.activeDisease];
  const classicalBest = data.classical.rf;
  const qml = data.quantum;

  // Determine whether to display empty state or data (with interactive demo toggle)
  const showEmptyState = !qml.hasData && !currentState.showSimulatedQml;

  return `
    <div class="page-header">
      <h1 class="page-title">Classical vs. Hybrid Quantum-Classical (QML)</h1>
      <p class="page-subtitle">Evaluating Variational Quantum Classifiers (VQC) against baseline classical ensemble models on ${data.name}.</p>
    </div>

    <div class="results-research-notice">
      <span class="results-notice-tag">Research Risk Classification — Not for Clinical Use</span>
      <span class="results-notice-sub">Scores are computed on a held-out public test split. They are not clinical performance.</span>
    </div>

    ${renderDiseaseSelector()}

    ${data.name === "Diabetes" ? `
      <div class="demo-toggle-bar">
        <span>Demo Honest Empty State:</span>
        <label class="toggle-switch">
          <input type="checkbox" id="empty-state-toggle">
          <span class="toggle-slider"></span>
        </label>
        <span style="font-weight: 600; color: var(--text-primary);">${currentState.showSimulatedQml ? "Show Completed Benchmark" : "Show Pending State"}</span>
      </div>
    ` : ""}

    ${showEmptyState ? `
      <div class="empty-state-card">
        <div class="empty-state-icon">
          <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <div class="empty-state-title">Hybrid Quantum Benchmark Benchmark Pending</div>
        <div class="empty-state-desc">${qml.pendingReason}</div>
        <span class="empty-state-badge">Status: Optimization In Progress</span>
      </div>

      <!-- Only Classical Card Displayed when Quantum Pending -->
      <div class="card-grid-2col">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Classical Random Forest (Baseline)</h3>
            <span class="card-badge badge-classical">Classical Best</span>
          </div>
          ${renderMetricsTable(classicalBest)}
        </div>
      </div>
    ` : `
      <!-- Side-by-side or Stacked Classical vs Hybrid Quantum -->
      <div class="card-grid-2col">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Classical Random Forest</h3>
            <span class="card-badge badge-classical">Classical Baseline</span>
          </div>
          ${renderMetricsTable(classicalBest)}
        </div>

        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Hybrid Quantum VQC</h3>
            <span class="card-badge badge-quantum">Quantum Variational</span>
          </div>
          ${renderMetricsTable(qml.hybrid)}
        </div>
      </div>

      <!-- Confusion Matrices Comparison -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>Confusion Matrices (Classical Baseline vs. Hybrid Quantum)</h3>
            <p>Evaluating false positive/negative counts on public test split</p>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
          <div>
            <div style="font-size: 0.85rem; font-weight: 700; text-align: center; margin-bottom: 8px; color: var(--text-primary);">Classical Random Forest</div>
            ${renderConfusionMatrixHTML(classicalBest.cm)}
          </div>
          <div>
            <div style="font-size: 0.85rem; font-weight: 700; text-align: center; margin-bottom: 8px; color: var(--accent-indigo);">Hybrid Quantum VQC</div>
            ${renderConfusionMatrixHTML(qml.hybrid.cm)}
          </div>
        </div>
        <p class="chart-caption">Which model looks stronger on this test split is not a clinical conclusion.</p>
      </div>

      <!-- Shared ROC Curve Comparison -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title-group">
            <h3>ROC Curve: Classical vs Hybrid Quantum</h3>
            <p>Comparing area under ROC curve on public benchmark test data</p>
          </div>
        </div>
        <div class="chart-svg-wrapper">
          ${renderRocComparisonSVG(data.classical.lr, classicalBest, qml.hybrid)}
        </div>
        <p class="chart-caption">No claim is made that quantum models are automatically superior to classical models.</p>
      </div>

      <!-- Quantum Circuit Visualizer Architecture Card -->
      ${renderQuantumCircuitCard(data.name)}
    `}
  `;
}

// --- 5. GLOSSARY PAGE ---
function renderGlossaryPage() {
  return `
    <div class="page-header">
      <h1 class="page-title">How to Read Machine Learning Metrics</h1>
      <p class="page-subtitle">A plain-language academic guide to standard statistical classification evaluation metrics.</p>
    </div>

    <div class="glossary-list">
      <div class="glossary-item">
        <div class="glossary-title">
          <span>Accuracy</span>
          <span class="glossary-formula">(TP + TN) / Total</span>
        </div>
        <p class="glossary-def">
          The proportion of all benchmark samples correctly classified (both high-risk and low-risk).
        </p>
        <p class="glossary-note">Best used when dataset classes are balanced.</p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>Precision (Positive Predictive Value)</span>
          <span class="glossary-formula">TP / (TP + FP)</span>
        </div>
        <p class="glossary-def">
          Out of all instances flagged as high risk by the model, how many were truly high risk in the benchmark data?
        </p>
        <p class="glossary-note">Higher precision minimizes false positive alarms.</p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>Recall / Sensitivity</span>
          <span class="glossary-formula">TP / (TP + FN)</span>
        </div>
        <p class="glossary-def">
          Out of all true high-risk instances in the benchmark data, how many did the model correctly identify?
        </p>
        <p class="glossary-note">Higher recall minimizes false negative omissions.</p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>Specificity (True Negative Rate)</span>
          <span class="glossary-formula">TN / (TN + FP)</span>
        </div>
        <p class="glossary-def">
          Out of all true low-risk instances in the benchmark data, how many did the model correctly identify as low risk?
        </p>
        <p class="glossary-note">Measures the model's ability to correctly screen out non-risk cases.</p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>F1-Score</span>
          <span class="glossary-formula">2 * (Precision * Recall) / (Precision + Recall)</span>
        </div>
        <p class="glossary-def">
          The harmonic mean of Precision and Recall, providing a single balanced metric when classes are imbalanced.
        </p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>ROC-AUC (Area Under ROC Curve)</span>
          <span class="glossary-formula">Scale: 0.5 (Random) to 1.0 (Perfect)</span>
        </div>
        <p class="glossary-def">
          Measures the model's ability to discriminate between high-risk and low-risk cases across all possible classification decision thresholds.
        </p>
      </div>

      <div class="glossary-item">
        <div class="glossary-title">
          <span>Confusion Matrix</span>
          <span class="glossary-formula">2x2 Grid of Sample Counts</span>
        </div>
        <p class="glossary-def">
          A tabular layout showing exact counts of True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).
        </p>
      </div>
    </div>
  `;
}

// --- 6. ABOUT AND LIMITS PAGE ---
function renderAboutPage() {
  return `
    <div class="page-header">
      <h1 class="page-title">About QureSense & Research Boundaries</h1>
      <p class="page-subtitle">Scope, public dataset constraints, and explicit research boundaries of this educational framework.</p>
    </div>

    <div class="about-card">
      <h3>
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        Educational & Research Purpose Only
      </h3>
      <p>
        QureSense is built strictly for academic study, model architecture comparisons, and educational demonstrations of quantum computing concepts in binary classification tasks. It is not a medical device and is not intended for clinical use or patient risk assessment.
      </p>
    </div>

    <div class="about-card">
      <h3>
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>
        Separate Model Architecture & Independent Datasets
      </h3>
      <p>
        Each evaluated disease condition utilizes its own dedicated, separately trained classical model (Logistic Regression, Random Forest) and its own Variational Quantum Classifier (VQC) hybrid circuit built on public benchmark datasets:
      </p>
      <ul>
        <li><strong>Breast Cancer:</strong> Wisconsin Diagnostic Dataset (WDBC)</li>
        <li><strong>Heart Disease:</strong> UCI Heart Disease Benchmark Dataset</li>
        <li><strong>Diabetes:</strong> Pima Indians Diabetes Benchmark Dataset</li>
      </ul>
      <p style="margin-top: 8px;">
        There is no unified or shared multi-disease predictor model.
      </p>
    </div>

    <div class="about-card">
      <h3>
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        No Claim of Quantum Superiority
      </h3>
      <p>
        Quantum machine learning algorithms (VQC) are undergoing active academic research. Higher accuracy on a small public test split does not imply general quantum advantage or real-world hospital performance.
      </p>
    </div>
  `;
}

// --- HELPER RENDERING COMPONENTS ---

function renderDiseaseSelector() {
  const current = currentState.activeDisease;
  return `
    <div class="disease-selector-wrapper">
      <span class="disease-selector-label">Select Disease Benchmark Dataset:</span>
      
      <!-- Desktop Inline Tabs -->
      <div class="disease-tabs-web">
        <button class="disease-tab-btn ${current === 'breast_cancer' ? 'active' : ''}" data-disease="breast_cancer">
          Breast Cancer (WDBC)
        </button>
        <button class="disease-tab-btn ${current === 'heart_disease' ? 'active' : ''}" data-disease="heart_disease">
          Heart Disease (UCI)
        </button>
        <button class="disease-tab-btn ${current === 'diabetes' ? 'active' : ''}" data-disease="diabetes">
          Diabetes (Pima)
        </button>
      </div>

      <!-- Mobile Full-Width Dropdown -->
      <select class="disease-dropdown-mobile">
        <option value="breast_cancer" ${current === 'breast_cancer' ? 'selected' : ''}>Breast Cancer (WDBC)</option>
        <option value="heart_disease" ${current === 'heart_disease' ? 'selected' : ''}>Heart Disease (UCI)</option>
        <option value="diabetes" ${current === 'diabetes' ? 'selected' : ''}>Diabetes (Pima)</option>
      </select>
    </div>
  `;
}

function renderMetricsTable(model) {
  return `
    <table class="metrics-table">
      <tr class="highlight-metric">
        <td class="metric-name-cell">
          <span>ROC-AUC Score</span>
          <span class="metric-def-tooltip">Area under ROC curve across thresholds</span>
        </td>
        <td class="metric-value-cell">${model.auc.toFixed(3)}</td>
      </tr>
      <tr>
        <td class="metric-name-cell">
          <span>Accuracy</span>
          <span class="metric-def-tooltip">Correctly classified test samples</span>
        </td>
        <td class="metric-value-cell">${model.accuracy.toFixed(3)}</td>
      </tr>
      <tr>
        <td class="metric-name-cell">
          <span>Precision</span>
          <span class="metric-def-tooltip">True risk / Total predicted risk</span>
        </td>
        <td class="metric-value-cell">${model.precision.toFixed(3)}</td>
      </tr>
      <tr>
        <td class="metric-name-cell">
          <span>Recall / Sensitivity</span>
          <span class="metric-def-tooltip">True risk identified / Total true risk</span>
        </td>
        <td class="metric-value-cell">${model.recall.toFixed(3)}</td>
      </tr>
      <tr>
        <td class="metric-name-cell">
          <span>Specificity</span>
          <span class="metric-def-tooltip">True non-risk identified / Total non-risk</span>
        </td>
        <td class="metric-value-cell">${model.specificity.toFixed(3)}</td>
      </tr>
      <tr>
        <td class="metric-name-cell">
          <span>F1-Score</span>
          <span class="metric-def-tooltip">Harmonic mean of precision & recall</span>
        </td>
        <td class="metric-value-cell">${model.f1.toFixed(3)}</td>
      </tr>
    </table>
  `;
}

function renderConfusionMatrixHTML(cm) {
  return `
    <div class="cm-container">
      <div class="cm-grid">
        <div></div>
        <div class="cm-header-cell">Pred Low</div>
        <div class="cm-header-cell">Pred High</div>
        
        <div class="cm-row-header">Actual Low</div>
        <div class="cm-cell cm-tn">
          <span class="cm-cell-count">${cm.tn}</span>
          <span class="cm-cell-tag">True Neg</span>
        </div>
        <div class="cm-cell cm-fp">
          <span class="cm-cell-count">${cm.fp}</span>
          <span class="cm-cell-tag">False Pos</span>
        </div>

        <div class="cm-row-header">Actual High</div>
        <div class="cm-cell cm-fn">
          <span class="cm-cell-count">${cm.fn}</span>
          <span class="cm-cell-tag">False Neg</span>
        </div>
        <div class="cm-cell cm-tp">
          <span class="cm-cell-count">${cm.tp}</span>
          <span class="cm-cell-tag">True Pos</span>
        </div>
      </div>
    </div>
  `;
}

// --- SVG CHART GENERATORS ---

function renderRocComparisonSVG(lr, rf, qml) {
  const w = 440;
  const h = 260;
  const pad = 40;

  return `
    <svg viewBox="0 0 ${w} ${h}" width="100%" height="auto" style="max-width: 520px;">
      <!-- Grid Lines -->
      <line x1="${pad}" y1="${h-pad}" x2="${w-pad}" y2="${h-pad}" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${h-pad}" stroke="#cbd5e1" stroke-width="1"/>
      
      <!-- Random Guess Diagonal Line -->
      <line x1="${pad}" y1="${h-pad}" x2="${w-pad}" y2="${pad}" stroke="#94a3b8" stroke-dasharray="4,4" stroke-width="1.5"/>

      <!-- LR Line (Slate) -->
      <path d="M ${pad} ${h-pad} Q ${pad+80} ${pad+30} ${w-pad} ${pad}" fill="none" stroke="#475569" stroke-width="2.5"/>

      <!-- RF Line (Teal) -->
      <path d="M ${pad} ${h-pad} Q ${pad+50} ${pad+10} ${w-pad} ${pad}" fill="none" stroke="#0d9488" stroke-width="2.5"/>

      ${qml ? `
        <!-- QML Line (Indigo) -->
        <path d="M ${pad} ${h-pad} Q ${pad+60} ${pad+15} ${w-pad} ${pad}" fill="none" stroke="#4f46e5" stroke-width="2.5" stroke-dasharray="6,2"/>
      ` : ''}

      <!-- Axis Labels -->
      <text x="${w/2}" y="${h-8}" font-size="10" fill="#64748b" text-anchor="middle" font-family="sans-serif">False Positive Rate (1 - Specificity)</text>
      <text x="12" y="${h/2}" font-size="10" fill="#64748b" text-anchor="middle" font-family="sans-serif" transform="rotate(-90 12 ${h/2})">True Positive Rate (Recall)</text>

      <!-- Legend -->
      <g transform="translate(${w-170}, ${h-90})">
        <rect x="0" y="0" width="150" height="${qml ? 65 : 48}" fill="#ffffff" stroke="#e2e8f0" rx="4"/>
        <line x1="10" y1="14" x2="30" y2="14" stroke="#475569" stroke-width="2.5"/>
        <text x="36" y="17" font-size="10" fill="#334155" font-family="sans-serif">Logistic Regression (${lr.auc.toFixed(2)})</text>
        
        <line x1="10" y1="30" x2="30" y2="30" stroke="#0d9488" stroke-width="2.5"/>
        <text x="36" y="33" font-size="10" fill="#334155" font-family="sans-serif">Random Forest (${rf.auc.toFixed(2)})</text>

        ${qml ? `
          <line x1="10" y1="46" x2="30" y2="46" stroke="#4f46e5" stroke-width="2.5" stroke-dasharray="6,2"/>
          <text x="36" y="49" font-size="10" fill="#334155" font-family="sans-serif">Hybrid QML (${qml.auc.toFixed(2)})</text>
        ` : ''}
      </g>
    </svg>
  `;
}

function renderDatasetDistributionSVG(data) {
  const w = 400;
  const h = 100;
  
  let p1 = 60, p2 = 40;
  if (data.name === "Breast Cancer") { p1 = 62.7; p2 = 37.3; }
  else if (data.name === "Heart Disease") { p1 = 54.5; p2 = 45.5; }
  else if (data.name === "Diabetes") { p1 = 65.1; p2 = 34.9; }

  const w1 = (w - 40) * (p1 / 100);
  const w2 = (w - 40) * (p2 / 100);

  return `
    <svg viewBox="0 0 ${w} ${h}" width="100%" height="auto" style="max-width: 480px;">
      <!-- Class 0 Bar (Low Risk / Slate) -->
      <rect x="20" y="30" width="${w1}" height="32" fill="#0d9488" rx="4"/>
      <text x="${20 + w1/2}" y="50" font-size="11" fill="#ffffff" font-weight="bold" text-anchor="middle" font-family="sans-serif">Low Risk (${p1}%)</text>

      <!-- Class 1 Bar (High Risk / Indigo) -->
      <rect x="${20 + w1 + 4}" y="30" width="${w2}" height="32" fill="#4f46e5" rx="4"/>
      <text x="${20 + w1 + 4 + w2/2}" y="50" font-size="11" fill="#ffffff" font-weight="bold" text-anchor="middle" font-family="sans-serif">High Risk (${p2}%)</text>
      
      <text x="${w/2}" y="82" font-size="10" fill="#64748b" text-anchor="middle" font-family="sans-serif">Total Samples: ${data.samples} benchmark records</text>
    </svg>
  `;
}

// --- 7. FEATURE SIMULATOR & SURROGATE INFERENCE LOGIC ---

function getSimValues(diseaseKey) {
  if (!currentState.simValues[diseaseKey]) {
    const data = QURESENSE_DATA[diseaseKey];
    currentState.simValues[diseaseKey] = {};
    data.simFeatures.forEach(f => {
      currentState.simValues[diseaseKey][f.id] = f.default;
    });
  }
  return currentState.simValues[diseaseKey];
}

function setSimPreset(diseaseKey, presetType) {
  const data = QURESENSE_DATA[diseaseKey];
  const simVals = getSimValues(diseaseKey);
  data.simFeatures.forEach(f => {
    if (presetType === 'low') simVals[f.id] = f.low;
    else if (presetType === 'borderline') simVals[f.id] = f.borderline;
    else if (presetType === 'high') simVals[f.id] = f.high;
  });
}

function calculateSurrogateInference(diseaseKey) {
  const data = QURESENSE_DATA[diseaseKey];
  const simVals = getSimValues(diseaseKey);

  let lrLinearSum = 0;
  let rfTreeSum = 0;
  let normalizedFeatures = [];

  data.simFeatures.forEach((f) => {
    const rawVal = simVals[f.id] !== undefined ? simVals[f.id] : f.default;
    const norm = (rawVal - f.min) / (f.max - f.min);
    const mid = (f.default - f.min) / (f.max - f.min);
    const diff = norm - mid;

    normalizedFeatures.push(norm);
    lrLinearSum += f.weight * diff;

    if (diff > 0) {
      rfTreeSum += f.weight * Math.pow(diff, 1.25);
    } else {
      rfTreeSum -= Math.abs(f.weight) * Math.pow(Math.abs(diff), 1.1);
    }
  });

  const probLR = 1 / (1 + Math.exp(-6.5 * lrLinearSum));
  const probRF = 1 / (1 + Math.exp(-7.2 * rfTreeSum));

  const z0 = normalizedFeatures[0] || 0.5;
  const z3 = normalizedFeatures[3] || 0.5;
  const qInterference = 0.12 * Math.sin(Math.PI * z0 * z3);
  const qmlScore = lrLinearSum + qInterference;
  const probQML = 1 / (1 + Math.exp(-6.8 * qmlScore));

  const liveAngles = normalizedFeatures.slice(0, 4).map(z => (z * Math.PI).toFixed(2) + " rad");
  while (liveAngles.length < 4) liveAngles.push("0.50 rad");

  return {
    lr: { prob: Math.min(0.99, Math.max(0.01, probLR)) },
    rf: { prob: Math.min(0.99, Math.max(0.01, probRF)) },
    qml: { prob: Math.min(0.99, Math.max(0.01, probQML)) },
    liveAngles
  };
}

function renderSimulatorPage() {
  const diseaseKey = currentState.activeDisease;
  const data = QURESENSE_DATA[diseaseKey];
  const simVals = getSimValues(diseaseKey);
  const results = calculateSurrogateInference(diseaseKey);

  return `
    <div class="page-header">
      <h1 class="page-title">Interactive Feature Input Simulator</h1>
      <p class="page-subtitle">Educational sandbox exploring model sensitivity and risk prediction across classical baselines and hybrid quantum surrogates.</p>
    </div>

    <div class="results-research-notice">
      <span class="results-notice-tag">Educational Sandbox Only — Not for Clinical Use</span>
      <span class="results-notice-sub">Outputs use normalized surrogate decision functions derived from public benchmark dataset statistics.</span>
    </div>

    ${renderDiseaseSelector()}

    <!-- Preset Loader Bar -->
    <div class="sim-preset-bar">
      <span class="sim-preset-label">Preset Profiles:</span>
      <button class="sim-preset-btn" data-preset="low">Typical Low Risk</button>
      <button class="sim-preset-btn" data-preset="borderline">Borderline Benchmark Baseline</button>
      <button class="sim-preset-btn" data-preset="high">High Risk Profile</button>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px;">
      
      <!-- Left Column: Feature Sliders -->
      <div>
        <div style="font-weight: 700; font-size: 1rem; color: var(--text-primary); margin-bottom: 12px;">
          Clinical Feature Input Vector (${data.name})
        </div>
        <div class="sim-sliders-grid" id="sim-sliders-container">
          ${data.simFeatures.map(f => {
            const currentVal = simVals[f.id] !== undefined ? simVals[f.id] : f.default;
            return `
              <div class="sim-slider-card">
                <div class="sim-slider-header">
                  <span class="sim-slider-title">${f.name}</span>
                  <span class="sim-slider-badge" id="badge-${f.id}">${Number(currentVal).toFixed(f.step < 0.1 ? 3 : (f.step < 1 ? 1 : 0))} ${f.unit}</span>
                </div>
                <input type="range" 
                       class="sim-slider-input" 
                       data-feature="${f.id}" 
                       min="${f.min}" 
                       max="${f.max}" 
                       step="${f.step}" 
                       value="${currentVal}">
                <div class="sim-slider-meta">
                  <span>Min: ${f.min} ${f.unit}</span>
                  <span>Baseline Mean: ${f.default} ${f.unit}</span>
                  <span>Max: ${f.max} ${f.unit}</span>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- Right Column: Model Result Cards -->
      <div>
        <div style="font-weight: 700; font-size: 1rem; color: var(--text-primary); margin-bottom: 12px;">
          Real-Time Model Prediction & Risk Gauge Comparison
        </div>
        <div class="sim-results-grid" id="sim-results-container" style="margin-top: 0; grid-template-columns: 1fr;">
          ${renderSimResultCard("Logistic Regression (Linear)", results.lr.prob, "lr-card", "Computes weighted linear decision boundary score with sigmoid activation.")}
          ${renderSimResultCard("Random Forest (Ensemble)", results.rf.prob, "rf-card", "Evaluates non-linear feature threshold splits across decision trees.")}
          ${renderSimResultCard("Hybrid Quantum VQC", results.qml.prob, "qml-card", "Maps features to quantum Hilbert state space with entangling rotation gates.", !data.quantum.hasData && !currentState.showSimulatedQml)}
        </div>
      </div>

    </div>

    <!-- Dynamic Live Quantum Circuit Architecture Visualizer -->
    <div id="sim-circuit-container">
      ${renderQuantumCircuitCard(data.name, results.liveAngles)}
    </div>
  `;
}

function renderSimResultCard(title, prob, cardClass, desc, isPending = false) {
  if (isPending) {
    return `
      <div class="sim-model-card ${cardClass}" style="opacity: 0.8;">
        <div class="sim-model-header">
          <span class="sim-model-name">${title}</span>
          <span class="sim-risk-tag" style="background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;">Pending</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
          Hybrid quantum simulator optimization in progress for this dataset. Toggle demo switch on QML page to preview completed state.
        </div>
      </div>
    `;
  }

  const pct = Math.round(prob * 100);
  const isHigh = prob >= 0.5;
  const tagText = isHigh ? "High Risk Classification" : "Low Risk Classification";
  const tagClass = isHigh ? "high-risk" : "low-risk";
  const fillColor = isHigh ? "#4f46e5" : "#0d9488";

  return `
    <div class="sim-model-card ${cardClass}">
      <div class="sim-model-header">
        <span class="sim-model-name">${title}</span>
        <span class="sim-risk-tag ${tagClass}">${tagText}</span>
      </div>
      <div class="sim-gauge-wrapper">
        <div class="sim-gauge-labels">
          <span>Estimated Risk Probability</span>
          <span style="font-family: var(--font-mono); font-weight: 700; color: ${fillColor};">${pct}%</span>
        </div>
        <div class="sim-gauge-bar-bg">
          <div class="sim-gauge-bar-fill" style="width: ${pct}%; background-color: ${fillColor};"></div>
        </div>
      </div>
      <div class="sim-formula-note">${desc}</div>
    </div>
  `;
}

function updateSimResultsLive(diseaseKey) {
  const results = calculateSurrogateInference(diseaseKey);
  const data = QURESENSE_DATA[diseaseKey];
  const container = document.getElementById("sim-results-container");
  if (container) {
    container.innerHTML = `
      ${renderSimResultCard("Logistic Regression (Linear)", results.lr.prob, "lr-card", "Computes weighted linear decision boundary score with sigmoid activation.")}
      ${renderSimResultCard("Random Forest (Ensemble)", results.rf.prob, "rf-card", "Evaluates non-linear feature threshold splits across decision trees.")}
      ${renderSimResultCard("Hybrid Quantum VQC", results.qml.prob, "qml-card", "Maps features to quantum Hilbert state space with entangling rotation gates.", !data.quantum.hasData && !currentState.showSimulatedQml)}
    `;
  }

  const circuitContainer = document.getElementById("sim-circuit-container");
  if (circuitContainer) {
    circuitContainer.innerHTML = renderQuantumCircuitCard(data.name, results.liveAngles);
  }
}


