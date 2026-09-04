"""Qiskit import is optional for unit tests; training is a separate command."""

from __future__ import annotations

import pytest


def test_qml_helpers_import_or_explain() -> None:
    from src.qml_models import require_qiskit

    try:
        require_qiskit()
    except ImportError:
        pytest.skip("Qiskit QML packages are not installed in this environment.")
