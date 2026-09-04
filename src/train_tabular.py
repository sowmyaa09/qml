"""Train compact LR + RF on one public table from the catalog.

    python -m src.train_tabular --list
    python -m src.train_tabular cardio
    python -m src.train_tabular all

Each dataset is a separate experiment. Not a universal diagnosis model.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.evaluate import beginner_summary, evaluate_models
from src.preprocessing import RANDOM_STATE, stratified_train_test_split
from src.tabular_datasets import CATALOG, list_dataset_keys, load_tabular_dataset
from src.train_classical import (
    build_compact_random_forest,
    predict_with_probabilities,
    train_and_save_models,
)
from src.utils import (
    LONG_DISCLAIMER,
    RESEARCH_DISCLAIMER,
    ensure_output_directories,
    get_metrics_dir,
)


def _train_one(key: str) -> dict:
    spec, features, target, path = load_tabular_dataset(key)
    print(f"=== {spec.title} ===", flush=True)
    print(f"File: {path}", flush=True)
    print(f"Rows: {len(features)} | Features: {features.shape[1]}", flush=True)
    print(spec.notes or spec.positive_name, flush=True)
    print(RESEARCH_DISCLAIMER, flush=True)

    x_train, x_test, y_train, y_test = stratified_train_test_split(features, target)
    models = train_and_save_models(
        x_train,
        y_train,
        name_prefix=key,
        forest=build_compact_random_forest(),
    )

    if spec.binary:
        predictions = {}
        probabilities = {}
        for name, model in models.items():
            y_pred, y_prob = predict_with_probabilities(model, x_test)
            predictions[name] = y_pred
            probabilities[name] = y_prob
        metrics = evaluate_models(
            y_test,
            predictions,
            probabilities,
            save_plots=True,
            artifact_prefix=key,
        )
        print(beginner_summary(metrics, positive_name=spec.positive_name))
        return {"key": key, "ok": True, "metrics": metrics}

    # Multiclass: accuracy / macro-F1 only (no binary ROC).
    rows = []
    for name, model in models.items():
        y_pred = model.predict(x_test)
        y_true = np.asarray(y_test)
        row = {
            "model": name,
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(
                precision_score(y_true, y_pred, average="macro", zero_division=0)
            ),
            "recall": float(
                recall_score(y_true, y_pred, average="macro", zero_division=0)
            ),
            "f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        }
        rows.append(row)
        print(f"  {name}: acc={row['accuracy']:.4f} macro_f1={row['f1']:.4f}")
    out = get_metrics_dir() / f"{key}_classical_model_metrics.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {out} (multiclass; no ROC)")
    return {"key": key, "ok": True, "metrics": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Train compact classical models on one public table."
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default=None,
        help="Catalog key, or 'all'. Use --list to print keys.",
    )
    parser.add_argument("--list", action="store_true", help="Print catalog keys.")
    args = parser.parse_args(argv)

    print(LONG_DISCLAIMER)
    print(RESEARCH_DISCLAIMER)
    print("Separate research tables - not a fused diagnosis product.")
    print()

    if args.list or args.dataset is None:
        print("Available keys:")
        for key, spec in CATALOG.items():
            print(f"  {key:16s} {spec.title}")
        if args.dataset is None and not args.list:
            print("\nExample: python -m src.train_tabular cardio")
        return 0 if args.list or args.dataset is None else 1

    ensure_output_directories()
    keys = list_dataset_keys() if args.dataset == "all" else [args.dataset]
    failures: list[str] = []
    for key in keys:
        if key not in CATALOG:
            print(f"Unknown dataset {key!r}. Use --list.", file=sys.stderr)
            failures.append(key)
            continue
        try:
            _train_one(key)
        except Exception as exc:
            print(f"SKIP {key}: {exc}", file=sys.stderr)
            failures.append(f"{key}: {exc}")
        print()

    if failures:
        print("Finished with skips/failures:")
        for item in failures:
            print(f"  - {item}")
        # Still exit 0 if at least one dataset trained when using 'all'.
        if args.dataset != "all":
            return 1
    print(RESEARCH_DISCLAIMER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
