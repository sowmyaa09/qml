"""Locate and load the public Raabin-WBC / Kaggle white-blood-cell images.

This is a research dataset of microscope photos of five cell types.
It is not a diagnostic tool and is not used to name a person's disease.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.preprocessing import RANDOM_STATE
from src.utils import get_project_root

WBC_KAGGLE_SLUG = "masoudnickparvar/white-blood-cells-dataset"
WBC_CLASSES = (
    "Basophil",
    "Eosinophil",
    "Lymphocyte",
    "Monocyte",
    "Neutrophil",
)
IMAGE_SIZE = 96


def find_wbc_dataset_root() -> Path:
    """Return the folder that contains Train/ and Test-A/.

    Looks in the project ``data/raw/white-blood-cells`` copy first, then
    the KaggleHub cache (and downloads if needed).
    """
    local = get_project_root() / "data" / "raw" / "white-blood-cells"
    if (local / "Train").is_dir() and (local / "Test-A").is_dir():
        return local

    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError(
            "The white-blood-cell images were not found in data/raw/"
            "white-blood-cells and kagglehub is not installed. "
            "Run: pip install kagglehub"
        ) from exc

    cached = Path(kagglehub.dataset_download(WBC_KAGGLE_SLUG))
    if not (cached / "Train").is_dir():
        raise FileNotFoundError(
            f"Downloaded WBC data at {cached} but found no Train/ folder."
        )
    return cached


def _transforms(*, train: bool) -> transforms.Compose:
    if train:
        return transforms.Compose(
            [
                transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=(0.5, 0.5, 0.5),
                    std=(0.5, 0.5, 0.5),
                ),
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.5, 0.5, 0.5),
                std=(0.5, 0.5, 0.5),
            ),
        ]
    )


def make_wbc_dataloaders(
    *,
    batch_size: int = 32,
    root: Path | None = None,
) -> tuple[DataLoader, DataLoader, list[str]]:
    """Build train and Test-A loaders. Test-B is ignored (only two classes)."""
    root = root or find_wbc_dataset_root()
    train_dir = root / "Train"
    test_dir = root / "Test-A"
    if not train_dir.is_dir() or not test_dir.is_dir():
        raise FileNotFoundError(
            f"Expected Train/ and Test-A/ under {root}. "
            "Re-download with kagglehub if the folder is incomplete."
        )

    train_set = datasets.ImageFolder(str(train_dir), transform=_transforms(train=True))
    test_set = datasets.ImageFolder(str(test_dir), transform=_transforms(train=False))
    class_names = [name for name, _ in sorted(train_set.class_to_idx.items(), key=lambda kv: kv[1])]
    if set(class_names) != set(WBC_CLASSES):
        raise RuntimeError(
            f"Expected classes {WBC_CLASSES}, found {class_names}."
        )

    train_loader = DataLoader(
        train_set,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        generator=torch.Generator().manual_seed(RANDOM_STATE),
    )
    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    return train_loader, test_loader, class_names


def inspect_wbc_dataset(root: Path | None = None) -> str:
    """Beginner-friendly counts of images per cell type."""
    root = root or find_wbc_dataset_root()
    lines = [
        "Dataset: White blood cells (Kaggle / Raabin-WBC, public research images)",
        "Task: classify cell type in a microscope photo (5 classes).",
        "Research risk classification - not for clinical use.",
        "This does not diagnose a person or name a disease.",
        f"Root folder: {root}",
    ]
    for split in ("Train", "Test-A"):
        split_dir = root / split
        lines.append(f"{split}:")
        for name in WBC_CLASSES:
            folder = split_dir / name
            count = len(list(folder.glob("*"))) if folder.is_dir() else 0
            lines.append(f"  {name}: {count}")
    return "\n".join(lines)
