"""Train a small CNN on one public MSK image research set.

    python -m src.train_msk fracture --epochs 3 --max-per-class 200
    python -m src.train_msk spine --epochs 3 --max-per-class 200

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

from src.image_datasets import (
    IMAGE_CATALOG,
    find_dataset_root,
    infer_imagefolder_dirs,
)
from src.preprocessing import RANDOM_STATE
from src.train_wbc import pick_device, run_one_epoch, set_seeds
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_figures_dir,
    get_metrics_dir,
    get_models_dir,
)
from src.wbc_data import IMAGE_SIZE
from src.wbc_model import SmallWbcCnn, count_trainable_parameters

sns.set_theme(style="whitegrid")


def _tf(*, train: bool):
    ops = [transforms.Resize((IMAGE_SIZE, IMAGE_SIZE))]
    if train:
        ops.append(transforms.RandomHorizontalFlip())
    ops.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
        ]
    )
    return transforms.Compose(ops)


def _cap_per_class(dataset: datasets.ImageFolder, max_per_class: int | None, seed: int):
    if max_per_class is None:
        return dataset
    buckets: dict[int, list[int]] = defaultdict(list)
    for idx, label in enumerate(dataset.targets):
        buckets[int(label)].append(idx)
    rng = random.Random(seed)
    chosen: list[int] = []
    for label, idxs in buckets.items():
        rng.shuffle(idxs)
        chosen.extend(idxs[:max_per_class])
    chosen.sort()
    return Subset(dataset, chosen)


def _subset_targets(dataset) -> list[int]:
    if isinstance(dataset, Subset):
        base = dataset.dataset
        return [int(base.targets[i]) for i in dataset.indices]
    return [int(t) for t in dataset.targets]


def _collect(model, loader, device):
    model.eval()
    y_true: list[int] = []
    y_pred: list[int] = []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            logits = model(images)
            pred = logits.argmax(dim=1).cpu().numpy()
            y_pred.extend(pred.tolist())
            y_true.extend(labels.numpy().tolist())
    return np.array(y_true), np.array(y_pred)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", nargs="?", default=None, help="fracture | spine")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-per-class", type=int, default=250)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    args = parser.parse_args(argv)

    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print("Image research experiment - not injury diagnosis.")
    print()

    if args.list or args.dataset is None:
        for key, spec in IMAGE_CATALOG.items():
            print(f"  {key:12s} {spec.title}")
            print(f"               {spec.notes}")
        if args.dataset is None:
            print("\nExample: python -m src.train_msk fracture")
        return 0

    if args.dataset not in IMAGE_CATALOG:
        print(f"Unknown image dataset {args.dataset!r}", file=sys.stderr)
        return 1

    spec = IMAGE_CATALOG[args.dataset]
    ensure_output_directories()
    set_seeds(RANDOM_STATE)
    device = pick_device()
    print(f"Device: {device}")
    print(spec.notes)

    root = find_dataset_root(spec)
    train_dir, test_dir = infer_imagefolder_dirs(root)
    print(f"Train images from: {train_dir}")

    train_ds = datasets.ImageFolder(train_dir, transform=_tf(train=True))
    class_names = list(train_ds.classes)
    train_ds = _cap_per_class(train_ds, args.max_per_class, RANDOM_STATE)

    if test_dir is not None:
        test_ds = datasets.ImageFolder(test_dir, transform=_tf(train=False))
        test_ds = _cap_per_class(test_ds, args.max_per_class, RANDOM_STATE + 1)
    else:
        indices = list(range(len(train_ds)))
        labels = _subset_targets(train_ds)
        try:
            tr, te = train_test_split(
                indices,
                test_size=0.2,
                random_state=RANDOM_STATE,
                stratify=labels,
            )
        except ValueError:
            tr, te = train_test_split(
                indices, test_size=0.2, random_state=RANDOM_STATE
            )
        base = train_ds
        train_ds = Subset(base, tr)
        # eval transform: rebuild folder without flip
        eval_full = datasets.ImageFolder(train_dir, transform=_tf(train=False))
        if isinstance(base, Subset):
            original_indices = [base.indices[i] for i in te]
            test_ds = Subset(eval_full, original_indices)
        else:
            test_ds = Subset(eval_full, te)

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0
    )
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0
    )

    n_classes = len(class_names)
    model = SmallWbcCnn(n_classes=n_classes).to(device)
    print(f"Classes ({n_classes}): {class_names}")
    print(f"Trainable weights: {count_trainable_parameters(model):,}")

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    history = {"train_loss": [], "val_loss": []}
    for epoch in range(1, args.epochs + 1):
        train_loss = run_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = run_one_epoch(model, test_loader, criterion, None, device)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        print(
            f"Epoch {epoch}/{args.epochs}  train_loss={train_loss:.4f}  "
            f"val_loss={val_loss:.4f}",
            flush=True,
        )

    y_true, y_pred = _collect(model, test_loader, device)
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "n_classes": n_classes,
        "n_test": int(len(y_true)),
    }

    prefix = f"msk_{spec.key}"
    figures = get_figures_dir()
    cm_path = figures / f"{prefix}_confusion_matrix.png"
    curve_path = figures / f"{prefix}_training_curves.png"
    matrix = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title(f"{spec.title}\n{RESEARCH_DISCLAIMER}")
    fig.tight_layout()
    fig.savefig(cm_path, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history["train_loss"], label="train")
    ax.plot(history["val_loss"], label="val")
    ax.legend()
    ax.set_title(f"{spec.key} training loss\n{RESEARCH_DISCLAIMER}")
    fig.tight_layout()
    fig.savefig(curve_path, dpi=150)
    plt.close(fig)

    metrics_path = get_metrics_dir() / f"{prefix}_metrics.csv"
    pd.DataFrame([metrics]).to_csv(metrics_path, index=False)
    model_path = get_models_dir() / f"{prefix}_cnn.pt"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "class_names": class_names,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        model_path,
    )
    print(f"Saved {model_path}")
    print(f"Saved {metrics_path}")
    print(f"accuracy={metrics['accuracy']:.4f} macro_f1={metrics['macro_f1']:.4f}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"MSK training failed: {exc}", file=sys.stderr)
        raise
