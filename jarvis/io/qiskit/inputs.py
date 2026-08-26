"""Module to solve Hermitian Matrix and predict bandstructures.

Migrated to Qiskit >= 1.2 / 2.x + qiskit-algorithms.
Supports: statevector simulator, Aer simulators, and IBM Quantum hardware.

Reference: https://doi.org/10.1088/1361-648X/ac1154

Install:
    pip install "qiskit>=1.2" qiskit-aer qiskit-algorithms
    pip install qiskit-ibm-runtime  # for hardware
"""

import numpy as np
import matplotlib.pyplot as plt

from qiskit.quantum_info import SparsePauliOp, Operator
from qiskit.circuit.library import EfficientSU2
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import SLSQP

from jarvis.core.kpoints import Kpoints3D as Kpoints
from jarvis.db.figshare import get_hk_tb
from jarvis.core.kpoints import generate_kgrid

plt.switch_backend("agg")


def _get_estimator(backend="statevector_simulator", seed=50, ibm_token=None):
    """Create the appropriate V2 Estimator for the requested backend.

    Parameters
    ----------
    backend : str
        "statevector_simulator", "aer_simulator*", or an IBM backend name
        like "ibm_kingston", "ibm_brisbane", etc.
    seed : int
        Random seed for reproducibility.
    ibm_token : str, optional
        IBM Quantum API token. Required for IBM hardware backends if
        not already saved via QiskitRuntimeService.save_account().
    """
    if backend == "statevector_simulator":
        from qiskit.primitives import StatevectorEstimator

        return StatevectorEstimator(seed=seed)

    elif backend.startswith("aer"):
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import EstimatorV2 as AerEstimator

        method_map = {
            "aer_simulator": "automatic",
            "aer_simulator_statevector": "statevector",
            "aer_simulator_density_matrix": "density_matrix",
            "aer_simulator_mps": "matrix_product_state",
        }
        method = method_map.get(backend, "automatic")
        aer_backend = AerSimulator(method=method, seed_simulator=seed)
        return AerEstimator.from_backend(aer_backend)

    else:
        # IBM hardware backend
        try:
            from qiskit_ibm_runtime import (
                QiskitRuntimeService,
                EstimatorV2 as RuntimeEstimator,
            )

            if ibm_token:
                # Try new IBM Cloud channel first; fall back to ibm_quantum
                try:
                    QiskitRuntimeService.save_account(
                        channel="ibm_cloud",
                        token=ibm_token,
                        overwrite=True,
                        set_as_default=True,
                    )
                except Exception:
                    QiskitRuntimeService.save_account(
                        channel="ibm_quantum",
                        token=ibm_token,
                        overwrite=True,
                        set_as_default=True,
                    )
            service = QiskitRuntimeService()
            hw_backend = service.backend(backend)
            return RuntimeEstimator(hw_backend)
        except ImportError:
            raise ImportError(
                f"Backend '{backend}' requires qiskit-ibm-runtime. "
                "Install: pip install qiskit-ibm-runtime"
            )
        except Exception as e:
            raise ValueError(f"Could not initialize backend '{backend}': {e}")


# Available backends for API/frontend enumeration
AVAILABLE_BACKENDS = [
    {
        "id": "statevector_simulator",
        "name": "Statevector (exact)",
        "desc": "Exact statevector simulation, no noise",
    },
    {
        "id": "aer_simulator",
        "name": "Aer (automatic)",
        "desc": "Aer simulator with automatic method selection",
    },
    {
        "id": "aer_simulator_statevector",
        "name": "Aer Statevector",
        "desc": "Aer with statevector method",
    },
    {
        "id": "aer_simulator_density_matrix",
        "name": "Aer Density Matrix",
        "desc": "Aer with density matrix method (supports noise)",
    },
    {
        "id": "aer_simulator_mps",
        "name": "Aer MPS",
        "desc": "Aer with matrix product state (larger qubit counts)",
    },
]


def decompose_Hamiltonian(H):
    """Decompose Hermitian matrix into Pauli basis."""
    return SparsePauliOp.from_operator(Operator(H)).simplify()


class HermitianSolver(object):
    """Solve a Hermitian matrix using quantum algorithms."""

    def __init__(self, mat=[], verbose=False):
        N = int(np.ceil(np.log2(len(mat))))
        hk = np.zeros((2**N, 2**N), dtype="complex")
        hk[: mat.shape[0], : mat.shape[1]] = mat
        self.mat = hk
        self.verbose = verbose
        if not self.check_hermitian():
            raise ValueError("Only implemented for Hermitian matrix.")

    def n_qubits(self):
        return int(np.log2(len(self.mat)))

    def check_hermitian(self):
        adjoint = self.mat.conj().T
        return np.allclose(self.mat, adjoint)

    def run_vqe(
        self,
        backend="statevector_simulator",
        var_form=None,
        optimizer=None,
        reps=None,
        mode="min_val",
        ibm_token=None,
    ):
        """Run variational quantum eigensolver.

        Auto-transpiles the ansatz to ISA circuits when running on real
        IBM hardware (required since March 2024).
        """
        seed = 50
        N = self.n_qubits()

        estimator = _get_estimator(
            backend=backend, seed=seed, ibm_token=ibm_token
        )

        if mode == "max_val":
            Hamil_qop = decompose_Hamiltonian(-1 * self.mat)
            np_eig = min(np.linalg.eig(-1 * self.mat)[0])
            if self.verbose:
                print("np_eig", np_eig)
        else:
            Hamil_qop = decompose_Hamiltonian(self.mat)
            np_eig = min(np.linalg.eig(self.mat)[0])
            if self.verbose:
                print("np_eig", np_eig)

        if var_form is None:
            if reps is None:
                reps = 2
            var_form = EfficientSU2(N, reps=reps)

        if optimizer is None:
            optimizer = SLSQP()

        # ── ISA TRANSPILATION FOR REAL HARDWARE ──
        is_hardware = not (
            backend == "statevector_simulator" or backend.startswith("aer")
        )
        if is_hardware:
            try:
                from qiskit.transpiler.preset_passmanagers import (
                    generate_preset_pass_manager,
                )
                from qiskit_ibm_runtime import QiskitRuntimeService

                service = QiskitRuntimeService()
                hw_backend = service.backend(backend)
                pm = generate_preset_pass_manager(
                    target=hw_backend.target, optimization_level=2
                )
                var_form = pm.run(var_form)
                # Re-map observable to transpiled qubit layout
                # Hamil_qop = Hamil_qop.apply_layout(var_form.layout)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to transpile circ. backend '{backend}':{e}"
                )

        vqe = VQE(estimator, var_form, optimizer)
        np.random.seed(seed)
        result = vqe.compute_minimum_eigenvalue(operator=Hamil_qop)
        en = result.eigenvalue

        if mode == "max_val":
            en = -1 * en

        return en, result, vqe

    def run_numpy(self):
        return np.linalg.eigh(self.mat)

    def run_vqd(
        self,
        backend="statevector_simulator",
        var_form=None,
        optimizer=None,
        reps=2,
        ibm_token=None,
    ):
        """Run variational quantum deflation."""
        tmp = HermitianSolver(self.mat)
        max_eigval, vqe_result, vqe = tmp.run_vqe(
            backend=backend,
            var_form=var_form,
            optimizer=optimizer,
            reps=reps,
            mode="max_val",
            ibm_token=ibm_token,
        )
        # Try to get eigenstate (V2 result has optimal_circuit, not eigenstate)
        try:
            from qiskit.quantum_info import Statevector

            if (
                hasattr(vqe_result, "optimal_circuit")
                and vqe_result.optimal_circuit is not None
            ):
                opt_c = vqe_result.optimal_circuit
                if opt_c.num_parameters > 0 and hasattr(
                    vqe_result, "optimal_point"
                ):
                    opt_c = opt_c.assign_parameters(
                        dict(zip(opt_c.parameters, vqe_result.optimal_point))
                    )
                eigstate = np.array(Statevector(opt_c)).flatten()
            else:
                eigstate = np.array(vqe_result.eigenstate).flatten()
        except Exception:
            eigstate = np.zeros(len(tmp.mat), dtype=complex)

        eigvals = [max_eigval]
        eigstates = [eigstate]

        for r in range(len(tmp.mat) - 1):
            val, vqe_result, vqe = tmp.run_vqe(
                backend=backend,
                var_form=var_form,
                optimizer=optimizer,
                reps=reps,
                ibm_token=ibm_token,
            )
            try:
                if (
                    hasattr(vqe_result, "optimal_circuit")
                    and vqe_result.optimal_circuit is not None
                ):
                    opt_c = vqe_result.optimal_circuit
                    if opt_c.num_parameters > 0 and hasattr(
                        vqe_result, "optimal_point"
                    ):
                        opt_c = opt_c.assign_parameters(
                            dict(
                                zip(opt_c.parameters, vqe_result.optimal_point)
                            )
                        )
                    eigstate = np.array(Statevector(opt_c)).flatten()
                else:
                    eigstate = np.array(vqe_result.eigenstate).flatten()
            except Exception:
                eigstate = np.zeros(len(tmp.mat), dtype=complex)

            outer_prod = np.outer(eigstate, np.conj(eigstate).T)
            tmp.mat = tmp.mat - (val - max_eigval) * outer_prod
            eigvals.append(val)
            eigstates.append(eigstate)
            tmp = HermitianSolver(tmp.mat)

        eigvals = np.array(eigvals)
        eigstates = np.array(eigstates)
        order = np.argsort(eigvals)
        eigvals = eigvals[order]
        eigstates = eigstates[order]
        return eigvals, eigstates


def get_bandstruct(
    w=[],
    atoms={},
    ef=0,
    line_density=1,
    ylabel="eV",
    font=22,
    var_form=None,
    filename="bands.png",
    savefig=True,
    neigs=None,
    max_nk=None,
    tol=None,
    factor=1,
    verbose=False,
    backend="statevector_simulator",
    ibm_token=None,
):
    """Compare bandstructures using quantum algos."""
    info = {}
    kpoints = Kpoints().kpath(atoms, line_density=line_density)
    labels = kpoints.to_dict()["labels"]
    kpts = kpoints.to_dict()["kpoints"]
    if verbose:
        print("Number of kpoints:", len(kpts))

    eigvals_q = []
    eigvals_np = []
    for ii, i in enumerate(kpts):
        if max_nk is not None and ii == max_nk:
            break
        try:
            hk = get_hk_tb(w=w, k=i)
            HS = HermitianSolver(hk)
            vqe_vals, _ = HS.run_vqd(
                var_form=var_form,
                backend=backend,
                ibm_token=ibm_token,
            )
            np_vals, _ = HS.run_numpy()
            if verbose:
                print("kp=", ii, i)
                print("np_vals", np_vals)
                print("vqe_vals", vqe_vals)
            eigvals_q.append(vqe_vals)
            eigvals_np.append(np_vals)
            if (
                neigs is not None
                and isinstance(neigs, int)
                and neigs == len(eigvals_q)
            ):
                break
        except Exception as exp:
            print(exp)
            pass

    eigvals_q = factor * np.array(eigvals_q)
    eigvals_np = factor * np.array(eigvals_np)

    for ii, i in enumerate(eigvals_q.T - ef):
        plt.plot(i, "*", c="b", label="VQD" if ii == 0 else "")
    for ii, i in enumerate(eigvals_np.T - ef):
        plt.plot(i, c="g", label="Numpy" if ii == 0 else "")

    new_kp, new_labels, count = [], [], 0
    kp = np.arange(len(kpts))
    for i, j in zip(kp, labels):
        if j != "":
            if count > 1 and count < len(labels) - 1:
                if labels[count] != labels[count + 1]:
                    new_kp.append(i)
                    new_labels.append("$" + str(j) + "$")
            else:
                new_kp.append(i)
                new_labels.append("$" + str(j) + "$")
        count += 1

    info["eigvals_q"] = list(eigvals_q.tolist())
    info["eigvals_np"] = list(eigvals_np.tolist())
    info["kpts"] = list(kpts)
    info["new_kp"] = list(np.array(new_kp).tolist())
    info["new_labels"] = list(new_labels)
    info["ef"] = ef
    if verbose:
        print(info)
    if tol is not None:
        plt.ylim([tol, np.max(eigvals_q)])
    plt.rcParams.update({"font.size": font})
    plt.xticks(new_kp, new_labels)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()

    if savefig:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()
    return info
