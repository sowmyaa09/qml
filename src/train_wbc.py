"""Train a small CNN on public white-blood-cell microscope images.

Run from the project root (venv on):

    python -m src.train_wbc

This classifies cell type (Basophil, Eosinophil, Lymphocyte, Monocyte,
Neutrophil). It is not a diagnosis of a person.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.utils.class_weight import compute_class_weight
from torch import nn
from torch.utils.data import DataLoader

from src.preprocessing import RANDOM_STATE
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_figures_dir,
    get_metrics_dir,
    get_models_dir,
)
from src.wbc_data import find_wbc_dataset_root, inspect_wbc_dataset, make_wbc_dataloaders
from src.wbc_model import SmallWbcCnn, count_trainable_parameters

sns.set_theme(style="whitegrid")


def pick_device() -> torch.device:
    """Use the NVIDIA GPU when PyTorch can see it; otherwise CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def set_seeds(seed: int = RANDOM_STATE) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def class_weights_from_counts(counts: list[int], device: torch.device) -> torch.Tensor:
    """Heavier loss on rare cell types (Basophil is much rarer than Neutrophil)."""
    y_all = np.concatenate(
        [np.full(count, idx, dtype=np.int64) for idx, count in enumerate(counts)]
    )
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(len(counts)),
        y=y_all,
    )
    return torch.tensor(weights, dtype=torch.float32, device=device)


def run_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    device: torch.device,
) -> float:
    train = optimizer is not None
    model.train(train)
    total_loss = 0.0
    n_seen = 0
    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)
        if train:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        batch = labels.size(0)
        total_loss += loss.item() * batch
        n_seen += batch
    return total_loss / max(n_seen, 1)


@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    y_true: list[np.ndarray] = []
    y_pred: list[np.ndarray] = []
    for images, labels in loader:
        logits = model(images.to(device))
        pred = logits.argmax(dim=1).cpu().numpy()
        y_true.append(labels.numpy())
        y_pred.append(pred)
    return np.concatenate(y_true), np.concatenate(y_pred)


def multiclass_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Accuracy plus macro-averaged precision, recall, and F1 (each in [0, 1])."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def plot_confusion(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    output_path: Path,
) -> None:
    matrix = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_xlabel("Predicted cell type")
    ax.set_ylabel("True cell type")
    ax.set_title(f"WBC CNN confusion matrix\n{RESEARCH_DISCLAIMER}")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_loss_curves(history: dict[str, list[float]], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history["train_loss"], label="Train loss")
    ax.plot(history["val_loss"], label="Test-A loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title(f"WBC CNN training curves\n{RESEARCH_DISCLAIMER}")
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a small CNN on public WBC images (research only)."
    )
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(LONG_DISCLAIMER, flush=True)
    print(RESEARCH_DISCLAIMER, flush=True)
    print(
        "This model labels cell type in a photo. It does not diagnose a person.",
        flush=True,
    )
    print(flush=True)

    set_seeds()
    ensure_output_directories()
    device = pick_device()
    print(f"Device: {device}", flush=True)
    if device.type == "cpu":
        print(
            "PyTorch does not see a CUDA GPU. Training will be slower. "
            "Install a CUDA build from https://pytorch.org if you have an NVIDIA GPU."
        )

    root = find_wbc_dataset_root()
    print(inspect_wbc_dataset(root), flush=True)
    print(flush=True)

    train_loader, test_loader, class_names = make_wbc_dataloaders(
        batch_size=args.batch_size,
        root=root,
    )
    n_classes = len(class_names)
    model = SmallWbcCnn(n_classes=n_classes).to(device)
    n_params = count_trainable_parameters(model)
    print(f"Trainable weights: {n_params:,}", flush=True)
    print(flush=True)

    train_targets = np.array(train_loader.dataset.targets)
    counts = [int((train_targets == idx).sum()) for idx in range(n_classes)]
    weights = class_weights_from_counts(counts, device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}
    for epoch in range(1, args.epochs + 1):
        train_loss = run_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = run_one_epoch(model, test_loader, criterion, None, device)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(
            f"Epoch {epoch}/{args.epochs}  train_loss={train_loss:.4f}  "
            f"testA_loss={val_loss:.4f}",
            flush=True,
        )

    y_true, y_pred = collect_predictions(model, test_loader, device)
    metrics = multiclass_metrics(y_true, y_pred)

    figures = get_figures_dir()
    metrics_path = get_metrics_dir() / "wbc_cnn_metrics.csv"
    model_path = get_models_dir() / "wbc_cnn.pt"
    cm_path = figures / "wbc_cnn_confusion_matrix.png"
    curve_path = figures / "wbc_cnn_training_curves.png"

    plot_confusion(y_true, y_pred, class_names, cm_path)
    plot_loss_curves(history, curve_path)
    pd.DataFrame([{**metrics, "n_parameters": n_params}]).to_csv(
        metrics_path, index=False
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "class_names": class_names,
            "n_parameters": n_params,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        model_path,
    )

    print()
    print("Test-A metrics (cell-type classification, not a diagnosis)")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    print()
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))
    print(f"Saved {model_path}")
    print(f"Saved {metrics_path}")
    print(f"Saved {cm_path}")
    print(f"Saved {curve_path}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"WBC training failed: {exc}", file=sys.stderr)
        raise
