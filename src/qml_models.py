"""Hybrid QML helpers (Qiskit Aer simulator). VQC + QSVC on a few features.

Research risk classification - not for clinical use.
"""

from __future__ import annotations

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import SVC

from src.preprocessing import RANDOM_STATE


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


def require_qnn():
    """Import the EstimatorQNN pieces used for the 'or equivalent' QNN track."""
    try:
        from qiskit_machine_learning.algorithms import NeuralNetworkClassifier
        from qiskit_machine_learning.neural_networks import EstimatorQNN
    except ImportError as exc:
        raise ImportError(
            "EstimatorQNN needs qiskit-machine-learning. Install with:\n"
            "  pip install qiskit-machine-learning\n"
            f"Original error: {exc}"
        ) from exc
    return EstimatorQNN, NeuralNetworkClassifier


def scale_to_unit_interval(x_train, x_test):
    """Map features to [0, 1] for angle encoding. Fit on train only."""
    scaler = MinMaxScaler(feature_range=(0.0, 1.0))
    x_train_s = scaler.fit_transform(x_train)
    x_test_s = scaler.transform(x_test)
    return scaler, np.asarray(x_train_s, dtype=float), np.asarray(x_test_s, dtype=float)


def build_rbf_svm_pipeline() -> Pipeline:
    """Classical kernel SVM on the same reduced features as QSVC (fair kernel baseline)."""
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                SVC(
                    kernel="rbf",
                    C=1.0,
                    gamma="scale",
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def recording_cobyla(maxiter: int, history: list[float]):
    """COBYLA as a Qiskit ``Minimizer`` that appends every objective value.

    ``VQC``/``NeuralNetworkClassifier`` accept a ``callback``, but in
    qiskit-machine-learning 0.9 it is not invoked on the COBYLA path, so the
    trace would always be empty. Wrapping the objective ourselves records the
    real convergence curve while still running SciPy's COBYLA.
    """
    from scipy.optimize import minimize as scipy_minimize

    def minimizer(fun, x0, jac=None, bounds=None):
        def recorded(params):
            value = float(fun(params))
            history.append(value)
            return value

        result = scipy_minimize(
            recorded,
            np.asarray(x0, dtype=float),
            method="COBYLA",
            options={"maxiter": int(maxiter)},
        )
        try:
            from qiskit_algorithms.optimizers import OptimizerResult

            wrapped = OptimizerResult()
        except ImportError:  # pragma: no cover - optimizer package always present
            class _Result:
                x = None
                fun = None
                nfev = None
                nit = None

            wrapped = _Result()
        wrapped.x = result.x
        wrapped.fun = float(result.fun)
        wrapped.nfev = int(getattr(result, "nfev", len(history)))
        wrapped.nit = int(getattr(result, "nit", 0) or 0)
        return wrapped

    return minimizer


def build_vqc(
    *,
    n_qubits: int,
    maxiter: int = 80,
    feature_reps: int = 2,
    ansatz_reps: int = 2,
    history: list[float] | None = None,
):
    """Variational quantum classifier (statevector / Aer path).

    Pass ``history`` to collect the optimizer objective at every evaluation.
    """
    ZZFeatureMap, RealAmplitudes, COBYLA, VQC, _QSVC, _Kernel = require_qiskit()
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=feature_reps)
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=ansatz_reps)
    optimizer = (
        recording_cobyla(maxiter, history) if history is not None else COBYLA(maxiter=maxiter)
    )
    rng = np.random.default_rng(RANDOM_STATE)
    initial_point = rng.uniform(-0.1, 0.1, size=int(ansatz.num_parameters))

    kwargs = {
        "feature_map": feature_map,
        "ansatz": ansatz,
        "optimizer": optimizer,
        "initial_point": initial_point,
    }
    try:
        return VQC(**kwargs)
    except TypeError:
        sampler = _optional_sampler()
        if sampler is not None:
            kwargs["sampler"] = sampler
        return VQC(**kwargs)


def build_qsvc(*, n_qubits: int, feature_reps: int = 2):
    """Quantum SVM with an exact fidelity kernel (no shot noise)."""
    ZZFeatureMap, _RA, _Opt, _VQC, QSVC, FidelityStatevectorKernel = require_qiskit()
    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=feature_reps)
    kernel = FidelityStatevectorKernel(feature_map=feature_map)
    try:
        return QSVC(quantum_kernel=kernel, random_state=RANDOM_STATE)
    except TypeError:
        return QSVC(quantum_kernel=kernel)


def labels_to_pm1(y) -> np.ndarray:
    """Map {0, 1} labels to {-1, +1} for an expectation-value QNN."""
    array = np.asarray(y).astype(int)
    unknown = set(np.unique(array)) - {0, 1}
    if unknown:
        raise ValueError(f"Expected 0/1 labels, saw {sorted(unknown)}.")
    return (2 * array - 1).astype(float)


def build_qnn_classifier(
    *,
    n_qubits: int,
    maxiter: int = 40,
    feature_reps: int = 2,
    ansatz_reps: int = 1,
    history: list[float] | None = None,
):
    """Quantum neural network classifier (EstimatorQNN + COBYLA).

    The problem statement allows "QNN or equivalent"; this is the QNN track.
    Fit it on {-1, +1} labels (see :func:`labels_to_pm1`).
    """
    ZZFeatureMap, RealAmplitudes, COBYLA, *_rest = require_qiskit()
    EstimatorQNN, NeuralNetworkClassifier = require_qnn()

    feature_map = ZZFeatureMap(feature_dimension=n_qubits, reps=feature_reps)
    ansatz = RealAmplitudes(num_qubits=n_qubits, reps=ansatz_reps)
    circuit = feature_map.compose(ansatz)
    qnn = EstimatorQNN(
        circuit=circuit,
        input_params=list(feature_map.parameters),
        weight_params=list(ansatz.parameters),
    )
    rng = np.random.default_rng(RANDOM_STATE)
    initial_point = rng.uniform(-0.1, 0.1, size=int(ansatz.num_parameters))
    optimizer = (
        recording_cobyla(maxiter, history) if history is not None else COBYLA(maxiter=maxiter)
    )
    return NeuralNetworkClassifier(
        neural_network=qnn,
        loss="squared_error",
        optimizer=optimizer,
        initial_point=initial_point,
    )


def swap_in_picklable_optimizer(model, *, maxiter: int) -> None:
    """Replace a recording ``Minimizer`` closure with a plain COBYLA.

    The trace wrapper is a local closure, so a fitted model holding it cannot
    be pickled. Trained weights are unaffected.
    """
    _fm, _ansatz, COBYLA, *_rest = require_qiskit()
    if hasattr(model, "_optimizer"):
        model._optimizer = COBYLA(maxiter=int(maxiter))


def qnn_ranking_scores(classifier, x) -> np.ndarray:
    """Raw expectation values in [-1, 1] used as the ROC ranking score."""
    weights = getattr(classifier, "weights", None)
    if weights is None:
        fit_result = getattr(classifier, "_fit_result", None)
        weights = getattr(fit_result, "x", None)
    if weights is None:
        raise RuntimeError("Fit the QNN classifier before asking for scores.")
    raw = classifier.neural_network.forward(np.asarray(x, dtype=float), weights)
    return np.asarray(raw, dtype=float).ravel()


def describe_circuits(*, n_qubits: int, feature_reps: int, ansatz_reps: int) -> str:
    """Beginner-readable description of the hybrid circuits."""
    return "\n".join(
        [
            f"Qubits: {n_qubits} (one per selected feature).",
            f"Feature map: ZZFeatureMap, reps={feature_reps} (angle encoding + ZZ entangling).",
            f"VQC ansatz: RealAmplitudes, reps={ansatz_reps}.",
            "QSVC kernel: FidelityStatevectorKernel (exact state overlap, simulator).",
            "Backend: classical simulator, not a hospital QPU.",
            "Research risk classification - not for clinical use.",
        ]
    )


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
