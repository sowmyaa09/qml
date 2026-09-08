"""Are the Phase 3 differences real? Bootstrap CIs, McNemar, DeLong, repeated CV.

    python -m src.train_qml_significance
    python -m src.train_qml_significance --resamples 4000
    python -m src.train_qml_significance --skip-cv

Reads the held-out scores that ``train_qml`` already saved, so the slow
circuit models are not refitted. Repeated cross-validation refits only the
fast models (logistic regression, random forest, RBF SVM, QSVC) inside a
leak-free pipeline.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.data_loader import load_breast_cancer_dataset
from src.decision_support import is_probability_like, test_scores_filename
from src.feature_selection import DEFAULT_K
from src.preprocessing import RANDOM_STATE
from src.qml_models import build_qsvc, build_rbf_svm_pipeline
from src.significance import (
    bootstrap_metric_ci,
    delong_roc_test,
    describe_p_value,
    labels_from_scores,
    mcnemar_test,
    paired_bootstrap_difference,
)
from src.train_classical import (
    LR_MODEL_NAME,
    RBF_SVM_NAME,
    RF_MODEL_NAME,
    build_logistic_regression_pipeline,
    build_random_forest,
)
from src.train_tune import QuantileClipper
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_figures_dir,
    get_metrics_dir,
    get_reports_dir,
)

QUANTUM_MODELS = ("QSVC", "VQC", "QNN")
CLASSICAL_MODELS = (LR_MODEL_NAME, RF_MODEL_NAME, RBF_SVM_NAME)
CI_METRICS = ("f1", "recall", "roc_auc")

WISCONSIN_PREFIX = "qml"


def _artifact_names(prefix: str) -> dict[str, str]:
    """Wisconsin keeps its original filenames; other experiments get their own."""
    return {
        "bootstrap_csv": f"{prefix}_significance_bootstrap.csv",
        "pairs_csv": f"{prefix}_significance_pairs.csv",
        "cv_csv": f"{prefix}_repeated_cv.csv",
        "figure": f"{prefix}_significance_intervals.png",
        "report": (
            "phase3_significance.md"
            if prefix == WISCONSIN_PREFIX
            else f"phase3_significance_{prefix}.md"
        ),
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confidence intervals and paired tests for Phase 3 results."
    )
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument(
        "--prefix",
        default=WISCONSIN_PREFIX,
        help=(
            "Artifact prefix of the experiment to test, e.g. 'qml' (Wisconsin) "
            "or 'heart_uci_pooled_qml'."
        ),
    )
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--cv-splits", type=int, default=5, dest="cv_splits")
    parser.add_argument("--cv-repeats", type=int, default=5, dest="cv_repeats")
    parser.add_argument(
        "--skip-cv",
        action="store_true",
        dest="skip_cv",
        help="Skip repeated cross-validation (QSVC refits are the slow part).",
    )
    return parser.parse_args(argv)


def _md_table(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in frame.iterrows():
        cells = []
        for col in cols:
            value = row[col]
            if isinstance(value, bool):
                cells.append("yes" if value else "no")
            elif isinstance(value, float):
                cells.append(f"{value:.4f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _load_held_out_scores(prefix: str) -> tuple[np.ndarray, dict[str, dict]]:
    path = get_metrics_dir() / test_scores_filename(prefix)
    if not path.is_file():
        raise FileNotFoundError(
            f"{path.name} is missing. Run `python -m src.train_qml --with-qnn` "
            "(or the matching train_qml_table command) first."
        )
    frame = pd.read_csv(path)
    truth: np.ndarray | None = None
    models: dict[str, dict] = {}
    for name, group in frame.groupby("model"):
        scores = group["score"].to_numpy(dtype=float)
        labels = group["y_true"].to_numpy(dtype=int)
        if truth is None:
            truth = labels
        elif not np.array_equal(truth, labels):
            raise ValueError(
                "Saved rows are not aligned across models; re-run train_qml."
            )
        probability_like = is_probability_like(scores)
        models[str(name)] = {
            "score": scores,
            "pred": labels_from_scores(scores, probability_like=probability_like),
            "probability_like": probability_like,
        }
    if truth is None:
        raise ValueError("No held-out scores found in the CSV.")
    return truth, models


def _plot_intervals(frame: pd.DataFrame, path) -> None:
    subset = frame[frame["metric"] == "f1"].sort_values("point")
    if subset.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    positions = np.arange(len(subset))
    lower = subset["point"] - subset["ci_lower"]
    upper = subset["ci_upper"] - subset["point"]
    ax.errorbar(
        subset["point"],
        positions,
        xerr=[lower, upper],
        fmt="o",
        capsize=4,
        color="tab:blue",
    )
    ax.set_yticks(positions)
    ax.set_yticklabels(subset["model"])
    ax.set_xlabel("F1 on the held-out split (95% bootstrap interval)")
    ax.set_xlim(0.0, 1.05)
    ax.set_title(
        f"Overlapping intervals mean the split cannot separate the models\n{RESEARCH_DISCLAIMER}"
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _mutual_info(x, y):
    """Module-level (picklable) scorer for SelectKBest inside a pipeline."""
    return mutual_info_classif(x, y, random_state=RANDOM_STATE)


def _cv_pipelines(k: int, n_features: int) -> dict[str, Pipeline]:
    """Leak-free pipelines: clip, select, scale, then fit, all inside each fold."""
    k = min(k, n_features)

    def selector() -> SelectKBest:
        return SelectKBest(_mutual_info, k=k)

    def head() -> list:
        # Impute before selecting: SelectKBest rejects NaN, and the fill values
        # must come from the fold's training rows only.
        return [
            ("clip", QuantileClipper()),
            ("impute", SimpleImputer(strategy="median")),
            ("select", selector()),
        ]

    return {
        LR_MODEL_NAME: Pipeline(
            [*head(), ("model", build_logistic_regression_pipeline())]
        ),
        RF_MODEL_NAME: Pipeline([*head(), ("model", build_random_forest())]),
        RBF_SVM_NAME: Pipeline([*head(), ("model", build_rbf_svm_pipeline())]),
        "QSVC": Pipeline(
            [*head(), ("scale", MinMaxScaler()), ("model", build_qsvc(n_qubits=k))]
        ),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    print(LONG_DISCLAIMER, flush=True)
    print(RESEARCH_DISCLAIMER)
    print("Significance of the Phase 3 gap - not a clinical claim.")
    print()
    ensure_output_directories()
    names = _artifact_names(args.prefix)
    if args.prefix != WISCONSIN_PREFIX and not args.skip_cv:
        # The CV block loads Wisconsin explicitly; other experiments would need
        # their own loader, so do not pretend to cross-validate them here.
        print(
            f"Cross-validation is Wisconsin-specific; skipping it for "
            f"prefix {args.prefix!r}.",
            flush=True,
        )
        args.skip_cv = True

    truth, models = _load_held_out_scores(args.prefix)
    print(f"Experiment prefix: {args.prefix}")
    print(f"Held-out rows: {len(truth)} ({int(truth.sum())} positive)")
    print(f"Models with saved scores: {', '.join(models)}")
    print(f"Bootstrap resamples: {args.resamples}", flush=True)
    print()

    rows = []
    for name, blob in models.items():
        print(f"  bootstrapping {name}...", flush=True)
        for metric in CI_METRICS:
            interval = bootstrap_metric_ci(
                truth,
                blob["pred"],
                blob["score"],
                metric=metric,
                n_resamples=args.resamples,
            )
            rows.append({"model": name, **interval})
    bootstrap_frame = pd.DataFrame(rows)
    bootstrap_frame.to_csv(get_metrics_dir() / names["bootstrap_csv"], index=False)

    print("95% bootstrap intervals for F1")
    for _, row in bootstrap_frame[bootstrap_frame["metric"] == "f1"].iterrows():
        print(
            f"  {row['model']:<20} {row['point']:.4f} "
            f"[{row['ci_lower']:.4f}, {row['ci_upper']:.4f}]"
        )
    print(flush=True)

    pair_rows = []
    for quantum in QUANTUM_MODELS:
        if quantum not in models:
            continue
        for classical in CLASSICAL_MODELS:
            if classical not in models:
                continue
            q, c = models[quantum], models[classical]
            difference = paired_bootstrap_difference(
                truth,
                (q["pred"], q["score"]),
                (c["pred"], c["score"]),
                metric="f1",
                n_resamples=args.resamples,
            )
            mcnemar = mcnemar_test(truth, q["pred"], c["pred"])
            delong = delong_roc_test(truth, q["score"], c["score"])
            pair_rows.append(
                {
                    "quantum_model": quantum,
                    "classical_model": classical,
                    "f1_difference": difference["difference"],
                    "f1_ci_lower": difference["ci_lower"],
                    "f1_ci_upper": difference["ci_upper"],
                    "f1_ci_crosses_zero": difference["crosses_zero"],
                    "mcnemar_discordant": mcnemar["discordant"],
                    "mcnemar_p": mcnemar["p_value"],
                    "mcnemar_method": mcnemar["method"],
                    "auc_difference": delong["auc_difference"],
                    "delong_p": delong["p_value"],
                }
            )
    pairs_frame = pd.DataFrame(pair_rows)
    pairs_frame.to_csv(get_metrics_dir() / names["pairs_csv"], index=False)

    print("Paired comparisons (quantum vs classical, same rows)")
    for _, row in pairs_frame.iterrows():
        print(
            f"  {row['quantum_model']} vs {row['classical_model']}: "
            f"dF1 {row['f1_difference']:+.4f} "
            f"[{row['f1_ci_lower']:+.4f}, {row['f1_ci_upper']:+.4f}], "
            f"McNemar p={row['mcnemar_p']:.3f}, DeLong p={row['delong_p']:.3f}"
        )
    print()

    _plot_intervals(bootstrap_frame, get_figures_dir() / names["figure"])

    cv_frame = pd.DataFrame()
    if not args.skip_cv:
        print(
            f"Repeated stratified CV ({args.cv_splits} splits x {args.cv_repeats} "
            "repeats, QSVC included; VQC/QNN excluded for runtime)...",
            flush=True,
        )
        data = load_breast_cancer_dataset()
        splitter = RepeatedStratifiedKFold(
            n_splits=args.cv_splits,
            n_repeats=args.cv_repeats,
            random_state=RANDOM_STATE,
        )
        cv_rows = []
        fold_scores: dict[str, np.ndarray] = {}
        for name, pipeline in _cv_pipelines(args.k, data.features.shape[1]).items():
            scores = cross_val_score(
                pipeline,
                data.features,
                data.target,
                cv=splitter,
                scoring="f1",
                n_jobs=1,
            )
            fold_scores[name] = scores
            cv_rows.append(
                {
                    "model": name,
                    "folds": int(scores.size),
                    "f1_mean": float(scores.mean()),
                    "f1_std": float(scores.std(ddof=1)),
                    "f1_min": float(scores.min()),
                    "f1_max": float(scores.max()),
                }
            )
            print(
                f"  {name:<20} F1 {scores.mean():.4f} +/- {scores.std(ddof=1):.4f}",
                flush=True,
            )
        cv_frame = pd.DataFrame(cv_rows)
        cv_frame.to_csv(get_metrics_dir() / names["cv_csv"], index=False)
        if "QSVC" in fold_scores and RBF_SVM_NAME in fold_scores:
            paired = fold_scores["QSVC"] - fold_scores[RBF_SVM_NAME]
            print(
                f"  QSVC - RBF SVM per fold: mean {paired.mean():+.4f} "
                f"+/- {paired.std(ddof=1):.4f}",
                flush=True,
            )
        print()

    best_classical = (
        bootstrap_frame[
            (bootstrap_frame["metric"] == "f1")
            & (bootstrap_frame["model"].isin(CLASSICAL_MODELS))
        ]
        .sort_values("point", ascending=False)
        .iloc[0]
    )
    verdict_lines = []
    if not pairs_frame.empty:
        qsvc_rows = pairs_frame[pairs_frame["quantum_model"] == "QSVC"]
        indistinguishable = qsvc_rows[qsvc_rows["mcnemar_p"] >= 0.05]
        if not qsvc_rows.empty:
            verdict_lines.append(
                f"QSVC is statistically indistinguishable from "
                f"{len(indistinguishable)} of {len(qsvc_rows)} classical baselines "
                "by McNemar at alpha = 0.05."
            )
            worst_p = float(qsvc_rows["mcnemar_p"].min())
            verdict_lines.append(describe_p_value(worst_p))
        separated = pairs_frame[~pairs_frame["f1_ci_crosses_zero"]]
        if separated.empty:
            verdict_lines.append(
                "Every paired F1 interval includes zero, so this split cannot "
                "separate any quantum model from any classical baseline on F1."
            )
        else:
            names = ", ".join(
                f"{row['quantum_model']} vs {row['classical_model']}"
                for _, row in separated.iterrows()
            )
            verdict_lines.append(
                f"These pairs had an F1 interval excluding zero: {names}."
            )

    report = get_reports_dir() / names["report"]
    body_parts = [
        "# Phase 3 significance — is the gap real?",
        "",
        RESEARCH_DISCLAIMER,
        "",
        f"One stratified test split of the public Wisconsin table: **{len(truth)} rows**, "
        f"{int(truth.sum())} positive. Small splits produce wide intervals, so a "
        "difference of a few thousandths of F1 means nothing on its own.",
        "",
        "## Method",
        "",
        "- **Stratified bootstrap** (resampling within each class) for every "
        f"model's metric, {args.resamples} resamples, percentile intervals.",
        "- **Paired bootstrap** of the difference: both models are scored on the "
        "same resampled rows, which cancels the row-to-row luck they shared.",
        "- **McNemar** on hard predictions: only the rows where exactly one model "
        "is correct carry information.",
        "- **DeLong** for two correlated ROC-AUCs on the same rows.",
        "- Predictions are recovered from saved scores at the same cutoff each "
        "estimator uses (0.5 for probabilities, 0.0 for decision scores), so no "
        "circuit model had to be refitted.",
        "",
        "## Confidence intervals (95%)",
        "",
        _md_table(bootstrap_frame),
        "",
        f"Figure: `{names['figure']}`. Overlapping intervals mean the split cannot "
        "tell those models apart.",
        "",
        "## Paired quantum vs classical tests",
        "",
        _md_table(pairs_frame) if not pairs_frame.empty else "_No pairs available._",
        "",
        "`f1_ci_crosses_zero = yes` means the F1 difference is not distinguishable "
        "from zero on this split.",
        "",
    ]

    if not cv_frame.empty:
        body_parts += [
            "## Repeated stratified cross-validation",
            "",
            f"{args.cv_splits} splits x {args.cv_repeats} repeats over all "
            f"{len(load_breast_cancer_dataset().features)} rows. Clipping, feature "
            "selection and scaling are refit **inside every fold**, so no fold sees "
            "its own preprocessing statistics.",
            "",
            _md_table(cv_frame),
            "",
            "VQC and QNN are excluded here: each fit takes minutes, so 25 folds "
            "would take hours for a result the single split already shows.",
            "",
            "We deliberately do **not** compute a p-value from these folds. "
            "Repeated-CV folds share training rows, so they are correlated and a "
            "naive paired t-test would be over-confident. The standard deviation "
            "is reported as a spread, not as a significance test.",
            "",
        ]

    body_parts += [
        "## Verdict",
        "",
        *[f"- {line}" for line in verdict_lines],
        "",
        f"Best classical F1 on this split: **{best_classical['model']}** at "
        f"{float(best_classical['point']):.4f} "
        f"[{float(best_classical['ci_lower']):.4f}, {float(best_classical['ci_upper']):.4f}].",
        "",
        "The defensible claim is about **cost**, not accuracy: the classical and "
        "quantum-kernel models land in the same interval, while the circuit "
        "models take orders of magnitude longer on a simulator. Statistical "
        "significance here says nothing about clinical usefulness.",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
    ]
    report.write_text("\n".join(body_parts), encoding="utf-8")

    for line in verdict_lines:
        print(line)
    print()
    print(f"Wrote {get_metrics_dir() / names['bootstrap_csv']}")
    print(f"Wrote {get_metrics_dir() / names['pairs_csv']}")
    if not cv_frame.empty:
        print(f"Wrote {get_metrics_dir() / names['cv_csv']}")
    print(f"Wrote {report}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Significance run failed: {exc}", file=sys.stderr)
        raise
