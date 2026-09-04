"""Hybrid QML helpers (Qiskit Aer simulator). VQC + QSVC on a few features.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.preprocessing import MinMaxScaler


def require_qiskit():
    """Import Qiskit ML pieces or raise a clear install error."""
    try:
        from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_machine_learning.algorithms import QSVC, VQC
        from qiskit_machine_learning.kernels import FidelityStatevectorKernel
    except ImportError as exc:
        raise ImportError(
            "Qiskit QML packages are missing. From the project venv run:\n"
            "  pip install qiskit qiskit-aer qiskit-algorithms "
            "qiskit-machine-learning\n"
            f"Original error: {exc}"
        ) from exc
    return ZZFeatureMap, RealAmplitudes, COBYLA, VQC, QSVC, FidelityStatevectorKernel


def scale_to_unit_interval(x_train, x_test):
    """Map features to [0, 1] for angle encoding. Fit on train only."""
    scaler = MinMaxScaler(feature_range=(0.0, 1.0))
    x_train_s = scaler.fit_transform(x_train)
    x_test_s = scaler.transform(x_test)
    return scaler, np.asarray(x_train_s, dtype=float), np.asarray(x_test_s, dtype=float)


def build_vqc(*, n_qubits: int, maxiter: int = 40):
    """Variational quantum classifier on the Aer/statevector simulator path."""
    ZZFeatureMap, RealAmplitudes, COBYLA, VQC, _QSVC, _Kernel = require_qiskit()
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=1)
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=1)
    optimizer = COBYLA(maxiter=maxiter)

    kwargs = {
        "feature_map": feature_map,
        "ansatz": ansatz,
        "optimizer": optimizer,
    }
    try:
        return VQC(**kwargs)
    except TypeError:
        sampler = _optional_sampler()
        if sampler is None:
            raise
        return VQC(sampler=sampler, **kwargs)


def build_qsvc(*, n_qubits: int):
    """Quantum SVM with a fidelity kernel (statevector; no hardware)."""
    ZZFeatureMap, _RA, _Opt, _VQC, QSVC, FidelityStatevectorKernel = require_qiskit()
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=1)
    kernel = FidelityStatevectorKernel(feature_map=feature_map)
    return QSVC(quantum_kernel=kernel)


def _optional_sampler():
    try:
        from qiskit.primitives import StatevectorSampler

        return StatevectorSampler()
    except Exception:
        pass
    try:
        from qiskit.primitives import Sampler

        return Sampler()
    except Exception:
        return None


@dataclass(frozen=True)
class TimedFit:
    model: object
    fit_seconds: float
    predict_seconds: float
