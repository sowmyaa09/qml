"""Project paths and small helpers.

All file locations are relative to the repository root so the project
runs the same on any computer (no hard-coded C:\\... paths).
"""

from __future__ import annotations

from pathlib import Path

# Every training command only writes PNG files. Leaving matplotlib on a GUI
# backend let Tk objects be finalized on a worker thread during long Qiskit
# fits, which killed the process with "Tcl_AsyncDelete: async handler deleted
# by the wrong thread". Selecting Agg here covers every entry point, because
# they all import this module.
try:  # pragma: no cover - depends on the installed backend
    import matplotlib

    matplotlib.use("Agg")
except Exception:  # matplotlib is optional for the pure-data helpers
    pass

RESEARCH_DISCLAIMER = "Research risk classification - not for clinical use."

LONG_DISCLAIMER = (
    "This project is for educational and research purposes only. "
    "It is not a medical device and must not be used for clinical "
    "diagnosis or treatment decisions."
)


def get_project_root() -> Path:
    """Return the repository root (the folder that contains ``src/``)."""
    return Path(__file__).resolve().parent.parent


def get_models_dir() -> Path:
    """Folder where trained ``.joblib`` files are saved."""
    return get_project_root() / "models"


def get_figures_dir() -> Path:
    """Folder where PNG plots are saved."""
    return get_project_root() / "outputs" / "figures"


def get_metrics_dir() -> Path:
    """Folder where the metrics CSV is saved."""
    return get_project_root() / "outputs" / "metrics"


def get_reports_dir() -> Path:
    """Folder where markdown/json research notes are saved."""
    return get_project_root() / "outputs" / "reports"


def ensure_output_directories() -> None:
    """Create models/ and outputs/ folders if they do not exist yet."""
    for directory in (
        get_models_dir(),
        get_figures_dir(),
        get_metrics_dir(),
        get_project_root() / "outputs" / "reports",
        get_project_root() / "data" / "raw",
        get_project_root() / "data" / "processed",
    ):
        directory.mkdir(parents=True, exist_ok=True)
