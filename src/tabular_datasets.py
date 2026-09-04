"""Public tabular research datasets. One table = one binary (or few-class) task.

Never fused into a single “which disease do I have?” model.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.utils import get_project_root

ALTERNATE_SLUGS: dict[str, tuple[str, ...]] = {
    "thyroid": (
        "jainaru/thyroid-disease-data",
        "emmanuelfwerr/thyroid-disease-data",
    ),
    "parkinson": (
        "thehassansat/parkinsons-disease-dataset",
        "kmader/parkinsons-data",
    ),
    "kidney": ("abhia1999/chronic-kidney-disease",),
    "pima": ("uciml/pima-indians-diabetes-database",),
}


@dataclass(frozen=True)
class TabularSpec:
    """How to find and label one public CSV."""

    key: str
    title: str
    kaggle_slug: str
    csv_glob: str
    target_column: str
    drop_columns: tuple[str, ...] = ()
    positive_name: str = "positive class"
    separator: str | None = None
    binary: bool = True
    notes: str = ""


CATALOG: dict[str, TabularSpec] = {
    "cardio": TabularSpec(
        key="cardio",
        title="Cardiovascular disease (Kaggle cardio_train)",
        kaggle_slug="sulianova/cardiovascular-disease-dataset",
        csv_glob="cardio_train.csv",
        target_column="cardio",
        drop_columns=("id",),
        positive_name="cardio=1 in this table",
        separator=";",
        notes="Age is in days in the source file. Public Kaggle table only.",
    ),
    "stroke": TabularSpec(
        key="stroke",
        title="Stroke prediction (fedesoriano)",
        kaggle_slug="fedesoriano/stroke-prediction-dataset",
        csv_glob="*.csv",
        target_column="stroke",
        drop_columns=("id",),
        positive_name="stroke=1 in this table",
        notes="Includes categoricals (work type, smoking). Public table only.",
    ),
    "heart_failure": TabularSpec(
        key="heart_failure",
        title="Heart failure clinical records",
        kaggle_slug="andrewmvd/heart-failure-clinical-data",
        csv_glob="*.csv",
        target_column="DEATH_EVENT",
        positive_name="DEATH_EVENT=1 in this table",
    ),
    "heart_disease": TabularSpec(
        key="heart_disease",
        title="Heart disease (UCI-style Kaggle mirror)",
        kaggle_slug="johnsmith88/heart-disease-dataset",
        csv_glob="*.csv",
        target_column="target",
        positive_name="target=1 in this table",
    ),
    "liver": TabularSpec(
        key="liver",
        title="Indian liver patient records",
        kaggle_slug="uciml/indian-liver-patient-records",
        csv_glob="*.csv",
        target_column="Dataset",
        positive_name="liver patient label in this table",
        notes="Source uses Dataset=1 for liver patient, 2 otherwise.",
    ),
    "kidney": TabularSpec(
        key="kidney",
        title="Chronic kidney disease (public UCI/Kaggle mirror)",
        kaggle_slug="mansoordaku/ckdisease",
        csv_glob="*.csv",
        target_column="classification",
        drop_columns=("id",),
        positive_name="ckd label in this table",
    ),
    "thyroid": TabularSpec(
        key="thyroid",
        title="Thyroid disease (public Kaggle table)",
        kaggle_slug="yasserhessein/thyroid-disease-data-set",
        csv_glob="*.csv",
        target_column="Recurred",
        positive_name="Recurred=Yes in this table",
        notes="If this slug is missing, train_tabular skips with an error message.",
    ),
    "fetal": TabularSpec(
        key="fetal",
        title="Fetal health (3-class CTG table)",
        kaggle_slug="andrewmvd/fetal-health-classification",
        csv_glob="*.csv",
        target_column="fetal_health",
        binary=False,
        positive_name="fetal_health class in this table",
        notes="Three classes, not binary. Separate research task.",
    ),
    "parkinson": TabularSpec(
        key="parkinson",
        title="Parkinson’s (voice features, public table)",
        kaggle_slug="vikasukani/parkinsons-disease-data-set",
        csv_glob="*.csv",
        target_column="status",
        drop_columns=("name",),
        positive_name="status=1 in this table",
    ),
    "pima": TabularSpec(
        key="pima",
        title="Pima Indians diabetes (small UCI table)",
        kaggle_slug="uciml/pima-indians-diabetes-database",
        csv_glob="*.csv",
        target_column="Outcome",
        positive_name="Outcome=1 in this table",
        notes="Optional small diabetes table; separate from BRFSS diabetes.",
    ),
}


def list_dataset_keys() -> list[str]:
    return list(CATALOG.keys())


def _kaggle_cache_root() -> Path:
    return Path.home() / ".cache" / "kagglehub" / "datasets"


def find_csv_for_spec(spec: TabularSpec) -> Path:
    """Return the CSV from KaggleHub cache, downloading if needed."""
    slugs = (spec.kaggle_slug, *ALTERNATE_SLUGS.get(spec.key, ()))
    errors: list[str] = []
    for slug in slugs:
        try:
            return _find_csv_for_slug(spec, slug)
        except Exception as exc:
            errors.append(f"{slug}: {exc}")
    try:
        openml_path = _openml_fallback(spec)
        if openml_path is not None:
            return openml_path
    except Exception as exc:
        errors.append(f"openml: {exc}")
    raise FileNotFoundError(
        f"Could not load CSV for {spec.key}. Tried: " + " | ".join(errors)
    )


def _openml_fallback(spec: TabularSpec) -> Path | None:
    """Write a small OpenML table to data/raw when Kaggle is blocked."""
    mapping = {
        "pima": ("diabetes", None),
        "parkinson": ("parkinsons", None),
    }
    if spec.key not in mapping:
        return None
    name, _ = mapping[spec.key]
    from sklearn.datasets import fetch_openml

    bunch = fetch_openml(name, version=1, as_frame=True, parser="auto")
    frame = bunch.frame
    out_dir = get_project_root() / "data" / "raw" / spec.key
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec.key}.csv"
    frame.to_csv(path, index=False)
    return path


def _find_csv_for_slug(spec: TabularSpec, slug: str) -> Path:
    owner, name = slug.split("/", 1)
    cache_dataset = _kaggle_cache_root() / owner / name
    hit = _first_csv(cache_dataset, spec.csv_glob) if cache_dataset.is_dir() else None
    if hit is not None:
        return hit

    local = get_project_root() / "data" / "raw" / spec.key
    hit = _first_csv(local, spec.csv_glob) if local.is_dir() else None
    if hit is not None:
        return hit

    try:
        import kagglehub
    except ImportError as exc:
        raise FileNotFoundError(
            f"No cached CSV for {spec.key} and kagglehub is not installed."
        ) from exc

    folder = Path(kagglehub.dataset_download(slug))
    hit = _first_csv(folder, spec.csv_glob)
    if hit is None:
        raise FileNotFoundError(f"No CSV matching {spec.csv_glob} under {folder}")
    return hit


def _first_csv(root: Path, pattern: str) -> Path | None:
    if "*" in pattern:
        matches = sorted(root.rglob(pattern))
    else:
        matches = sorted(root.rglob(pattern))
    files = [p for p in matches if p.is_file()]
    if not files:
        files = [
            p
            for p in sorted(root.rglob("*"))
            if p.is_file() and p.suffix.lower() in {".csv", ".data", ".txt"}
            and p.name.lower() not in {"license.txt", "readme.txt"}
        ]
    return files[0] if files else None


def _read_csv(path: Path, spec: TabularSpec) -> pd.DataFrame:
    sep = spec.separator
    if sep is None:
        sample = path.read_text(encoding="utf-8", errors="replace")[:4096]
        sep = ";" if sample.count(";") > sample.count(",") else ","
    frame = pd.read_csv(path, sep=sep)
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame


def _map_target(series: pd.Series, spec: TabularSpec) -> pd.Series:
    cleaned = series.astype(str).str.strip().str.lower()
    if spec.key == "liver":
        # UCI: 1 = liver patient, 2 = non-patient
        mapped = series.replace({1: 1, 2: 0, "1": 1, "2": 0})
        return mapped.astype(int)
    if spec.key == "kidney":
        def _ckd(value: str):
            if "not" in value:
                return 0
            if "ckd" in value:
                return 1
            return pd.NA

        return cleaned.map(_ckd).astype("Int64").astype(int)
    if spec.key == "thyroid":
        mapped = cleaned.replace({"yes": 1, "no": 0, "true": 1, "false": 0})
        return mapped.astype(int)
    if spec.key == "pima":
        mapped = cleaned.replace(
            {
                "tested_positive": 1,
                "tested_negative": 0,
                "1": 1,
                "0": 0,
                "yes": 1,
                "no": 0,
            }
        )
        return pd.to_numeric(mapped, errors="coerce").astype(int)
    if spec.binary:
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.isna().any() and cleaned.nunique() <= 4:
            mapped = cleaned.replace({"yes": 1, "no": 0, "true": 1, "false": 0})
            return mapped.astype(int)
        return numeric.astype(int)
    # Multiclass: keep integer class ids, possibly starting at 1.
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        codes, _uniques = pd.factorize(series.astype(str).str.strip())
        return pd.Series(codes, index=series.index, name=spec.target_column)
    return numeric.astype(int)


def load_tabular_dataset(key: str) -> tuple[TabularSpec, pd.DataFrame, pd.Series, Path]:
    """Load features X and target y for one catalog key."""
    if key not in CATALOG:
        raise KeyError(f"Unknown dataset {key!r}. Choose from: {list_dataset_keys()}")
    spec = CATALOG[key]
    path = find_csv_for_spec(spec)
    frame = _read_csv(path, spec)

    target_col = spec.target_column
    if target_col not in frame.columns:
        lowered = {c.lower(): c for c in frame.columns}
        fallbacks = [target_col, *{
            "thyroid": ("Recurred", "class", "Class", "binaryClass", "Category"),
            "parkinson": ("status", "Class", "class"),
            "pima": ("Outcome", "class"),
        }.get(spec.key, ())]
        found = None
        for name in fallbacks:
            if name in frame.columns:
                found = name
                break
            if name.lower() in lowered:
                found = lowered[name.lower()]
                break
        if found is None:
            raise ValueError(
                f"{spec.key}: expected target {spec.target_column!r} in {list(frame.columns)}"
            )
        target_col = found

    target = _map_target(frame[target_col], spec)
    drop = [target_col, *spec.drop_columns]
    features = frame.drop(columns=[c for c in drop if c in frame.columns])
    features = features.replace("?", pd.NA)
    features = features.replace("\t?", pd.NA)
    for col in features.columns:
        if features[col].dtype == object:
            numeric = pd.to_numeric(
                features[col].astype(str).str.replace("\t", "", regex=False),
                errors="coerce",
            )
            if numeric.notna().mean() > 0.8:
                features[col] = numeric
    features = pd.get_dummies(features, drop_first=True)
    features = features.apply(pd.to_numeric, errors="coerce")
    features = features.fillna(features.median(numeric_only=True))
    features = features.fillna(0)
    valid = target.notna()
    features = features.loc[valid]
    target = target.loc[valid].astype(int)
    if spec.binary and set(target.unique()) - {0, 1}:
        raise ValueError(
            f"{spec.key}: binary target must be 0/1 after mapping, got {sorted(target.unique())}"
        )
    return spec, features, target, path
