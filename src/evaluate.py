"""Metrics, plots, and a beginner-friendly comparison of two models.

Malignant is the positive class (1):
  TP = malignant predicted malignant
  FN = malignant predicted benign
  Sensitivity / Recall = TP / (TP + FN)
  Specificity = TN / (TN + FP)
  ROC-AUC uses predicted probabilities, not hard 0/1 labels.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.utils import RESEARCH_DISCLAIMER, get_figures_dir, get_metrics_dir

sns.set_theme(style="whitegrid")

METRIC_DISPLAY_ORDER = (
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1",
    "roc_auc",
)


def compute_specificity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Specificity = TN / (TN + FP) from the confusion matrix."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    denominator = tn + fp
    if denominator == 0:
        raise ValueError(
            "Cannot compute specificity: there are no true-negative or "
            "false-positive cases in this batch (TN + FP = 0)."
        )
    return float(tn / denominator)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
) -> dict[str, float]:
    """Return accuracy, precision, recall, specificity, F1, and ROC-AUC.

    Parameters
    ----------
    y_true :
        True labels (1 = malignant).
    y_pred :
        Predicted class labels (0 or 1).
    y_prob :
        Predicted probability of class 1 (malignant), from predict_proba[:, 1].
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_prob = np.asarray(y_prob)

    if y_prob.ndim != 1:
        raise ValueError("y_prob must be a 1-D array of probabilities for class 1.")

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": compute_specificity(y_true, y_pred),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
    }
    for name, value in metrics.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Metric {name}={value} is outside [0, 1].")
    return metrics


def _caption() -> str:
    return RESEARCH_DISCLAIMER


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_title: str,
    output_path: Path,
) -> Path:
    """Save a heatmap of the 2x2 confusion matrix."""
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Benign (0)", "Malignant (1)"],
        yticklabels=["Benign (0)", "Malignant (1)"],
        ax=ax,
    )
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"{model_title}\n{_caption()}")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_roc_comparison(
    y_true: np.ndarray,
    probabilities_by_model: dict[str, np.ndarray],
    output_path: Path,
) -> Path:
    """Save one ROC plot with a curve for each model."""
    fig, ax = plt.subplots(figsize=(7, 6))
    for name, y_prob in probabilities_by_model.items():
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        ax.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate (recall)")
    ax.set_title(f"ROC curve comparison\n{_caption()}")
    ax.legend(loc="lower right")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_metric_bars(
    metrics_by_model: dict[str, dict[str, float]],
    output_path: Path,
) -> Path:
    """Save a grouped bar chart of the main metrics for each model."""
    rows: list[dict[str, Any]] = []
    for model_name, metrics in metrics_by_model.items():
        for metric_name in METRIC_DISPLAY_ORDER:
            rows.append(
                {
                    "model": model_name,
                    "metric": metric_name,
                    "value": metrics[metric_name],
                }
            )
    frame = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=frame, x="metric", y="value", hue="model", ax=ax)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Score")
    ax.set_xlabel("Metric")
    ax.set_title(f"Model metric comparison\n{_caption()}")
    ax.legend(title="Model")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def save_metrics_csv(
    metrics_by_model: dict[str, dict[str, float]],
    output_path: Path | None = None,
) -> Path:
    """Write one row per model to a CSV file."""
    if output_path is None:
        output_path = get_metrics_dir() / "classical_model_metrics.csv"
    rows = [{"model": name, **scores} for name, scores in metrics_by_model.items()]
    frame = pd.DataFrame(rows)
    column_order = ["model", *METRIC_DISPLAY_ORDER]
    frame = frame[column_order]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return output_path


def beginner_summary(
    metrics_by_model: dict[str, dict[str, float]],
    *,
    positive_name: str = "positive-class",
) -> str:
    """Explain which model looked stronger on this test set, in plain language."""
    if len(metrics_by_model) < 2:
        names = list(metrics_by_model)
        return f"Only one model was evaluated: {names[0] if names else 'none'}."

    # Rank by recall first (catching malignant cases), then F1, then ROC-AUC.
    ranked = sorted(
        metrics_by_model.items(),
        key=lambda item: (item[1]["recall"], item[1]["f1"], item[1]["roc_auc"]),
        reverse=True,
    )
    best_name, best = ranked[0]
    other_name, other = ranked[1]

    lines = [
        RESEARCH_DISCLAIMER,
        "",
        "Beginner summary (this public test split only - not a clinical ranking)",
        "",
        f"On recall (catching {positive_name} rows), {best_name} scored {best['recall']:.3f} "
        f"and {other_name} scored {other['recall']:.3f}.",
        f"On F1 (balance of precision and recall), {best_name} scored {best['f1']:.3f} "
        f"and {other_name} scored {other['f1']:.3f}.",
        f"On ROC-AUC (ranking quality from probabilities), {best_name} scored "
        f"{best['roc_auc']:.3f} and {other_name} scored {other['roc_auc']:.3f}.",
        "",
        f"For this research comparison we highlight {best_name} because it did at "
        "least as well on recall, then F1, then ROC-AUC. That does not mean it is "
        "a medical test. Accuracy alone can look high while still missing "
        f"{positive_name} cases, so we look at several metrics.",
        "",
        "A later quantum model is not assumed to beat these numbers.",
    ]
    return "\n".join(lines)


def evaluate_models(
    y_true,
    predictions_by_model: dict[str, np.ndarray],
    probabilities_by_model: dict[str, np.ndarray],
    *,
    save_plots: bool = True,
    artifact_prefix: str = "",
) -> dict[str, dict[str, float]]:
    """Compute metrics for each model and optionally write PNG + CSV files."""
    figures = get_figures_dir()
    y_true_arr = np.asarray(y_true)
    metrics_by_model: dict[str, dict[str, float]] = {}
    prefix = f"{artifact_prefix}_" if artifact_prefix else ""

    file_stems = {
        "Logistic Regression": f"{prefix}logistic_regression_confusion_matrix.png",
        "Random Forest": f"{prefix}random_forest_confusion_matrix.png",
    }

    for name, y_pred in predictions_by_model.items():
        y_prob = np.asarray(probabilities_by_model[name])
        y_pred_arr = np.asarray(y_pred)
        metrics_by_model[name] = compute_classification_metrics(
            y_true_arr, y_pred_arr, y_prob
        )
        if save_plots:
            stem = file_stems.get(
                name, f"{prefix}{name.lower().replace(' ', '_')}_confusion_matrix.png"
            )
            plot_confusion_matrix(y_true_arr, y_pred_arr, name, figures / stem)

    if save_plots:
        plot_roc_comparison(
            y_true_arr,
            {k: np.asarray(v) for k, v in probabilities_by_model.items()},
            figures / f"{prefix}roc_curve_comparison.png",
        )
        plot_metric_bars(
            metrics_by_model,
            figures / f"{prefix}model_metric_comparison.png",
        )
        csv_name = f"{prefix}classical_model_metrics.csv" if prefix else "classical_model_metrics.csv"
        save_metrics_csv(metrics_by_model, get_metrics_dir() / csv_name)

    return metrics_by_model
