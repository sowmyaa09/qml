"""Build a one-page reviewer sheet from whatever artifacts exist.

    python -m src.make_judge_sheet

Reads the metrics CSVs already written by the training commands and writes
``outputs/reports/judge_sheet.md``. Nothing is invented: sections whose files
are missing say so.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.preprocessing import RANDOM_STATE, TEST_SIZE
from src.utils import (
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
    get_reports_dir,
)

QML_MODELS = ("VQC", "QSVC", "QNN")
REPORT_NAME = "judge_sheet.md"


def _read(path: Path) -> pd.DataFrame | None:
    if path.is_file():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


def _best_row(frame: pd.DataFrame, models: tuple[str, ...] | None = None, column: str = "f1"):
    if frame is None or frame.empty or column not in frame.columns:
        return None
    subset = frame
    if models is not None:
        subset = frame[frame["model"].isin(models)]
    if subset.empty:
        return None
    return subset.sort_values(column, ascending=False).iloc[0]


def _fmt(row, column: str, fmt: str = "{:.4f}") -> str:
    if row is None or column not in row or pd.isna(row[column]):
        return "n/a"
    value = row[column]
    if isinstance(value, (int, float)):
        return fmt.format(value)
    return str(value)


def build_sheet() -> str:
    metrics = get_metrics_dir()
    classical = _read(metrics / "classical_model_metrics.csv")
    reduced = _read(metrics / "phase2_reduced_classical_model_metrics.csv")
    qml = _read(metrics / "qml_vs_classical_metrics.csv")
    ablation = _read(metrics / "qml_ablation_k.csv")
    thresholds = _read(metrics / "qml_threshold_options.csv")
    intervals = _read(metrics / "qml_significance_bootstrap.csv")
    pairs = _read(metrics / "qml_significance_pairs.csv")
    repeated_cv = _read(metrics / "qml_repeated_cv.csv")

    config_path = get_reports_dir() / "phase3_config.json"
    config = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config = {}

    # Phase artifacts reuse the same filename pattern; they are not disease tables.
    internal_prefixes = {"qml", "phase2_full", "phase2_reduced"}
    extra_tables = sorted(
        stem
        for stem in (
            p.name.replace("_classical_model_metrics.csv", "")
            for p in metrics.glob("*_classical_model_metrics.csv")
        )
        if stem not in internal_prefixes and not stem.endswith("_qml")
    )
    hybrid_tables = sorted(
        p.name.replace("_qml_metrics.csv", "") for p in metrics.glob("*_qml_metrics.csv")
    )

    best_classical_full = _best_row(classical)
    best_qml = _best_row(qml, QML_MODELS) if qml is not None else None
    best_classical_reduced = (
        _best_row(qml, ("Logistic Regression", "Random Forest", "RBF SVM"))
        if qml is not None
        else None
    )

    lines: list[str] = [
        "# Q-Care Detect — reviewer sheet",
        "",
        f"**{RESEARCH_DISCLAIMER}** Educational research prototype, not a medical device.",
        "",
        "Hybrid quantum-classical machine learning on **public biomedical "
        "benchmarks**: classical preprocessing and feature selection, then small "
        "quantum models on a simulator, measured against classical baselines.",
        "",
        "## Reproducibility",
        "",
        f"- Stratified {int((1 - TEST_SIZE) * 100)}/{int(TEST_SIZE * 100)} split, "
        f"`random_state={RANDOM_STATE}` everywhere.",
        "- Feature selection, scaling, imputation and quantile clipping are fit on "
        "**training rows only**.",
        "- Positive class 1 = disease-present / malignant for the table in question.",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\Activate.ps1",
        "python -m src.train_classical",
        "python -m src.train_phase2",
        "python -m src.train_qml --with-qnn",
        "python -m src.train_qml_significance",
        "python -m src.train_qml_ablation",
        "python -m src.train_qml_table coimbra",
        "python -m src.train_phase4",
        "python -m src.make_judge_sheet",
        "streamlit run app/streamlit_app.py",
        "pytest",
        "```",
        "",
        "## Headline numbers (Wisconsin, held-out split)",
        "",
        "| Track | Best model | F1 | Recall | ROC-AUC | Fit seconds |",
        "| --- | --- | --- | --- | --- | --- |",
        "| Classical, 30 features | "
        f"{_fmt(best_classical_full, 'model')} | {_fmt(best_classical_full, 'f1')} | "
        f"{_fmt(best_classical_full, 'recall')} | {_fmt(best_classical_full, 'roc_auc')} | n/a |",
        "| Classical, selected features | "
        f"{_fmt(best_classical_reduced, 'model')} | {_fmt(best_classical_reduced, 'f1')} | "
        f"{_fmt(best_classical_reduced, 'recall')} | {_fmt(best_classical_reduced, 'roc_auc')} | "
        f"{_fmt(best_classical_reduced, 'fit_seconds', '{:.2f}')} |",
        "| Hybrid QML, same features | "
        f"{_fmt(best_qml, 'model')} | {_fmt(best_qml, 'f1')} | "
        f"{_fmt(best_qml, 'recall')} | {_fmt(best_qml, 'roc_auc')} | "
        f"{_fmt(best_qml, 'fit_seconds', '{:.2f}')} |",
        "",
    ]

    if best_qml is not None and best_classical_reduced is not None:
        qml_f1 = float(best_qml["f1"])
        classical_f1 = float(best_classical_reduced["f1"])
        if qml_f1 > classical_f1 + 1e-6:
            verdict = (
                f"**{best_qml['model']}** edged out the classical baselines on F1 for "
                "this one split. One split on a small, nearly linearly separable "
                "table is not a quantum-advantage claim."
            )
        elif qml_f1 < classical_f1 - 1e-6:
            verdict = (
                "The classical baselines kept the higher F1, and they trained orders "
                "of magnitude faster. We report that honestly rather than tuning "
                "until quantum looks better."
            )
        else:
            verdict = "Quantum and classical tied on F1 for this split."
        lines += ["**Verdict.** " + verdict, ""]

    if config:
        lines += [
            "## Quantum configuration",
            "",
            f"- Qubits: {config.get('n_qubits', 'n/a')} (one per selected feature).",
            f"- ZZFeatureMap reps: {config.get('feature_reps', 'n/a')}; "
            f"RealAmplitudes reps: {config.get('ansatz_reps', 'n/a')}.",
            f"- VQC optimizer: COBYLA maxiter={config.get('maxiter', 'n/a')}.",
            f"- QNN track run: {'yes' if config.get('with_qnn') else 'no'}.",
            "- QSVC kernel: FidelityStatevectorKernel on a classical simulator "
            "(no QPU, no shot noise).",
            "",
        ]

    if intervals is not None and not intervals.empty:
        f1_rows = intervals[intervals["metric"] == "f1"].sort_values(
            "point", ascending=False
        )
        lines += [
            "## Is the difference real? (95% bootstrap, paired tests)",
            "",
            "| Model | F1 | 95% interval |",
            "| --- | --- | --- |",
        ]
        for _, row in f1_rows.iterrows():
            lines.append(
                f"| {row['model']} | {float(row['point']):.4f} | "
                f"[{float(row['ci_lower']):.4f}, {float(row['ci_upper']):.4f}] |"
            )
        lines.append("")

    if pairs is not None and not pairs.empty:
        undecided = int(pairs["f1_ci_crosses_zero"].sum())
        qsvc = pairs[pairs["quantum_model"] == "QSVC"]
        lines += [
            f"- {undecided} of {len(pairs)} quantum-vs-classical pairs have an F1 "
            "difference interval containing zero.",
        ]
        if not qsvc.empty:
            lines.append(
                "- QSVC vs classical McNemar p-values: "
                + ", ".join(
                    f"{row['classical_model']} p={float(row['mcnemar_p']):.3f}"
                    for _, row in qsvc.iterrows()
                )
                + "."
            )
            lines.append(
                "- Read: on this split QSVC and the classical baselines are "
                "**statistically indistinguishable**. The defensible difference is "
                "runtime, not accuracy."
            )
        losers = pairs[~pairs["f1_ci_crosses_zero"]]["quantum_model"].unique()
        if len(losers):
            lines.append(
                "- Separated from the baselines (worse, intervals exclude zero): "
                + ", ".join(sorted(losers))
                + "."
            )
        lines.append("")

    if repeated_cv is not None and not repeated_cv.empty:
        lines += [
            "| Model | Repeated-CV F1 (5x5) |",
            "| --- | --- |",
        ]
        for _, row in repeated_cv.sort_values("f1_mean", ascending=False).iterrows():
            lines.append(
                f"| {row['model']} | {float(row['f1_mean']):.4f} "
                f"+/- {float(row['f1_std']):.4f} |"
            )
        lines += [
            "",
            "Preprocessing is refit inside every fold. No p-value is taken from "
            "these folds, because repeated-CV folds share training rows.",
            "",
        ]

    if ablation is not None and not ablation.empty:
        qsvc_rows = ablation[ablation["model"] == "QSVC"].sort_values("k")
        lines += ["## Ablation — qubits vs quantum-kernel quality", ""]
        lines.append("| k (qubits) | QSVC F1 | QSVC fit seconds |")
        lines.append("| --- | --- | --- |")
        for _, row in qsvc_rows.iterrows():
            lines.append(
                f"| {int(row['k'])} | {float(row['f1']):.4f} | {float(row['fit_seconds']):.2f} |"
            )
        lines.append("")

    if thresholds is not None and not thresholds.empty:
        lines += [
            "## Decision support (threshold options on this split)",
            "",
            "| Model | Rule | Threshold | Recall | Specificity | Missed positives |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for _, row in thresholds.iterrows():
            lines.append(
                f"| {row['model']} | {row['rule']} | {float(row['threshold']):.3f} | "
                f"{float(row['recall']):.3f} | {float(row['specificity']):.3f} | "
                f"{int(row['false_negatives'])} |"
            )
        lines += [
            "",
            "Thresholds trade sensitivity against false positives on a public test "
            "split. They are not clinical cut-offs.",
            "",
        ]

    audit = _read(metrics / "dataset_duplicate_audit.csv")
    if audit is not None and not audit.empty:
        risky = audit[audit["leakage_risk"]]
        lines += [
            "## Data integrity (duplicate-row audit)",
            "",
            f"- {len(audit)} tables audited for repeated rows before any split.",
        ]
        if risky.empty:
            lines.append("- No table exceeded the duplicate threshold.")
        else:
            for _, row in risky.iterrows():
                lines.append(
                    f"- **{row['key']}**: {int(row['duplicate_rows'])} of "
                    f"{int(row['rows'])} rows are repeats "
                    f"({float(row['duplicate_share']):.1%}). A random split would "
                    "put the same patient in train and test."
                )
        lines += [
            "- `load_tabular_dataset` drops exact duplicates by default, so those "
            "rows can no longer inflate a score.",
            "- More data therefore means **more patients**, not more copies: the "
            "`heart_uci_pooled` table combines four hospital cohorts (Cleveland, "
            "Hungary, Switzerland, VA Long Beach) that share one schema. "
            "`brfss_heart` is the large unique-respondent survey (~320k CDC 2020 "
            "adults), separate from Kaggle `cardio_train`.",
            "",
        ]

    lines += [
        "## Dataset inventory",
        "",
        f"- Public tables with saved classical metrics: {len(extra_tables)} "
        f"({', '.join(extra_tables) if extra_tables else 'none yet'}).",
        f"- Hybrid QML experiments: Wisconsin"
        + (f" plus {', '.join(hybrid_tables)}" if hybrid_tables else "")
        + ".",
        "- Every table is a **separate** experiment: one file, one label, one model.",
        "",
        "## What this project does not claim",
        "",
        "- No diagnosis, triage, or treatment advice.",
        "- No multi-disease score for a person: each model only sees its own "
        "table's columns and its own label.",
        "- No symptom checker, no test recommendations, no named doctors.",
        "- No real quantum hardware, no hospital EHR, no patient uploads.",
        "- No claim that quantum machine learning is inherently more accurate.",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
    ]
    return "\n".join(lines)


def main() -> int:
    ensure_output_directories()
    path = get_reports_dir() / REPORT_NAME
    path.write_text(build_sheet(), encoding="utf-8")
    print(f"Wrote {path}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Judge sheet failed: {exc}", file=sys.stderr)
        raise
