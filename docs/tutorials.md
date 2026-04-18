# Tutorials

A guided tour of the most common JARVIS-Tools workflows. For runnable
notebooks, see the
[AIMS 2024 workshop](https://github.com/usnistgov/aims2024_workshop)
and the
[jarvis-tools-notebooks gallery](https://github.com/JARVIS-Materials-Design/jarvis-tools-notebooks).

## Atomic structures

Atomic structures are the input to nearly every simulation in
JARVIS-Tools — DFT, molecular dynamics, Monte Carlo, atomistic graph
neural networks. A structure is defined by element types, fractional or
Cartesian coordinates, and a lattice matrix that sets the periodic
boundary conditions.

The example below builds a silicon primitive cell. The same pattern
applies to multi-component systems.

```python
from jarvis.core.atoms import Atoms

box = [[2.715, 2.715, 0], [0, 2.715, 2.715], [2.715, 0, 2.715]]
coords = [[0, 0, 0], [0.25, 0.25, 0.25]]
elements = ["Si", "Si"]

Si = Atoms(lattice_mat=box, coords=coords, elements=elements, cartesian=False)
print(Si)                 # POSCAR-style printout
Si.write_poscar("POSCAR.vasp")
Si.write_cif("Si.cif")
```

The `Atoms` class can also be loaded from `.cif`, `POSCAR`, `.xyz`,
`.pdb`, `.sdf`, or `.mol2` files, and written back out to any of those
formats.

For molecular systems, pad with vacuum (e.g. 50 Å in each direction):
`lattice_mat=[[50,0,0],[0,50,0],[0,0,50]]`. For free surfaces, add
vacuum along one crystallographic direction (typically z) while keeping
the in-plane lattice vectors intact.

```python
my_atoms = Atoms.from_poscar("POSCAR")
my_atoms.write_poscar("MyPOSCAR")
```

Once an `Atoms` object exists, common quantities are one attribute away:

```python
print("volume          ", Si.volume)
print("density (g/cm³) ", Si.density)
print("composition     ", Si.composition)
print("formula         ", Si.composition.reduced_formula)
print("space group     ", Si.spacegroup())
print("lattice (abc)   ", Si.lattice.abc, Si.lattice.angles)
print("packing fraction", Si.packing_fraction)
print("num atoms       ", Si.num_atoms)
print("center of mass  ", Si.get_center_of_mass())
print("atomic numbers  ", Si.atomic_numbers)
```

To round-trip through dicts (useful for serializing to JSON):

```python
d = Si.to_dict()
new_atoms = Atoms.from_dict(d)
```

To convert to/from other toolkits:

```python
pmg_struct = Si.pymatgen_converter()   # requires pymatgen
ase_atoms  = Si.ase_converter()        # requires ase
```

Supercells:

```python
supercell_1 = Si.make_supercell([2, 2, 2])
supercell_2 = Si.make_supercell_matrix([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
assert supercell_1.density == supercell_2.density
```

### Radial, angular, and dihedral distribution functions

`NeighborsAnalysis` computes radial (RDF), angular (ADF), and dihedral
(DDF) distribution functions. Different cutoffs limit how many neighbors
are considered for the angular and dihedral distributions; see the
module reference for details.

```python
from jarvis.analysis.structure.neighbors import NeighborsAnalysis
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

nb = NeighborsAnalysis(Si)
bins_rdf, rdf, _   = nb.get_rdf()           # global RDF
adfa, bins_a       = nb.ang_dist_first()    # ADF, first-neighbor cutoff
adfb, bins_b       = nb.ang_dist_second()   # ADF, second-neighbor cutoff
ddf,  bins_d       = nb.get_ddf()           # DDF, first-neighbor cutoff

grid = GridSpec(2, 2)
plt.rcParams.update({"font.size": 24})
plt.figure(figsize=(16, 14))

plt.subplot(grid[0, 0]); plt.title("(a) RDF")
plt.plot(bins_rdf, rdf); plt.xlabel(r"Distance ($\AA$)")

plt.subplot(grid[0, 1]); plt.title("(b) ADF-a")
plt.plot(bins_a[:-1], adfa); plt.xlabel(r"Angle ($^\circ$)")

plt.subplot(grid[1, 0]); plt.title("(c) ADF-b")
plt.plot(bins_b[:-1], adfb); plt.xlabel(r"Angle ($^\circ$)")

plt.subplot(grid[1, 1]); plt.title("(d) DDF")
plt.plot(bins_d[:-1], ddf); plt.xlabel(r"Angle ($^\circ$)")
plt.tight_layout()
```

### XRD patterns

Theoretical XRD patterns (2θ and d_hkl) using Cu-Kα radiation:

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from jarvis.analysis.diffraction.xrd import XRD

two_theta, d_hkl, intensity = XRD().simulate(atoms=Si)

grid = GridSpec(1, 2)
plt.rcParams.update({"font.size": 24})
plt.figure(figsize=(10, 5))

plt.subplot(grid[0])
plt.bar(two_theta, intensity)
plt.xlabel(r"2$\Theta$"); plt.ylabel("XRD intensity")

plt.subplot(grid[1])
plt.bar(two_theta, d_hkl)
plt.xlabel(r"d$_{hkl}$"); plt.ylabel("XRD intensity")
plt.tight_layout()
```

### Defects: vacancies, surfaces, and heterostructures

Real materials contain point defects (vacancies, interstitials,
substitutions), line defects (dislocations), surface defects (free
surfaces, grain boundaries, stacking faults, interfaces), and volume
defects (voids, pores). JARVIS-Tools generates several of these
automatically.

Vacancies at the unique Wyckoff sites:

```python
from jarvis.analysis.defects.vacancy import Vacancy

vacs = Vacancy(atoms=Si).generate_defects(enforce_c_size=10.0)
len(vacs), vacs[0].to_dict()["defect_structure"].num_atoms
# Si has only one symmetry-unique vacancy site.
```

Free surfaces:

```python
from jarvis.analysis.defects.surface import Surface

surface_111 = (
    Surface(atoms=Si, indices=[1, 1, 1], layers=3, vacuum=18)
    .make_surface()
    .center_around_origin()
)
print(surface_111)
```

All symmetry-distinct surfaces up to a given Miller index:

```python
from jarvis.analysis.structure.spacegroup import (
    Spacegroup3D,
    symmetrically_distinct_miller_indices,
)

spg = Spacegroup3D(atoms=Si)
cvn = spg.conventional_standard_structure
mills = symmetrically_distinct_miller_indices(max_index=3, cvn_atoms=cvn)
for hkl in mills:
    surf = Surface(atoms=Si, indices=hkl, layers=3, vacuum=18).make_surface()
    print("Index:", hkl)
    print(surf)
```

Film/substrate heterostructures via the Zur–McGill (ZSL) algorithm:

```python
from jarvis.analysis.interface.zur import make_interface
from jarvis.analysis.defects.surface import Surface

film      = Surface(atoms=Si, indices=[1, 1, 1], layers=3, vacuum=18).make_surface().center_around_origin()
substrate = Surface(atoms=Si, indices=[1, 1, 1], layers=3, vacuum=18).make_surface().center_around_origin()

interface = make_interface(film=film, subs=substrate)["interface"].center(vacuum=18)
print(interface)
```

## DFT calculations with VASP

The Vienna Ab initio Simulation Package (VASP) performs ab initio
quantum-mechanical calculations using either Vanderbilt pseudopotentials
or the projector augmented-wave method, with a plane-wave basis set.
See the [VASP manual](https://www.vasp.at/wiki/index.php/The_VASP_Manual)
for theory and runtime details.

A VASP run requires `INCAR`, `POSCAR`, `KPOINTS`, and `POTCAR` (plus
`vdw_kernel.bindat` for some calculations). For one-off jobs this is
straightforward; for thousands of materials with consistent
post-processing, JARVIS-Tools provides:

1. an `Atoms` representation in `jarvis.core.atoms`,
2. input-file generation in `jarvis.io.vasp.inputs`,
3. queue submission via `jarvis.tasks.vasp` and `jarvis.tasks.queue_jobs`,
4. output parsing in `jarvis.io.vasp.outputs`, and
5. XML/HTML generation in `jarvis.db.vasp_to_xml` (via XSLT for the
   web rendering).

A consolidated JSON file is then built from the per-material XML pages
for downstream data analytics and ML. The
[JARVIS-DFT database](https://jarvis.nist.gov/jarvisdft/) is produced
with this workflow.

Make sure `VASP_PSP_DIR` points at your pseudopotential directory,
typically in your `~/.bashrc`:

```bash
export VASP_PSP_DIR=/path/to/vasp_pseudopotentials
```

### A single calculation

```python
import os
from jarvis.tasks.vasp.vasp import VaspJob, write_vaspjob
from jarvis.io.vasp.inputs import Potcar, Incar, Poscar
from jarvis.core.kpoints import Kpoints3D
from jarvis.db.jsonutils import dumpjson

mat = Poscar.from_file("POSCAR")

incar = Incar(dict(
    PREC="Accurate",
    ISMEAR=0,
    SIGMA=0.01,
    IBRION=2,
    ISIF=3,
    GGA="BO",
    PARAM1=0.1833333333,
    PARAM2=0.2200000000,
    LUSE_VDW=".TRUE.",
    AGGAC=0.0000,
    EDIFF="1E-7",
    EDIFFG="-1E-3",
    NELM=400,
    ISPIN=2,
    LCHARG=".FALSE.",
    LVTOT=".FALSE.",
    LVHAR=".FALSE.",
    LWAVE=".FALSE.",
))

potcar = Potcar.from_atoms(mat.atoms)
kpoints = Kpoints3D().automatic_length_mesh(
    lattice_mat=mat.atoms.lattice_mat, length=20
)

job = VaspJob(
    poscar=mat,
    incar=incar,
    potcar=potcar,
    kpoints=kpoints,
    vasp_cmd="/path/to/vasp_std",
    copy_files=["/path/to/vdw_kernel.bindat"],
    jobname="MAIN-RELAX@JVASP-1002",
)

dumpjson(data=job.to_dict(), filename="job.json")
write_vaspjob(pyname="job.py", job_json="job.json")
```

`job.py` can now be run directly on a workstation, or submitted to a
PBS/SLURM cluster:

```python
import os
from jarvis.tasks.queue_jobs import Queue

job_line = "source activate my_jarvis\npython job.py"
Queue.pbs(
    job_line=job_line,
    jobname="TestJob",
    directory=os.getcwd(),
    submit_cmd=["qsub", "submit_job"],
)
```

### High-throughput calculations

`JobFactory` chains together a sequence of standard property
calculations (relaxation, band structure, optics, elastic constants,
…) for many structures.

```python
import os
from jarvis.tasks.vasp.vasp import JobFactory, GenericIncars, write_jobfact
from jarvis.io.vasp.inputs import Poscar
from jarvis.db.jsonutils import dumpjson
from jarvis.tasks.queue_jobs import Queue

structures = ["POSCAR-1.vasp", "POSCAR-2.vasp", "POSCAR-3.vasp"]

vasp_cmd   = "mpirun /path/to/vasp_std"
copy_files = ["/path/to/vdw_kernel.bindat"]
submit_cmd = ["qsub", "submit_job"]   # use ["sbatch", "submit_job"] for SLURM

steps = ["ENCUT", "KPLEN", "RELAX", "BANDSTRUCT", "OPTICS", "MBJOPTICS", "ELASTIC"]
incs  = GenericIncars().optb88vdw().incar.to_dict()

home = os.getcwd()
for poscar_file in structures:
    mat = Poscar.from_file(poscar_file)
    dir_name = poscar_file.split(".vasp")[0] + "_PBEBO"
    os.makedirs(dir_name, exist_ok=True)
    os.chdir(dir_name)

    job = JobFactory(
        vasp_cmd=vasp_cmd,
        poscar=mat,
        steps=steps,
        copy_files=copy_files,
        use_incar_dict=incs,
    )
    dumpjson(data=job.to_dict(), filename="job_fact.json")
    write_jobfact(
        pyname="job_fact.py",
        job_json="job_fact.json",
        input_arg="v.step_flow()",
    )

    job_line = "source activate my_jarvis\npython job_fact.py"
    Queue.pbs(
        job_line=job_line,
        jobname=poscar_file,
        walltime="24:00:00",
        cores=12,
        directory=os.getcwd(),
        submit_cmd=submit_cmd,
    )
    # SLURM equivalent:
    # Queue.slurm(job_line=job_line, jobname=poscar_file,
    #             directory=os.getcwd(), submit_cmd=["sbatch", "submit_job"])

    os.chdir(home)
```

Convert a finished calculation tree to JARVIS-API XML (and from there
to HTML via XSLT):

```python
from jarvis.db.vasp_to_xml import VaspToApiXmlSchema

VaspToApiXmlSchema(folder="jarvis/jarvis/examples/vasp/SiOptB88vdW").write_xml(
    filename="JVASP-1002.xml",
)
```

### Band structure and DOS

After the workflow above, the band structure and DOS come from the
`vasprun.xml` files in the `MAIN-BAND` and `MAIN-RELAX` folders
respectively.

```python
import matplotlib.pyplot as plt
from jarvis.io.vasp.outputs import Vasprun

vrun = Vasprun("vasprun.xml")
plt.rcParams.update({"font.size": 22})

# Band structure
vrun.get_bandstructure(kpoints_file_path="KPOINTS")

# DOS
energies, spin_up, spin_dn = vrun.total_dos
plt.plot(energies, spin_up, label="Spin up")
plt.plot(energies, spin_dn, label="Spin down")
plt.xlabel(r"$E - E_\mathrm{F}$ (eV)")
plt.ylabel("DOS (arb. units)")
plt.xlim(-4, 4)
plt.legend()
```

### Other VASP analyses

The following workflows are available but not yet documented in this
guide. Consult the corresponding modules under `jarvis.analysis` and
`jarvis.io.vasp.outputs` for usage:

- elastic constants
- STM / STEM image generation
- dielectric function and solar-cell efficiency
- electronic Wannier tight-binding models
- Fermi surfaces
- BoltzTraP transport properties
- heterostructures and interfaces
- IR / Raman spectra
- piezoelectric, dielectric, Born effective charge constants
- electric-field gradients
- surface work functions
- 2D-material exfoliation energies

## Classical MD with LAMMPS

JARVIS-Tools wraps LAMMPS through `LammpsJob`, which takes an `Atoms`
object, a pair-style and coefficient, and a control file
(`*.mod` template).

### Run a calculation

```python
from jarvis.tasks.lammps.lammps import LammpsJob, JobFactory
from jarvis.core.atoms import Atoms
from jarvis.db.figshare import get_jid_data
from jarvis.analysis.structure.spacegroup import Spacegroup3D

# Pull aluminum FCC from JARVIS-DFT
atoms = Atoms.from_dict(get_jid_data(jid="JVASP-816", dataset="dft_3d")["atoms"])
cvn_atoms = Spacegroup3D(atoms).conventional_standard_structure

ff  = "/users/knc6/Software/LAMMPS/lammps-master/potentials/Al_zhou.eam.alloy"
mod = "/users/knc6/Software/Devs/jarvis/jarvis/tasks/lammps/templates/inelast.mod"
cmd = "/users/knc6/Software/LAMMPS/lammps-master/src/lmp_serial<in.main>out"

parameters = {
    "pair_style":   "eam/alloy",
    "pair_coeff":   ff,
    "atom_style":   "charge",
    "control_file": mod,
}

LammpsJob(
    atoms=cvn_atoms, parameters=parameters, lammps_cmd=cmd, jobname="Test",
).runjob()

# High-throughput equivalent
job_fact = JobFactory(pair_style="eam/alloy", name="my_first_lammps_run")
job_fact.all_props_eam_alloy(atoms=cvn_atoms, ff_path=ff, lammps_cmd=cmd)
```

### Parse and export

```python
from jarvis.io.lammps.outputs import parse_material_calculation_folder
from jarvis.db.lammps_to_xml import write_xml

data = parse_material_calculation_folder(
    "/home/users/knc6/Software/jarvis/jarvis/examples/lammps/Aleam"
)
write_xml(data=data, filename="JLMP-123.xml")
```

The XML is converted to HTML via XSLT for web display.

## DFT calculations with Quantum ESPRESSO

Quantum ESPRESSO is a free, GPL-licensed suite for first-principles
electronic-structure calculations using DFT, plane-wave basis sets, and
pseudopotentials.

### A single calculation

```python
from jarvis.core.atoms import Atoms
from jarvis.core.kpoints import Kpoints3D
from jarvis.io.qe.inputs import QEinfile

box = [[2.715, 2.715, 0], [0, 2.715, 2.715], [2.715, 0, 2.715]]
coords = [[0, 0, 0], [0.25, 0.25, 0.25]]
elements = ["Si", "Si"]
Si = Atoms(lattice_mat=box, coords=coords, elements=elements)

# SCF input
kp = Kpoints3D().automatic_length_mesh(lattice_mat=Si.lattice_mat, length=20)
qe = QEinfile(Si, kp)
qe.write_file()                  # default filename

# Band-structure input on a high-symmetry k-path
kp_path = Kpoints3D().kpath(atoms=Si)
QEinfile(Si, kp_path).write_file("qe.in2")

print(qe.atomic_species_string())
print(qe.atomic_cell_params())
print("nat =", qe.input_params["system_params"]["nat"])
```

Then run from the shell:

```bash
$PATH_TO_PWSCF/pw.x -i qe.in
```

## ML models with JARVIS-CFID (sklearn / LightGBM)

JARVIS-Tools supports two main routes to atomistic ML models:

- **JARVIS-CFID** (Classical Force-field Inspired Descriptors) —
  hand-crafted descriptors usable with classical ML libraries. See
  `jarvis.ai.descriptors.cfid`.
- **JARVIS-ALIGNN** (Atomistic Line Graph Neural Network) — graph
  neural networks for property prediction, distributed as a
  separate `alignn` package.

This section covers CFID for both formula-only and formula+structure
inputs.

### Chemical-formula-only models

For each chemical formula, CFID produces 438 descriptors (average
electronegativity, average boiling point, etc.). A toy training set:

```python
import numpy as np
from jarvis.ai.descriptors.cfid import get_chem_only_descriptors
from jarvis.ai.pkgs.lgbm.regression import regression

my_data = [
    ["CoAl",                1], ["CoNi",              2], ["CoNb2Ni5",       3],
    ["Co1.2Al2.3NiRe2",     4], ["Co",                5], ["CoAlTi",         1],
    ["CoNiTi",              2], ["CoNb2Ni5Ti",        3], ["Co1.2Al2.3NiRe2Ti", 4],
    ["CoTi",                5], ["CoAlFe",            1], ["CoNiFe",         2],
    ["CoNb2Ni5Fe",          3], ["Co1.2Al2.3NiRe2Fe", 4], ["CoFe",           5],
]

X, Y, IDs = [], [], []
for i, (formula, target) in enumerate(my_data):
    X.append(get_chem_only_descriptors(formula))
    Y.append(target)
    IDs.append(i)

X   = np.array(X)
Y   = np.array(Y).reshape(-1, 1)
IDs = np.array(IDs)
```

Now train a LightGBM regressor through the JARVIS-Tools wrapper, which
also handles feature pre-processing:

```python
config = {"n_estimators": 5, "learning_rate": 0.01, "num_leaves": 2}
info = regression(X=X, Y=Y, jid=IDs, feature_importance=False, config=config)

print(
    "r2  =", info["reg_scores"]["r2"],
    "MAE =", info["reg_scores"]["mae"],
    "RMSE=", info["reg_scores"]["rmse"],
)
```

### Formula + structure regression

For 60,000 materials, CFID produces a 1,557-dimensional descriptor per
material (438 chemical + structural and charge descriptors), giving a
60,000 × 1,557 input matrix. Pair this with a target — for example
formation energies from JARVIS-DFT — and train any regressor.

We find that gradient-boosted decision trees (LightGBM in particular)
work especially well with CFID. JARVIS-Tools ships wrappers for
scikit-learn, TensorFlow, PyTorch, and LightGBM.

```python
from jarvis.ai.pkgs.utils import get_ml_data, regr_scores
import lightgbm as lgb
from sklearn.model_selection import train_test_split

# Default target: formation energy for 3D materials.
X, y, jid = get_ml_data()

X_train, X_test, y_train, y_test, _, _ = train_test_split(
    X, y, jid, random_state=1, test_size=0.1,
)

lgbm = lgb.LGBMRegressor(
    device="gpu",
    n_estimators=1170,
    learning_rate=0.15375236057119931,
    num_leaves=273,
)
lgbm.fit(X_train, y_train)
print("MAE =", regr_scores(y_test, lgbm.predict(X_test))["mae"])
```

## ML models with JARVIS-ALIGNN (PyTorch)

ALIGNN training and inference live in the standalone
[`alignn`](https://github.com/usnistgov/alignn) package; see its
documentation for regression and classification workflows.

## Quantum computing with Qiskit / Tequila / PennyLane

Quantum chemistry — and, in JARVIS, condensed-matter electronic-structure
problems via Wannier tight-binding Hamiltonians (WTBH) — is one of the
most promising applications of quantum computers. The Variational
Quantum Eigensolver (VQE) is a standard hybrid quantum-classical
algorithm for ground-state estimation: a parameterized quantum circuit
("ansatz") prepares a trial state, the quantum device measures the
expectation value of the Hamiltonian, and a classical optimizer updates
the circuit parameters to minimize the energy.

This section runs VQE on a WTBH from the JARVIS-WTBH database. WTBHs can
be generated by several DFT codes; here we use the JARVIS-WTBH dataset
directly.

### Build a circuit and run VQE

A handful of standard ansatz templates live in `jarvis.core.circuits`.
The example below uses circuit-6 (EfficientSU2) to predict electronic
energy levels of FCC aluminum at the X-point in the Brillouin zone.

```python
from qiskit import Aer
from jarvis.db.figshare import get_wann_electron, get_hk_tb
from jarvis.io.qiskit.inputs import HermitianSolver
from jarvis.core.circuits import QuantumCircuitLibrary

backend = Aer.get_backend("statevector_simulator")

# Aluminum, JARVIS-ID JVASP-816
wtbh, Ef, atoms = get_wann_electron("JVASP-816")
hk = get_hk_tb(w=wtbh, k=[0.5, 0.0, 0.5])     # X-point

solver = HermitianSolver(hk)
circuit = QuantumCircuitLibrary(n_qubits=solver.n_qubits()).circuit6()

en, vqe_result, vqe = solver.run_vqe(var_form=circuit, backend=backend)
vals, vecs = solver.run_numpy()

print("Classical, VQE (eV):", vals[0] - Ef, en - Ef)
print("Circuit:")
print(circuit)
```

### Run on a real quantum device

Replace the simulator backend with an IBM Quantum device:

```python
import qiskit
from qiskit import IBMQ

token = "<your IBM Quantum API token>"
qiskit.IBMQ.save_account(token)
provider = IBMQ.load_account()
backend  = provider.get_backend("ibmq_5_yorktown")
```

The job is queued; results are returned when execution finishes. Wait
times depend on device load.
