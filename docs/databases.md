# Databases

JARVIS-Tools provides one-line access to a large collection of curated
materials datasets — JARVIS-DFT, JARVIS-FF, JARVIS-ML, and mirrors of
external sets such as Materials Project, OQMD, AFLOW, Alexandria, the
Open Catalyst Project, QM9, and others. Most are hosted on Figshare and
fetched lazily into a local cache the first time they are requested.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/Analyzing_data_in_the_JARVIS_DFT_dataset.ipynb)
[![Open in SLMat](https://img.shields.io/badge/Open-SLMat-blue)](https://deepmaterials.github.io/slmat/lab?fromURL=https://raw.githubusercontent.com/deepmaterials/slmat/main/content/Database_analysis.ipynb)

## Quickstart

Every dataset listed below — except `stm`, `wtbh_electron`, and
`wtbh_phonon`, which have dedicated helpers in `jarvis.db.figshare` —
can be loaded with the same call:

```python
from jarvis.db.figshare import data

d = data("dft_3d")        # pick any dataset name from the tables below
print(len(d))             # number of records
print(d[0].keys())        # available fields per record
```

Each record is a plain Python dict. Atomic structures are stored under
the `"atoms"` key as a serialized `Atoms` dict:

```python
from jarvis.core.atoms import Atoms

a = Atoms.from_dict(d[0]["atoms"])
print(a)                  # POSCAR-style printout, viewable in VESTA
```

Convert any dataset into a pandas `DataFrame` for filtering and joins:

```python
import pandas as pd

df = pd.DataFrame(d)
df.head()
```

---

## JARVIS databases

| Name | Records | Description |
|------|---------|-------------|
| [`dft_3d`](https://doi.org/10.6084/m9.figshare.6815699) | 75,993 | 3D materials in JARVIS-DFT, OptB88vdW + TBmBJ |
| [`dft_2d`](https://doi.org/10.6084/m9.figshare.6815705) | 1,109 | 2D materials in JARVIS-DFT, OptB88vdW |
| [`dft_3d_2021`](https://doi.org/10.6084/m9.figshare.6815699) | 55,723 | 3D materials, 2021 snapshot |
| [`dft_2d_2021`](https://doi.org/10.6084/m9.figshare.6815705) | 1,079 | 2D materials, 2021 snapshot |
| [`cfid_3d`](https://doi.org/10.6084/m9.figshare.6815699) | 55,723 | JARVIS-DFT 3D + CFID descriptors |
| [`jff`](https://doi.org/10.6084/m9.figshare.14213522) | 2,538 | JARVIS-FF: classical force-field properties |
| [`alignn_ff_db`](https://doi.org/10.6084/m9.figshare.21667874) | 307,113 | ALIGNN-FF training set: energies, forces, stresses |
| [`edos_pdos`](https://doi.org/10.6084/m9.figshare.14745327) | 48,469 | Normalized electron + phonon DOS, fixed-bin |
| [`qe_tb`](https://doi.org/10.6084/m9.figshare.15127788) | 829,574 | JARVIS-QETB three-body tight-binding properties |
| [`supercon_3d`](https://doi.org/10.6084/m9.figshare.21370572) | 1,058 | 3D superconductor DFT dataset |
| [`supercon_2d`](https://doi.org/10.6084/m9.figshare.21370572) | 161 | 2D superconductor DFT dataset |
| [`vacancydb`](https://doi.org/10.6084/m9.figshare.23000573) | 464 | Vacancy formation energies |
| [`surfacedb`](https://doi.org/10.6084/m9.figshare.25832614) | 607 | Surface properties |
| [`interfacedb`](https://doi.org/10.6084/m9.figshare.25832614) | 593 | Interface properties |
| [`ramandb`](https://doi.org/10.6084/m9.figshare.29458907) | 5,000 | Raman spectra |
| [`raw_files`](https://doi.org/10.6084/m9.figshare.13154159) | 144,895 | Figshare links to raw VASP outputs for JARVIS-DFT |
| `stm` | 1,132 | 2D-material STM images (JARVIS-STM) |
| `wtbh_electron` | 1,440 | Wannier tight-binding Hamiltonians, electrons + SOC (keyword `WANN`) |
| `wtbh_phonon` | 15,502 | Wannier tight-binding Hamiltonians, phonons at Γ (keyword `FD-ELAST`) |

## Alexandria

| Name | Records | Description |
|------|---------|-------------|
| [`alex_pbe_hull`](https://doi.org/10.6084/m9.figshare.27174897) | 116k | Convex-hull-stable materials, PBE |
| [`alex_pbe_3d_all`](https://doi.org/10.6084/m9.figshare.27174897) | 5M | All 3D materials, PBE |
| [`alex_pbe_2d_all`](https://doi.org/10.6084/m9.figshare.27174897) | 200k | All 2D materials, PBE |
| [`alex_pbe_1d_all`](https://doi.org/10.6084/m9.figshare.27174897) | 100k | All 1D materials, PBE |
| [`alex_scan_3d_all`](https://doi.org/10.6084/m9.figshare.27174897) | 500k | All 3D materials, SCAN |
| [`alex_pbesol_3d_all`](https://doi.org/10.6084/m9.figshare.27174897) | 500k | All 3D materials, PBEsol |
| [`alex_supercon`](https://doi.org/10.6084/m9.figshare.27174897) | 8,253 | Superconductor subset |

## RRUFF (experimental spectra)

| Name | Records | Description |
|------|---------|-------------|
| [`rruff_powder_xrd`](https://doi.org/10.6084/m9.figshare.31817977) | 1,362 | Powder XRD |
| [`rruff_raman_excellent`](https://doi.org/10.6084/m9.figshare.31817977) | 7,688 | Raman spectra (excellent-quality subset) |
| [`rruff_ir`](https://doi.org/10.6084/m9.figshare.31817977) | 824 | IR spectra |

## Materials Project mirrors

| Name | Records | Description |
|------|---------|-------------|
| `mp_3d_2020` | 127k | CFID descriptors for MP (2020 snapshot) |
| [`mp_3d`](https://doi.org/10.6084/m9.figshare.13054247) | 84k | CFID descriptors for 84k MP entries |
| [`megnet`](https://doi.org/10.6084/m9.figshare.14177630) | 69,239 | Formation energies and band gaps (MEGNet 2018) |
| [`megnet2`](https://doi.org/10.6084/m9.figshare.14745435) | 133k | 133k MP entries with formation energies |
| [`m3gnet_mpf`](https://doi.org/10.6084/m9.figshare.23267852) | 168k | Energies, forces, stresses (M3GNet) |
| [`m3gnet_mpf_1.5mil`](https://doi.org/10.6084/m9.figshare.23267852) | 1.5M | Extended M3GNet training set |

## OQMD

| Name | Records | Description |
|------|---------|-------------|
| [`oqmd_3d`](https://doi.org/10.6084/m9.figshare.13055333) | 460k | CFID descriptors for OQMD |
| [`oqmd_3d_no_cfid`](https://doi.org/10.6084/m9.figshare.14206169) | 817,636 | Formation energies and band gaps |

## Open Catalyst Project

| Name | Records | Description |
|------|---------|-------------|
| [`ocp_all`](https://doi.org/10.6084/m9.figshare.23250629) | 510,214 | Train (460,328) + val + test |
| [`ocp100k`](https://doi.org/10.6084/m9.figshare.23206193) | 149,886 | Train (100k) + val + test |
| [`ocp10k`](https://doi.org/10.6084/m9.figshare.22817633) | 59,886 | Train (10k) + val + test |

## Catalyst (AGRA, TinNet)

| Name | Records | Description |
|------|---------|-------------|
| [`AGRA_O`](https://doi.org/10.6084/m9.figshare.23909478) | 1,000 | AGRA O catalysts |
| [`AGRA_OH`](https://doi.org/10.6084/m9.figshare.23909478) | 875 | AGRA OH catalysts |
| [`AGRA_COOH`](https://doi.org/10.6084/m9.figshare.23909478) | 280 | AGRA COOH catalysts |
| [`AGRA_CHO`](https://doi.org/10.6084/m9.figshare.23909478) | 214 | AGRA CHO catalysts |
| [`AGRA_CO`](https://doi.org/10.6084/m9.figshare.23909478) | 193 | AGRA CO catalysts |
| [`tinnet_N`](https://doi.org/10.6084/m9.figshare.23225687) | 329 | TinNet N catalysts |
| [`tinnet_O`](https://doi.org/10.6084/m9.figshare.23254151) | 747 | TinNet O catalysts |
| [`tinnet_OH`](https://doi.org/10.6084/m9.figshare.23254154) | 748 | TinNet OH catalysts |

## QM9 and molecular

| Name | Records | Description |
|------|---------|-------------|
| `qm9_std_jctc` | 130,829 | QM9 (standardized) |
| [`qm9_dgl`](https://doi.org/10.6084/m9.figshare.14827584) | 130,829 | QM9 prepared for DGL |
| `qm9` | 134k | QM9 + CFID descriptors |
| `hopv` | 4,855 | HOPV15 photovoltaic molecules |
| [`pdbbind`](https://doi.org/10.6084/m9.figshare.14812038) | 11,189 | Bio-molecular complexes (PDBBind v2015) |
| `pdbbind_core` | 195 | PDBBind core set |
| [`cccbdb`](https://doi.org/10.6084/m9.figshare.26117998) | 1,333 | NIST CCCBDB computational chemistry data |

## MOFs

| Name | Records | Description |
|------|---------|-------------|
| [`qmof`](https://doi.org/10.6084/m9.figshare.14812044) | 20,425 | QMOF band gaps and total energies |
| [`hmof`](https://doi.org/10.6084/m9.figshare.15127758) | 137,651 | Hypothetical MOFs |

## 2D materials (external)

| Name | Records | Description |
|------|---------|-------------|
| `c2db` | 3,514 | C2DB properties |
| [`twod_matpd`](https://doi.org/10.6084/m9.figshare.14205083) | 6,351 | 2DMatPedia formation energies + band gaps |
| [`mxene275`](https://doi.org/10.6084/m9.figshare.23531523) | 275 | MXenes |

## Other

| Name | Records | Description |
|------|---------|-------------|
| [`aflow2`](https://doi.org/10.6084/m9.figshare.13215308) | 400k | AFLOW |
| [`cod`](https://doi.org/10.6084/m9.figshare.14912820.v1) | 431,778 | Crystallography Open Database |
| [`cod_200`](https://doi.org/10.6084/m9.figshare.14912820.v1) | 237k | COD (2025 snapshot) |
| [`snumat`](https://doi.org/10.6084/m9.figshare.21713885) | 10,481 | Hybrid-functional band gaps |
| [`polymer_genome`](https://doi.org/10.6084/m9.figshare.14213603) | 1,073 | Crystalline polymer band gaps + dielectric constants |
| [`omdb`](https://doi.org/10.6084/m9.figshare.14812050) | 12,500 | OMDB organic-polymer band gaps |
| [`halide_peroskites`](https://doi.org/10.6084/m9.figshare.25256236) | 229 | Halide perovskites |
| [`supercon_chem`](https://doi.org/10.6084/m9.figshare.22975787) | 16,414 | Superconductor chemical formulae |
| [`mag2d_chem`](https://doi.org/10.6084/m9.figshare.22976285) | 226 | Magnetic 2D-material chemical formulae |
| [`ssub`](https://doi.org/10.6084/m9.figshare.22583677) | 1,726 | SSUB formation energies |
| [`mlearn`](https://doi.org/10.6084/m9.figshare.22721047) | 1,730 | ML force-field per-element datasets |
| [`foundry_ml_exp_bandgaps`](https://doi.org/10.6084/m9.figshare.22814318) | 2,069 | Experimental band gaps via Foundry-ML |

## Text and NLP

| Name | Records | Description |
|------|---------|-------------|
| [`arXiv`](https://doi.org/10.6084/m9.figshare.14211860) | 1,796,911 | arXiv title + abstract + ID |
| [`arxiv_summary`](https://doi.org/10.6084/m9.figshare.22817651) | 137,927 | arXiv summaries (cond-mat) |
| [`cord19`](https://doi.org/10.6084/m9.figshare.14211857) | 223k | CORD-19 COVID-19 research articles |
