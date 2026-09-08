"""Duplicate-row audit for every catalog table.

    python -m src.audit_datasets
    python -m src.audit_datasets --keys heart_disease cardio

Why this exists: public disease tables are re-uploaded constantly, and many
"bigger" mirrors are the original rows repeated. Identical rows split across
train and test leak the answer and inflate every score. This script measures
that instead of guessing.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

import pandas as pd

from src.tabular_datasets import CATALOG, list_dataset_keys, load_tabular_dataset
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
    get_reports_dir,
)

CSV_NAME = "dataset_duplicate_audit.csv"
REPORT_NAME = "dataset_duplicate_audit.md"
# Above this share of repeated rows, a random split almost certainly puts the
# same row on both sides.
LEAKAGE_WARN_SHARE = 0.05


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Count duplicate rows per table.")
    parser.add_argument(
        "--keys",
        nargs="+",
        default=None,
        help="Catalog keys to audit (default: all).",
    )
    return parser.parse_args(argv)


def audit_key(key: str) -> dict:
    """Duplicate counts for one table, measured before any train/test split."""
    spec, features, target, path = load_tabular_dataset(key, drop_duplicates=False)
    rows = len(features)
    with_target = features.copy()
    with_target["__target__"] = target.to_numpy()

    duplicate_full = int(with_target.duplicated().sum())
    duplicate_features_only = int(features.duplicated().sum())
    conflicting = duplicate_features_only - duplicate_full

    return {
        "key": key,
        "title": spec.title,
        "file": path.name,
        "rows": rows,
        "unique_rows": rows - duplicate_full,
        "duplicate_rows": duplicate_full,
        "duplicate_share": round(duplicate_full / rows, 4) if rows else 0.0,
        "same_features_different_label": max(conflicting, 0),
        "leakage_risk": duplicate_full / rows > LEAKAGE_WARN_SHARE if rows else False,
    }


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
                cells.append("**yes**" if value else "no")
            elif isinstance(value, float):
                cells.append(f"{value:.4f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    print(LONG_DISCLAIMER, flush=True)
    print(RESEARCH_DISCLAIMER)
    print("Duplicate-row audit - looking for hidden train/test leakage.")
    print(flush=True)
    ensure_output_directories()

    keys = args.keys or list_dataset_keys()
    rows: list[dict] = []
    for key in keys:
        if key not in CATALOG:
            print(f"SKIP unknown key {key!r}", file=sys.stderr)
            continue
        try:
            result = audit_key(key)
        except Exception as exc:
            print(f"SKIP {key}: {exc}", file=sys.stderr)
            continue
        rows.append(result)
        flag = "  <-- LEAKAGE RISK" if result["leakage_risk"] else ""
        print(
            f"  {key:<14} rows={result['rows']:<7} duplicates="
            f"{result['duplicate_rows']:<7} "
            f"({result['duplicate_share']:.1%}){flag}",
            flush=True,
        )

    if not rows:
        print("Nothing audited.", file=sys.stderr)
        return 1

    frame = pd.DataFrame(rows).sort_values("duplicate_share", ascending=False)
    csv_path = get_metrics_dir() / CSV_NAME
    frame.to_csv(csv_path, index=False)

    risky = frame[frame["leakage_risk"]]
    report = get_reports_dir() / REPORT_NAME
    body = "\n".join(
        [
            "# Duplicate-row audit",
            "",
            RESEARCH_DISCLAIMER,
            "",
            "Counted on the **whole** table, before any train/test split.",
            "",
            "- `duplicate_rows`: rows whose features **and** label already appear "
            "earlier in the file.",
            "- `same_features_different_label`: identical features carrying a "
            "different label. These are genuine source contradictions, not copies.",
            f"- `leakage_risk`: more than {LEAKAGE_WARN_SHARE:.0%} duplicates, so a "
            "random split will very likely place the same row in train and test.",
            "",
            _md_table(frame),
            "",
            "## Reading this",
            "",
            (
                "Tables flagged above are re-uploads that repeat their source rows. "
                "Concatenating more mirrors of them does **not** add cases; it adds "
                "copies, and copies raise scores without adding knowledge. "
                "`load_tabular_dataset` therefore drops exact duplicates by default."
                if not risky.empty
                else "No table crossed the duplicate threshold."
            ),
            "",
            "A legitimately larger dataset needs **different patients**, not the "
            "same rows again: for example the four UCI heart cohorts (Cleveland, "
            "Hungary, Switzerland, VA Long Beach), which share one schema but were "
            "collected at four sites.",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        ]
    )
    report.write_text(body, encoding="utf-8")

    print()
    if not risky.empty:
        print("Tables with duplicate-driven leakage risk:")
        for _, row in risky.iterrows():
            print(
                f"  {row['key']}: {row['duplicate_rows']} of {row['rows']} rows "
                f"are repeats ({row['duplicate_share']:.1%})"
            )
    print(f"Wrote {csv_path}")
    print(f"Wrote {report}")
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        raise
