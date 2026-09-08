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
    "coimbra": ("uciml/breast-cancer-coimbra-data-set",),
    "seizure": ("harunshimanto/epileptic-seizure-recognition",),
    "framingham": (
        "dileep070/heart-disease-prediction-using-logistic-regression",
        "aasheesh200/framingham-heart-study-dataset",
    ),
    "cervical": ("loveall/cervical-cancer-risk-classification",),
    "hepatitis": ("codebreaker619/hepatitis-data",),
    "brfss_heart": (
        "kamilpytlak/personal-key-indicators-of-heart-disease",
        "mlfamm/heart-2020-cleaned",
    ),
    "pcos": (
        "prasoonkottarathil/polycystic-ovary-syndrome-pcos",
        "shreyasvedpathak/pcos-dataset",
    ),
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
    uci_id: int | None = None
    zenodo_file_url: str | None = None
    http_urls: tuple[str, ...] = ()
    # Several headerless files from *different cohorts* that share one schema
    # and are meant to be pooled. Not mirrors of the same rows.
    pooled_urls: tuple[str, ...] = ()
    pooled_columns: tuple[str, ...] = ()


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
    "coimbra": TabularSpec(
        key="coimbra",
        title="Breast Cancer Coimbra (UCI blood markers, not WDBC)",
        kaggle_slug="uciml/breast-cancer-coimbra-data-set",
        csv_glob="*.csv",
        target_column="Classification",
        positive_name="Classification=patient (2) in this table",
        uci_id=451,
        notes=(
            "Nine routine blood/anthropometry fields. Different from Wisconsin FNA. "
            "Separate research task."
        ),
    ),
    "seizure": TabularSpec(
        key="seizure",
        title="Epileptic seizure recognition (EEG chunks, binary 1 vs rest)",
        kaggle_slug="harunshimanto/epileptic-seizure-recognition",
        csv_glob="*.csv",
        target_column="y",
        drop_columns=("Unnamed: 0",),
        positive_name="y=1 seizure class in this table",
        uci_id=None,
        notes=(
            "178 EEG samples per 1s chunk. Binary: class 1 vs 2–5. "
            "Not a clinical EEG product. Do not send 178 columns into QML."
        ),
    ),
    "framingham": TabularSpec(
        key="framingham",
        title="Framingham 10-year CHD (public teaching subset)",
        kaggle_slug="dileep070/heart-disease-prediction-using-logistic-regression",
        csv_glob="*.csv",
        target_column="TenYearCHD",
        positive_name="TenYearCHD=1 in this table",
        http_urls=(
            "https://raw.githubusercontent.com/dhirajk100/Framingham/master/framingham.csv",
        ),
        notes="Classic risk-factor table. Separate from Kaggle cardio_train.",
    ),
    "seer_breast": TabularSpec(
        key="seer_breast",
        title="SEER breast cancer subset (survival status, not FNA)",
        kaggle_slug="zenodo/seer-breast-cancer-subset",
        csv_glob="*.csv",
        target_column="Status",
        drop_columns=("Survival Months", "Survival months"),
        positive_name="Status=Dead in this SEER subset",
        zenodo_file_url=(
            "https://zenodo.org/api/records/5120960/files/"
            "SEER%20Breast%20Cancer%20Dataset%20.csv/content"
        ),
        notes=(
            "All rows already have breast cancer. Target is Alive/Dead on this public "
            "subset. Drop survival-months (leakage). Not Wisconsin FNA."
        ),
    ),
    "cervical": TabularSpec(
        key="cervical",
        title="Cervical cancer risk factors (UCI, Biopsy label)",
        kaggle_slug="loveall/cervical-cancer-risk-classification",
        csv_glob="*.csv",
        target_column="Biopsy",
        drop_columns=("Hinselmann", "Schiller", "Citology"),
        positive_name="Biopsy=1 in this table",
        uci_id=383,
        notes=(
            "Survey/risk-factor fields; other screening tests dropped so they are not "
            "used as extra labels. Many missing values. Separate research task."
        ),
    ),
    "hepatitis": TabularSpec(
        key="hepatitis",
        title="UCI hepatitis (die vs live on this table)",
        kaggle_slug="codebreaker619/hepatitis-data",
        csv_glob="*.csv",
        target_column="Class",
        positive_name="Class=die (1) in this table",
        uci_id=46,
        notes="Tiny UCI table. Class 1=die, 2=live in the UCI encoding.",
    ),
    "brfss_heart": TabularSpec(
        key="brfss_heart",
        title="CDC BRFSS 2020 heart-disease survey indicators",
        kaggle_slug="kamilpytlak/personal-key-indicators-of-heart-disease",
        csv_glob="heart_2020_cleaned.csv",
        target_column="HeartDisease",
        positive_name="HeartDisease=Yes on this 2020 BRFSS survey table",
        zenodo_file_url=(
            "https://zenodo.org/api/records/15364962/files/"
            "heart_2020_cleaned.csv/content"
        ),
        http_urls=(
            "https://raw.githubusercontent.com/ParthGohil21/Heart-Disease/main/"
            "heart_2020_cleaned.csv",
        ),
        notes=(
            "About 320k unique telephone-survey adults, not 320k hospital charts. "
            "Not Kaggle cardio_train and not the 2015 BRFSS diabetes table. "
            "Identical answer patterns can still appear (few categorical bins); "
            "those are dropped so they cannot leak across the split. "
            "Stroke/diabetes/kidney columns here are survey covariates for this "
            "one heart-disease label — not extra diagnoses. Classical only; "
            "do not send this table into QSVC."
        ),
    ),
    "heart_uci_pooled": TabularSpec(
        key="heart_uci_pooled",
        title="UCI heart disease, four cohorts pooled (Cleveland + Hungary + Switzerland + VA)",
        kaggle_slug="",
        csv_glob="pooled.csv",
        target_column="num",
        drop_columns=("source_cohort",),
        positive_name="num > 0 (disease present) in these UCI cohorts",
        pooled_urls=(
            "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.hungarian.data",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.switzerland.data",
            "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.va.data",
        ),
        pooled_columns=(
            "age",
            "sex",
            "cp",
            "trestbps",
            "chol",
            "fbs",
            "restecg",
            "thalach",
            "exang",
            "oldpeak",
            "slope",
            "ca",
            "thal",
            "num",
        ),
        notes=(
            "920 patients from four hospitals that share the same 14 attributes: "
            "Cleveland 303, Hungary 294, Switzerland 123, VA Long Beach 200. "
            "Disease prevalence differs a lot by site, so the cohort column is "
            "dropped from the features - otherwise a model can just learn the "
            "site's base rate. Hungary/Switzerland/VA have many missing values."
        ),
    ),
    "pcos": TabularSpec(
        key="pcos",
        title="PCOS clinical table (Kaggle public dump)",
        kaggle_slug="prasoonkottarathil/polycystic-ovary-syndrome-pcos",
        csv_glob="*.*",
        target_column="PCOS (Y/N)",
        drop_columns=("Sl. No", "Patient File No.", "Sl No"),
        positive_name="PCOS=Yes in this table",
        notes=(
            "Kaggle clinical spreadsheet. Quality varies by mirror. "
            "Separate endocrine research table, not a fused diagnosis."
        ),
    ),
}


def list_dataset_keys() -> list[str]:
    return list(CATALOG.keys())


def _kaggle_cache_root() -> Path:
    return Path.home() / ".cache" / "kagglehub" / "datasets"


def find_csv_for_spec(spec: TabularSpec) -> Path:
    """Return the CSV from cache, Kaggle, UCI, Zenodo, or a direct URL."""
    errors: list[str] = []

    # Multi-cohort tables build their own combined file; the generic local scan
    # below would otherwise grab a single cohort part.
    if spec.pooled_urls:
        pooled = _pooled_fallback(spec)
        if pooled is not None:
            return pooled

    local = get_project_root() / "data" / "raw" / spec.key
    hit = _first_table(local, spec.csv_glob) if local.is_dir() else None
    if hit is not None:
        return hit

    try:
        uci_path = _uci_fallback(spec)
        if uci_path is not None:
            return uci_path
    except Exception as exc:
        errors.append(f"uci: {exc}")

    try:
        remote = _url_fallback(spec)
        if remote is not None:
            return remote
    except Exception as exc:
        errors.append(f"url: {exc}")

    slugs = (spec.kaggle_slug, *ALTERNATE_SLUGS.get(spec.key, ()))
    for slug in slugs:
        if not slug or "/" not in slug:
            continue
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
        f"Could not load table for {spec.key}. Tried: " + " | ".join(errors)
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


def _uci_fallback(spec: TabularSpec) -> Path | None:
    if spec.uci_id is None:
        return None
    url = f"https://archive.ics.uci.edu/static/public/{spec.uci_id}/data.csv"
    dest = get_project_root() / "data" / "raw" / spec.key / "uci_data.csv"
    return _download_url(url, dest)


def _url_fallback(spec: TabularSpec) -> Path | None:
    dest_dir = get_project_root() / "data" / "raw" / spec.key
    if spec.zenodo_file_url:
        return _download_url(spec.zenodo_file_url, dest_dir / "zenodo.csv")
    for i, url in enumerate(spec.http_urls):
        try:
            return _download_url(url, dest_dir / f"remote_{i}.csv")
        except Exception:
            continue
    return None


def _pooled_fallback(spec: TabularSpec) -> Path | None:
    """Download several same-schema cohorts and concatenate them once."""
    if not spec.pooled_urls:
        return None
    dest_dir = get_project_root() / "data" / "raw" / spec.key
    combined = dest_dir / "pooled.csv"
    if combined.is_file() and combined.stat().st_size > 200:
        return combined

    frames = []
    for url in spec.pooled_urls:
        name = url.rsplit("/", 1)[-1]
        part = _download_url(url, dest_dir / name)
        frame = pd.read_csv(
            part,
            header=None,
            names=list(spec.pooled_columns),
            na_values=["?", "-9", "-9.0"],
        )
        cohort = name.replace("processed.", "").replace(".data", "")
        frame["source_cohort"] = cohort
        frames.append(frame)
        print(f"  pooled cohort {cohort}: {len(frame)} rows", flush=True)

    pooled = pd.concat(frames, ignore_index=True)
    combined.parent.mkdir(parents=True, exist_ok=True)
    pooled.to_csv(combined, index=False)
    print(f"  pooled total: {len(pooled)} rows -> {combined.name}", flush=True)
    return combined


def _download_url(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 200:
        return dest
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Q-Care-Detect-research/1.0"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        dest.write_bytes(response.read())
    if dest.stat().st_size < 200:
        dest.unlink(missing_ok=True)
        raise FileNotFoundError(f"Download too small: {url}")
    return dest


def _find_csv_for_slug(spec: TabularSpec, slug: str) -> Path:
    owner, name = slug.split("/", 1)
    cache_dataset = _kaggle_cache_root() / owner / name
    hit = _first_table(cache_dataset, spec.csv_glob) if cache_dataset.is_dir() else None
    if hit is not None:
        return hit

    local = get_project_root() / "data" / "raw" / spec.key
    hit = _first_table(local, spec.csv_glob) if local.is_dir() else None
    if hit is not None:
        return hit

    try:
        import kagglehub
    except ImportError as exc:
        raise FileNotFoundError(
            f"No cached CSV for {spec.key} and kagglehub is not installed."
        ) from exc

    folder = Path(kagglehub.dataset_download(slug))
    hit = _first_table(folder, spec.csv_glob)
    if hit is None:
        raise FileNotFoundError(f"No table matching {spec.csv_glob} under {folder}")
    return hit


_TABLE_SUFFIXES = {".csv", ".data", ".txt", ".xlsx", ".xls"}


def _first_table(root: Path, pattern: str) -> Path | None:
    matches = sorted(root.rglob(pattern))
    files = [
        p
        for p in matches
        if p.is_file() and p.suffix.lower() in _TABLE_SUFFIXES
        and p.name.lower() not in {"license.txt", "readme.txt"}
    ]
    if files:
        return files[0]
    files = [
        p
        for p in sorted(root.rglob("*"))
        if p.is_file()
        and p.suffix.lower() in _TABLE_SUFFIXES
        and p.name.lower() not in {"license.txt", "readme.txt"}
    ]
    return files[0] if files else None


def _read_csv(path: Path, spec: TabularSpec) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        frame = _read_excel_table(path)
    else:
        sep = spec.separator
        if sep is None:
            sample = path.read_text(encoding="utf-8", errors="replace")[:4096]
            sep = ";" if sample.count(";") > sample.count(",") else ","
        frame = pd.read_csv(path, sep=sep)
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame


def _read_excel_table(path: Path) -> pd.DataFrame:
    book = pd.ExcelFile(path)
    ranked: list[tuple[int, str]] = []
    for name in book.sheet_names:
        preview = pd.read_excel(book, sheet_name=name, nrows=1)
        cols = " ".join(str(c).lower() for c in preview.columns)
        score = 0
        if any(token in cols for token in ("pcos", "classification", "outcome", "target")):
            score += 10
        if "instruction" in name.lower() or "readme" in name.lower():
            score -= 20
        if "without" in name.lower() or "full" in name.lower():
            score += 3
        ranked.append((score, name))
    ranked.sort(reverse=True)
    return pd.read_excel(book, sheet_name=ranked[0][1])


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
    if spec.key == "coimbra":
        numeric = pd.to_numeric(series, errors="coerce")
        # UCI: 1 = healthy control, 2 = patient
        return numeric.map({1: 0, 2: 1}).astype("Int64")
    if spec.key == "hepatitis":
        numeric = pd.to_numeric(series, errors="coerce")
        # UCI: 1 = die, 2 = live
        mapped = numeric.map({1: 1, 2: 0})
        if mapped.isna().all():
            mapped = cleaned.replace({"die": 1, "live": 0, "death": 1})
        return mapped.astype("Int64")
    if spec.key == "seizure":
        numeric = pd.to_numeric(series, errors="coerce")
        return (numeric == 1).astype(int)
    if spec.key == "heart_uci_pooled":
        # UCI grades severity 0-4; any grade above 0 counts as disease present.
        numeric = pd.to_numeric(series, errors="coerce")
        mapped = (numeric > 0).astype("Int64")
        mapped[numeric.isna()] = pd.NA
        return mapped
    if spec.key == "seer_breast":
        mapped = cleaned.replace({"dead": 1, "alive": 0, "1": 1, "0": 0})
        numeric = pd.to_numeric(mapped, errors="coerce")
        return numeric.astype("Int64")
    if spec.key == "pcos":
        mapped = cleaned.replace(
            {"yes": 1, "no": 0, "y": 1, "n": 0, "1": 1, "0": 0, "1.0": 1, "0.0": 0}
        )
        return pd.to_numeric(mapped, errors="coerce").astype("Int64")
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
        return pd.to_numeric(mapped, errors="coerce").astype("Int64")
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


def _repair_source_errors(frame: pd.DataFrame, spec: TabularSpec) -> pd.DataFrame:
    """Drop physically impossible rows (not a learned transform)."""
    out = frame.copy()
    if spec.key == "cardio":
        for col in ("ap_hi", "ap_lo", "height", "weight"):
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")
        mask = pd.Series(True, index=out.index)
        if "ap_hi" in out.columns:
            mask &= out["ap_hi"].between(60, 250)
        if "ap_lo" in out.columns:
            mask &= out["ap_lo"].between(40, 150)
        if "ap_hi" in out.columns and "ap_lo" in out.columns:
            mask &= out["ap_hi"] > out["ap_lo"]
        if "height" in out.columns:
            mask &= out["height"].between(100, 230)
        if "weight" in out.columns:
            mask &= out["weight"].between(35, 200)
        out = out.loc[mask]
    return out


def load_tabular_dataset(
    key: str,
    *,
    drop_duplicates: bool = True,
) -> tuple[TabularSpec, pd.DataFrame, pd.Series, Path]:
    """Load features X and target y for one catalog key.

    Exact duplicate rows are dropped by default. Many public disease tables are
    re-uploads that repeat their source rows, and an identical row landing in
    both train and test leaks the answer. Pass ``drop_duplicates=False`` to
    measure that instead (see ``src.audit_datasets``).
    """
    if key not in CATALOG:
        raise KeyError(f"Unknown dataset {key!r}. Choose from: {list_dataset_keys()}")
    spec = CATALOG[key]
    path = find_csv_for_spec(spec)
    frame = _read_csv(path, spec)
    frame = _repair_source_errors(frame, spec)

    target_col = spec.target_column
    if target_col not in frame.columns:
        lowered = {c.lower(): c for c in frame.columns}
        fallbacks = [target_col, *{
            "thyroid": ("Recurred", "class", "Class", "binaryClass", "Category"),
            "parkinson": ("status", "Class", "class"),
            "pima": ("Outcome", "class"),
            "coimbra": ("Classification", "classification"),
            "seizure": ("y", "Y", "class"),
            "framingham": ("TenYearCHD", "TenYearCHD "),
            "seer_breast": ("Status", "status"),
            "cervical": ("Biopsy", "biopsy"),
            "hepatitis": ("Class", "class", "Category"),
            "brfss_heart": ("HeartDisease", "Heart Disease", "heartdisease"),
            "pcos": ("PCOS (Y/N)", "PCOS(Y/N)", "PCOS", "pcos"),
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
    features = features.drop(
        columns=[c for c in features.columns if str(c).lower().startswith("unnamed")],
        errors="ignore",
    )
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
    valid = target.notna()
    features = features.loc[valid]
    target = target.loc[valid].astype(int)
    if spec.binary and set(target.unique()) - {0, 1}:
        raise ValueError(
            f"{spec.key}: binary target must be 0/1 after mapping, got {sorted(target.unique())}"
        )

    if drop_duplicates:
        stacked = features.copy()
        stacked["__target__"] = target.to_numpy()
        keep = ~stacked.duplicated()
        removed = int((~keep).sum())
        if removed:
            features = features.loc[keep.to_numpy()]
            target = target.loc[keep.to_numpy()]
            print(
                f"  dropped {removed} exact duplicate rows from {spec.key} "
                f"({removed / len(stacked):.1%}) - identical rows in train and "
                "test would leak the label",
                flush=True,
            )
    return spec, features, target, path
