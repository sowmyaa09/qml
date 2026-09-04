"""Public image-folder research sets (fracture / spine), WBC-style CNN.

Laptop-sized. Not QML. Not all injuries. Labels exist only inside that dataset.

    python -m src.train_msk --list
    python -m src.train_msk fracture --epochs 4 --max-per-class 250
    python -m src.train_msk spine --epochs 4 --max-per-class 250

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.utils import get_project_root


@dataclass(frozen=True)
class ImageSpec:
    key: str
    title: str
    kaggle_slug: str
    notes: str


IMAGE_CATALOG: dict[str, ImageSpec] = {
    "fracture": ImageSpec(
        key="fracture",
        title="Bone fracture X-ray research set (Kaggle labels only)",
        kaggle_slug="vuppalaadithyasairam/bone-fracture-detection-using-xrays",
        notes=(
            "Binary or few-class fracture labels in this archive only. "
            "Not all bones, not ER triage, not disfigurement."
        ),
    ),
    "spine": ImageSpec(
        key="spine",
        title="Spine X-ray research set (scoliosis vs normal labels in that file)",
        kaggle_slug="salmankey/scoliosis-yolov5-annotated-spine-x-ray-dataset",
        notes=(
            "YOLO-labeled public spine X-rays mapped to scoliosis vs normal "
            "for a CNN demo. Not all spinal cord injuries."
        ),
    ),
}

ALTERNATE_IMAGE_SLUGS: dict[str, tuple[str, ...]] = {
    "fracture": (
        "bmadushanirodrigo/fracture-multi-region-x-ray-data",
        "pkdarabi/bone-break-classification-image-dataset",
    ),
    "spine": (
        "c3ls1y/vertebraekeypoints50",
    ),
}


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_dataset_root(spec: ImageSpec) -> Path:
    slugs = (spec.kaggle_slug, *ALTERNATE_IMAGE_SLUGS.get(spec.key, ()))
    local = get_project_root() / "data" / "raw" / spec.key
    if local.is_dir() and _count_images(local) > 0:
        return local

    errors: list[str] = []
    for slug in slugs:
        owner, name = slug.split("/", 1)
        cache = Path.home() / ".cache" / "kagglehub" / "datasets" / owner / name
        if cache.is_dir() and _count_images(cache) > 0:
            if spec.key == "spine":
                converted = _yolo_detection_to_imagefolder(cache)
                if converted is not None:
                    return converted
            return cache
        try:
            import kagglehub

            downloaded = Path(kagglehub.dataset_download(slug))
            if spec.key == "spine":
                converted = _yolo_detection_to_imagefolder(downloaded)
                if converted is not None:
                    return converted
            if _count_images(downloaded) == 0:
                raise FileNotFoundError(f"No images under {downloaded}")
            return downloaded
        except Exception as exc:
            errors.append(f"{slug}: {exc}")
    raise FileNotFoundError(
        f"Could not locate images for {spec.key}. Tried: " + " | ".join(errors)
    )


def _yolo_detection_to_imagefolder(root: Path) -> Path | None:
    """Turn YOLO train/images + labels into class folders (scoliosis vs normal)."""
    image_dirs = list(root.rglob("images"))
    if not image_dirs:
        return None
    out = get_project_root() / "data" / "processed" / "spine_imagefolder"
    train_out = out / "train"
    test_out = out / "test"
    if train_out.is_dir() and _looks_like_class_dirs(train_out) and _count_images(train_out) > 0:
        return out

    import shutil

    copied = 0
    for img_dir in image_dirs:
        split_name = img_dir.parent.name.lower()
        dest_split = train_out if split_name in {"train", "training"} else test_out
        label_dir = img_dir.parent / "labels"
        for img in img_dir.iterdir():
            if img.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            label_path = label_dir / f"{img.stem}.txt"
            class_ids: set[int] = set()
            if label_path.is_file():
                for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines():
                    parts = line.strip().split()
                    if parts:
                        try:
                            class_ids.add(int(float(parts[0])))
                        except ValueError:
                            continue
            if 1 in class_ids:
                class_name = "scoliosis_spine"
            elif 2 in class_ids:
                class_name = "normal_spine"
            else:
                continue
            dest = dest_split / class_name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img, dest / img.name)
            copied += 1
    if copied == 0 or not _looks_like_class_dirs(train_out):
        return None
    return out


def _count_images(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS)


def infer_imagefolder_dirs(root: Path) -> tuple[Path, Path | None]:
    """Return (train_dir, optional_test_dir) for torchvision ImageFolder."""
    for train_name, test_name in (
        ("train", "val"),
        ("train", "test"),
        ("Train", "Test"),
        ("training", "testing"),
    ):
        train_dir = root / train_name
        test_dir = root / test_name
        if train_dir.is_dir() and _looks_like_class_dirs(train_dir):
            if test_dir.is_dir() and _looks_like_class_dirs(test_dir):
                return train_dir, test_dir
            return train_dir, None
    if _looks_like_class_dirs(root):
        return root, None
    # Nested single folder
    subdirs = [p for p in root.iterdir() if p.is_dir()]
    if len(subdirs) == 1:
        return infer_imagefolder_dirs(subdirs[0])
    raise FileNotFoundError(
        f"Could not find ImageFolder class directories under {root}"
    )


def _looks_like_class_dirs(path: Path) -> bool:
    class_dirs = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if len(class_dirs) < 2:
        return False
    return any(
        any(f.suffix.lower() in IMAGE_EXTENSIONS for f in d.rglob("*"))
        for d in class_dirs
    )
