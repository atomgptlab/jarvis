# JARVIS-Tools

[![PyPI](https://badge.fury.io/py/jarvis-tools.svg)](https://pypi.org/project/jarvis-tools/)
[![conda-forge](https://anaconda.org/conda-forge/jarvis-tools/badges/version.svg)](https://anaconda.org/conda-forge/jarvis-tools)
[![GitHub tag](https://img.shields.io/github/v/tag/atomgptlab/jarvis-tools)](https://github.com/atomgptlab/jarvis-tools)
[![CI](https://github.com/atomgptlab/jarvis-tools/workflows/JARVIS-Tools%20github%20action/badge.svg)](https://github.com/atomgptlab/jarvis-tools)
[![Lint](https://github.com/atomgptlab/jarvis/workflows/JARVIS-Tools%20linting/badge.svg)](https://github.com/atomgptlab/jarvis-tools)
[![Coverage](https://img.shields.io/codecov/c/github/knc6/jarvis)](https://codecov.io/gh/knc6/jarvis)
[![Downloads](https://pepy.tech/badge/jarvis-tools)](https://pepy.tech/badge/jarvis-tools)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3903515.svg)](https://doi.org/10.5281/zenodo.3903515)
[![Docs](https://img.shields.io/badge/JARVIS-ToolsDocs-Green.svg)](https://atomgptlab.github.io/jarvis-tools/)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/atomgptlab/jarvis-tools-notebooks)

JARVIS-Tools is an open-access Python package for atomistic, data-driven
materials design. It provides building blocks for:

- setting up first-principles and classical simulations,
- analysis and informatics on the resulting data,
- plotting and visualization,
- building and querying materials databases,
- powering web interfaces.

It is the engine behind [NIST-JARVIS](https://jarvis.nist.gov) (Joint
Automated Repository for Various Integrated Simulations), an integrated
framework spanning density functional theory, classical
force-fields/molecular dynamics, and machine learning. The project is
part of the [Materials Genome Initiative at NIST](https://mgi.nist.gov/).

For background, see the JARVIS overview papers
([npj Comput. Mater. 2020](https://www.nature.com/articles/s41524-020-00440-1),
[Appl. Phys. Rev. 2023](https://pubs.aip.org/aip/apr/article/10/4/041302/2917416)),
the [full publication list](https://scholar.google.com/citations?user=3w6ej94AAAAJ),
and the [introductory video](https://www.youtube.com/watch?v=P0ZcHXOC6W0).

<p align="center">
   <a href="https://jarvis.nist.gov/"><img src="https://www.ctcms.nist.gov/~knc6/images/logo/jarvis-mission.png" alt="JARVIS mission" width="600"/></a>
</p>

---

## Capabilities

- **Simulation workflows** — pre/post-processing for VASP, Quantum
  ESPRESSO, Wien2k, BoltzTraP, Wannier90, LAMMPS, and ML/QC frameworks
  (scikit-learn, TensorFlow, LightGBM, PyTorch, DGL, Qiskit, Tequila,
  PennyLane).
- **Analysis tools** — atomic and electronic structure, space groups,
  diffraction, 2D/vdW systems, mechanical, optoelectronic, topological,
  solar-cell, thermoelectric, piezoelectric, dielectric, STM, phonons,
  dark-matter detection, Wannier tight-binding models, point defects,
  heterostructures, magnetic ordering, image and spectrum processing.
- **Database access** — download JARVIS datasets (DFT, FF, ML,
  WannierTB, Solar, STM) and external sets (Materials Project, OQMD,
  AFLOW). See the [datasets summary](https://atomgptlab.github.io/jarvis-tools/databases/).
- **Reproducibility** — fetch raw input/output files for entries in the
  JARVIS databases.
- **Machine learning** — descriptors, graphs, and curated datasets for
  model training.
- **HPC integration** — job submission for Torque/PBS and SLURM.

## Installation

We recommend an isolated conda environment. Install
[Miniconda](https://conda.io/miniconda.html), then:

```bash
conda create -n my_jarvis python=3.10 -y
conda activate my_jarvis
```

Then pick one of the following install methods.

**pip (recommended):**

```bash
pip install -U jarvis-tools
```

**conda-forge:**

```bash
conda install -c conda-forge jarvis-tools
```

**From source:**

```bash
git clone https://github.com/atomgptlab/jarvis-tools.git
cd jarvis-tools
pip install -e .
```

**Developer setup** (with the dev environment file and tests):

```bash
git clone https://github.com/atomgptlab/jarvis-tools.git
cd jarvis-tools
git checkout develop
conda env create -n my_jarvis -f environment.yml
conda activate my_jarvis
pip install -e .
pip install pytest coverage codecov
coverage run -m pytest
```

## Quick example

Build a silicon structure and compute its density:

```python
from jarvis.core.atoms import Atoms

box = [[2.715, 2.715, 0], [0, 2.715, 2.715], [2.715, 0, 2.715]]
coords = [[0, 0, 0], [0.25, 0.25, 0.25]]
elements = ["Si", "Si"]
si = Atoms(lattice_mat=box, coords=coords, elements=elements)
print(round(si.density, 2))  # 2.33
```

Download the JARVIS-DFT 3D dataset and write each structure as a POSCAR:

```python
from jarvis.core.atoms import Atoms
from jarvis.db.figshare import data
from jarvis.io.vasp.inputs import Poscar

dft_3d = data(dataset="dft_3d")
print(len(dft_3d))  # ~75993

for entry in dft_3d:
    atoms = Atoms.from_dict(entry["atoms"])
    Poscar(atoms).write_file(f"POSCAR-{entry['jid']}.vasp")
```

Pull electronic density-of-states data from the JARVIS-DFT web pages and
interpolate onto a common energy grid:

```python
import numpy as np
from jarvis.core.atoms import Atoms
from jarvis.core.spectrum import Spectrum
from jarvis.db.figshare import data
from jarvis.db.webpages import Webpage

energy_grid = np.arange(-5, 10, 0.05)
dft_3d = data(dataset="dft_3d")

for entry in dft_3d[:10]:
    try:
        edos = Webpage(jid=entry["jid"]).get_dft_electron_dos()
        ens = np.fromstring(edos["edos_energies"].strip("'"), sep=",")
        dos_up = np.fromstring(edos["total_edos_up"].strip("'"), sep=",")
        interp = Spectrum(x=ens, y=dos_up).get_interpolated_values(new_dist=energy_grid)
        Atoms.from_dict(entry["atoms"]).write_cif(f"{entry['jid']}.cif")
    except Exception as exc:
        print(f"skip {entry['jid']}: {exc}")
```

More examples:

- [Tutorials](https://atomgptlab.github.io/jarvis-tools/tutorials/)
- [Notebook gallery](https://github.com/JARVIS-Materials-Design/jarvis-tools-notebooks)
- [Reference test files](https://atomgptlab.github.io/jarvis-tools/jarvis/tests/testfiles)

## Citing

If JARVIS-Tools contributes to a publication, please cite:

> Choudhary, K. *et al.* The joint automated repository for various
> integrated simulations (JARVIS) for data-driven materials design.
> *npj Computational Materials* **6**, 173 (2020).
> <https://www.nature.com/articles/s41524-020-00440-1>

For a broader list, see the
[JARVIS publications on Google Scholar](https://scholar.google.com/citations?user=3w6ej94AAAAJ).

## Contributing

[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

See the [contribution guide](https://github.com/atomgptlab/jarvis-tools/blob/master/Contribution.rst)
and the [code of conduct](https://github.com/atomgptlab/jarvis-tools/blob/master/CODE_OF_CONDUCT.md).
Bug reports and feature requests go to
[GitHub issues](https://github.com/atomgptlab/jarvis-tools/issues);
direct correspondence: <kamal.choudhary@nist.gov>.

## Funding

Developed under the [NIST Materials Genome Initiative](https://www.nist.gov/mgi).

> Note: this repository was migrated from
> <https://github.com/usnistgov/jarvis> to
> <https://github.com/atomgptlab/jarvis-tools>.

## Module structure

```text
jarvis/
├── ai/                  # ML descriptors, models, uncertainty
│   ├── descriptors/     # CFID, Coulomb matrix, ...
│   ├── gcn/             # graph convolutional networks
│   ├── pkgs/            # scikit-learn, LightGBM wrappers
│   └── uncertainty/
├── analysis/            # property-specific analyses
│   ├── darkmatter/  defects/  diffraction/  elastic/
│   ├── interface/   magnetism/  periodic/  phonon/
│   ├── solarefficiency/  stm/  structure/
│   ├── thermodynamics/  topological/
├── core/                # Atoms, Composition, Lattice, Spectrum, ...
├── db/                  # Figshare downloads, REST API, web scraping
├── examples/            # runnable LAMMPS / VASP examples
├── io/                  # parsers/writers per code
│   ├── boltztrap/  calphad/  lammps/  pennylane/  phonopy/
│   ├── qe/  qiskit/  tequila/  vasp/  wannier/  wanniertools/  wien2k/
├── tasks/               # workflow drivers + queue submission
│   ├── boltztrap/  lammps/  phonopy/  vasp/  queue_jobs.py
└── tests/               # unit tests + reference files under testfiles/
```
