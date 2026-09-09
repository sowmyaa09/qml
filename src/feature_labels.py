"""Plain-language labels for public-table columns. Not a diagnosis catalog.

Keys match catalog schema column names. Paste and API scoring still use the
short keys (e.g. ``mean perimeter``, ``cp``).

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from typing import Any

# label = full readable name; description = one sentence for judges / beginners.
FIELD_LABELS: dict[str, dict[str, str]] = {
    "mean perimeter": {
        "label": "Mean perimeter of cell nuclei",
        "description": (
            "Average length around the edge of breast cell nuclei in the "
            "fine-needle aspirate (FNA) sample (Wisconsin benchmark units)."
        ),
    },
    "mean concave points": {
        "label": "Mean concave points (indent severity)",
        "description": (
            "Average severity of inward curves on the nuclear boundary — "
            "a shape measure from the same FNA image analysis."
        ),
    },
    "worst radius": {
        "label": "Worst (largest) radius of cell nuclei",
        "description": (
            "Largest half-width among the most abnormal-looking nuclei in "
            "the sample (radius = distance from center to the edge)."
        ),
    },
    "worst perimeter": {
        "label": "Worst (largest) perimeter of cell nuclei",
        "description": (
            "Longest edge-length around the most abnormal nuclei — related "
            "to how large and irregular those cells appear."
        ),
    },
    "worst area": {
        "label": "Worst (largest) area of cell nuclei",
        "description": (
            "Largest nuclear footprint among the most abnormal cells in "
            "the FNA sample."
        ),
    },
    "worst concave points": {
        "label": "Worst concave points (max indent severity)",
        "description": (
            "Strongest inward curve on the most abnormal nuclei — a shape "
            "feature, not a symptom."
        ),
    },
    "cp": {
        "label": "Chest Pain type (CP)",
        "description": (
            "Chest pain category on the UCI heart benchmark: "
            "0 = typical angina, 1 = atypical angina, "
            "2 = non-anginal pain, 3 = asymptomatic. "
            "This is not a 1–10 pain score and not headache."
        ),
    },
}


def label_for(field: str) -> str:
    """Full readable name, or the raw column key if unknown."""
    meta = FIELD_LABELS.get(field)
    return meta["label"] if meta else field


def description_for(field: str) -> str:
    """One-line help text, or empty if unknown."""
    meta = FIELD_LABELS.get(field)
    return meta["description"] if meta else ""


def enrich_field(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Attach label + description to a slider/catalog field dict."""
    out = dict(payload)
    out["name"] = name
    meta = FIELD_LABELS.get(name)
    if meta:
        out["label"] = meta["label"]
        out["description"] = meta["description"]
    else:
        out["label"] = name
        out["description"] = ""
    return out
