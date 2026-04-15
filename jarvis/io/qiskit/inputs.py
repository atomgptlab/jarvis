"""Module to solve Hermitian Matrix and predict bandstructures.

Migrated to Qiskit >= 1.2 / 2.x + qiskit-algorithms >= 0.3.

Reference: https://doi.org/10.1088/1361-648X/ac1154

Install:
    pip install "qiskit>=1.2" qiskit-aer qiskit-algorithms
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


def _get_estimator(backend="statevector_simulator", seed=50):
    """Create the appropriate V2 Estimator for the requested backend.

    Parameters
    ----------
    backend : str
        One of:
        - "statevector_simulator" : exact statevector (no noise, no shots)
        - "aer_simulator"        : Aer default (automatic method selection)
        - "aer_simulator_statevector" : Aer with statevector method
        - "aer_simulator_density_matrix" : Aer with density matrix method
        - "aer_simulator_mps"   : Aer with matrix product state method
        Any string starting with "aer" will use
        qiskit_aer.primitives.EstimatorV2.
        For IBM hardware, pass the backend name (requires qiskit-ibm-runtime).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    estimator : BaseEstimatorV2
        A V2-compatible estimator instance.
    """
    if backend == "statevector_simulator":
        # Exact simulation via qiskit built-in (no dependencies beyond qiskit)
        from qiskit.primitives import StatevectorEstimator

        return StatevectorEstimator(seed=seed)

    elif backend.startswith("aer"):
        # Aer-backed simulation: supports noise models, various methods
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import EstimatorV2 as AerEstimator

        # Map friendly names to Aer simulation methods
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
        # Assume IBM hardware backend name
        try:
            from qiskit_ibm_runtime import (
                QiskitRuntimeService,
                EstimatorV2 as RuntimeEstimator,
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


# Available backends for the API/frontend to enumerate
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
    """Decompose Hermitian matrix into Pauli basis.

    Uses SparsePauliOp.from_operator() which replaces the manual
    opflow-based decomposition from Qiskit 0.x.
    """
    return SparsePauliOp.from_operator(Operator(H)).simplify()


class HermitianSolver(object):
    """Solve a Hermitian matrix using quantum algorithms."""

    def __init__(self, mat=[], verbose=False):
        """Initialize with a numpy Hermitian matrix."""
        N = int(np.ceil(np.log2(len(mat))))
        hk = np.zeros((2**N, 2**N), dtype="complex")
        hk[: mat.shape[0], : mat.shape[1]] = mat
        self.mat = hk
        self.verbose = verbose
        if not self.check_hermitian():
            raise ValueError("Only implemented for Hermitian matrix.")

    def n_qubits(self):
        """Get number of qubits required."""
        return int(np.log2(len(self.mat)))

    def check_hermitian(self):
        """Check if a matrix is Hermitian."""
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

        Parameters
        ----------
        backend : str
            Backend identifier. See _get_estimator() for options:
            "statevector_simulator", "aer_simulator",
            "aer_simulator_statevector", "aer_simulator_density_matrix",
            "aer_simulator_mps", or an IBM hardware backend name.
        var_form : QuantumCircuit, optional
            Ansatz circuit. Defaults to EfficientSU2.
        optimizer : Optimizer, optional
            Classical optimizer. Defaults to SLSQP.
        reps : int, optional
            Repetitions for default ansatz.
        mode : str
            "min_val" for ground state, "max_val" for highest eigenvalue.
        """
        seed = 50
        N = self.n_qubits()

        estimator = _get_estimator(backend=backend, seed=seed)

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

        vqe = VQE(estimator, var_form, optimizer)
        np.random.seed(seed)
        result = vqe.compute_minimum_eigenvalue(operator=Hamil_qop)
        en = result.eigenvalue

        if mode == "max_val":
            en = -1 * en

        return en, result, vqe

    def run_numpy(self):
        """Obtain eigenvalues and vecs using Numpy solvers."""
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
        )
        eigvals = [max_eigval]
        eigstates = [vqe_result.eigenstate]

        for r in range(len(tmp.mat) - 1):
            val, vqe_result, vqe = tmp.run_vqe(
                backend=backend,
                var_form=var_form,
                optimizer=optimizer,
                reps=reps,
            )
            outer_prod = np.outer(
                vqe_result.eigenstate, np.conj(vqe_result.eigenstate).T
            )
            tmp.mat = tmp.mat - (val - max_eigval) * outer_prod
            eigvals.append(val)
            eigstates.append(vqe_result.eigenstate)
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
        else:
            try:
                hk = get_hk_tb(w=w, k=i)
                HS = HermitianSolver(hk)
                vqe_vals, _ = HS.run_vqd(var_form=var_form, backend=backend)
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
        if ii == 0:
            plt.plot(i, "*", c="b", label="VQD")
        else:
            plt.plot(i, "*", c="b")

    for ii, i in enumerate(eigvals_np.T - ef):
        if ii == 0:
            plt.plot(i, c="g", label="Numpy")
        else:
            plt.plot(i, c="g")
    new_kp = []
    new_labels = []
    count = 0
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


def get_dos(
    w=[],
    grid=[2, 1, 1],
    proj=None,
    efermi=0.0,
    xrange=None,
    nenergy=100,
    sig=0.02,
    use_dask=True,
    filename="dos.png",
    savefig=True,
):
    """Get density of states."""
    nwan = int(np.ceil(np.log2(w.nwan))) ** 2
    kpoints = generate_kgrid(grid=grid)
    nk = len(kpoints)
    q_vals = np.zeros((nk, nwan), dtype=float)
    np_vals = np.zeros((nk, nwan), dtype=float)
    pvals = np.zeros((nk, nwan - 1), dtype=float)

    for i, k in enumerate(kpoints):
        hk = get_hk_tb(w=w, k=k)
        HS = HermitianSolver(hk)
        vqe_vals, _ = HS.run_vqd()
        n_vals, _ = HS.run_numpy()
        print("np_vals", n_vals, len(n_vals), np_vals.shape)
        print("vqe_vals", vqe_vals, len(vqe_vals), q_vals.shape)
        q_vals[i, :] = vqe_vals
        np_vals[i, :] = n_vals

    if xrange is None:
        vmin = np.min(q_vals[:])
        vmax = np.max(q_vals[:])
        vmin2 = vmin - (vmax - vmin) * 0.05
        vmax2 = vmax + (vmax - vmin) * 0.05
        xrange = [vmin2, vmax2]

    energies = np.arange(
        xrange[0],
        xrange[1] + 1e-5,
        (xrange[1] - xrange[0]) / float(nenergy),
    )
    dos = np.zeros(np.size(energies))
    pdos = np.zeros(np.size(energies))

    v = q_vals

    c = -0.5 / sig**2
    for i in range(np.size(energies)):
        arg = c * (v - energies[i]) ** 2
        dos[i] = np.sum(np.exp(arg))
        if proj is not None:
            pdos[i] = np.sum(np.exp(arg) * pvals)

    de = energies[1] - energies[0]
    dos = dos / sig / (2.0 * np.pi) ** 0.5 / float(nk)
    if proj is not None:
        pdos = pdos / sig / (2.0 * np.pi) ** 0.5 / float(nk)
    print("np.sum(dos) ", np.sum(dos * de))
    if proj is not None:
        print("np.sum(pdos) ", np.sum(pdos * de))
    plt.plot(energies, dos)
    if savefig:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()
    return energies, dos, pdos
