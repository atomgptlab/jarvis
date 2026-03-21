# Databases

## [FigShare](https://figshare.com/authors/Kamal_Choudhary/4445539) based databases

[![Open in Colab]](https://colab.research.google.com/github/knc6/jarvis-tools-notebooks/blob/master/jarvis-tools-notebooks/Analyzing_data_in_the_JARVIS_DFT_dataset.ipynb)
[![Open in SLMat]](https://deepmaterials.github.io/slmat/lab?fromURL=https://raw.githubusercontent.com/deepmaterials/slmat/main/content/Database_analysis.ipynb)

### JARVIS databases

| Database name     | Number of data-points | Description                                                                                              |
|-------------------|-----------------------|----------------------------------------------------------------------------------------------------------|
| `dft_3d`          | 75993                 | Various 3D materials properties in JARVIS-DFT database computed with OptB88vdW and TBmBJ methods        |
| `dft_2d`          | 1109                  | Various 2D materials properties in JARVIS-DFT database computed with OptB88vdW                           |
| `dft_3d_2021`     | 55723                 | Various 3D materials properties in JARVIS-DFT database computed with OptB88vdW and TBmBJ methods (2021 version) |
| `dft_2d_2021`     | 1079                  | Various 2D materials properties in JARVIS-DFT database computed with OptB88vdW (2021 version)            |
| `cfid_3d`         | 55723                 | Various 3D materials properties in JARVIS-DFT database computed with OptB88vdW and TBmBJ methods with CFID |
| `jff`             | 2538                  | Various 3D materials properties in JARVIS-FF database computed with several force-fields                 |
| `alignn_ff_db`    | 307113                | Energy per atom, forces and stresses for ALIGNN-FF training for 75k materials                            |
| `edos_pdos`       | 48469                 | Normalized electron and phonon density of states with interpolated values and fixed number of bins        |
| `qe_tb`           | 829574                | Various 3D materials properties in JARVIS-QETB database                                                 |
| `supercon_3d`     | 1058                  | 3D superconductor DFT dataset                                                                           |
| `supercon_2d`     | 161                   | 2D superconductor DFT dataset                                                                           |
| `vacancydb`       | 464                   | Vacancy formation energy dataset                                                                         |
| `surfacedb`       | 607                   | Surface property dataset                                                                                 |
| `interfacedb`     | 593                   | Interface property dataset                                                                               |
| `ramandb`         | 5000                  | Raman spectra dataset                                                                                    |
| `raw_files`       | 144895                | Figshare links to download raw calculations VASP files from JARVIS-DFT                                   |
| `stm`             | 1132                  | 2D materials STM images in JARVIS-STM database                                                           |
| `wtbh_electron`   | 1440                  | 3D and 2D materials Wannier tight-binding Hamiltonian database for electrons with spin-orbit coupling in JARVIS-WTB (Keyword: 'WANN') |
| `wtbh_phonon`     | 15502                 | 3D and 2D materials Wannier tight-binding Hamiltonian for phonons at Gamma with finite difference (Keyword: FD-ELAST) |

### Alexandria databases

| Database name        | Number of data-points | Description                                                    |
|----------------------|-----------------------|----------------------------------------------------------------|
| `alex_pbe_hull`      | 116k                  | Alexandria DB convex hull stable materials with PBE functional |
| `alex_pbe_3d_all`    | 5 million             | Alexandria DB all 3D materials with PBE                        |
| `alex_pbe_2d_all`    | 200k                  | Alexandria DB all 2D materials with PBE                        |
| `alex_pbe_1d_all`    | 100k                  | Alexandria DB all 1D materials with PBE                        |
| `alex_scan_3d_all`   | 500k                  | Alexandria DB all 3D materials with SCAN                       |
| `alex_pbesol_3d_all` | 500k                  | Alexandria DB all 3D materials with PBEsol                     |
| `alex_supercon`      | 8253                  | Alexandria superconductor database                             |

### RRUFF databases

| Database name          | Number of data-points | Description                  |
|------------------------|-----------------------|------------------------------|
| `rruff_powder_xrd`     | 1362                  | RRUFF powder XRD dataset     |
| `rruff_raman_excellent`| 7688                  | RRUFF Raman spectra dataset  |
| `rruff_ir`             | 824                   | RRUFF IR spectra dataset     |

### Materials Project databases

| Database name     | Number of data-points | Description                                                                                              |
|-------------------|-----------------------|----------------------------------------------------------------------------------------------------------|
| `mp_3d_2020`      | 127k                  | CFID descriptors for materials project (2020)                                                            |
| `mp_3d`           | 84k                   | CFID descriptors for 84k materials project                                                               |
| `megnet`          | 69239                 | Formation energy and bandgaps of 3D materials properties in Materials project database as on 2018, used in megnet |
| `megnet2`         | 133k                  | 133k materials and their formation energy in MP                                                          |
| `m3gnet_mpf`      | 168k                  | 168k structures and their energy, forces and stresses in MP                                              |
| `m3gnet_mpf_1.5mil` | 1.5 million        | 1.5 million structures and their energy, forces and stresses in MP                                       |

### OQMD databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `oqmd_3d`         | 460k                  | CFID descriptors for 460k materials in OQMD                    |
| `oqmd_3d_no_cfid` | 817636                | Formation energies and bandgaps of 3D materials from OQMD database |

### Open Catalyst databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `ocp_all`         | 510214                | Open Catalyst 460328 training, rest validation and test dataset |
| `ocp100k`         | 149886                | Open Catalyst 100000 training, rest validation and test dataset |
| `ocp10k`          | 59886                 | Open Catalyst 10000 training, rest validation and test dataset  |

### Catalyst databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `AGRA_O`          | 1000                  | AGRA Oxygen catalyst dataset                                   |
| `AGRA_OH`         | 875                   | AGRA OH catalyst dataset                                       |
| `AGRA_COOH`       | 280                   | AGRA COOH catalyst dataset                                     |
| `AGRA_CHO`        | 214                   | AGRA CHO catalyst dataset                                      |
| `AGRA_CO`         | 193                   | AGRA CO catalyst dataset                                       |
| `tinnet_N`        | 329                   | TinNet Nitrogen catalyst dataset                               |
| `tinnet_O`        | 747                   | TinNet Oxygen catalyst dataset                                 |
| `tinnet_OH`       | 748                   | TinNet OH group catalyst dataset                               |

### QM9 and molecular databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `qm9_std_jctc`    | 130829                | Various properties of molecules in QM9 database (standardized) |
| `qm9_dgl`         | 130829                | Various properties of molecules in QM9 dgl database            |
| `qm9`             | 134k                  | Various properties of molecules in QM9 database with CFID      |
| `hopv`            | 4855                  | Various properties of molecules in HOPV15 dataset              |
| `pdbbind`         | 11189                 | Bio-molecular complexes database from PDBBind v2015            |
| `pdbbind_core`    | 195                   | Bio-molecular complexes database from PDBBind core             |
| `cccbdb`          | 1333                  | NIST CCCBDB computational chemistry dataset                    |

### MOF databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `qmof`            | 20425                 | Bandgaps and total energies of metal organic frameworks in QMOF database |
| `hmof`            | 137651                | Hypothetical MOF database                                      |

### 2D materials databases (external)

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `c2db`            | 3514                  | Various properties in C2DB database                            |
| `twod_matpd`      | 6351                  | Formation energy and bandgaps of 2D materials properties in 2DMatPedia database |
| `mxene275`        | 275                   | MXene dataset                                                  |

### Other materials databases

| Database name               | Number of data-points | Description                                                    |
|-----------------------------|-----------------------|----------------------------------------------------------------|
| `aflow2`                    | 400k                  | AFLOW dataset                                                  |
| `cod`                       | 431778                | Atomic structures from crystallographic open database          |
| `snumat`                    | 10481                 | Bandgaps with hybrid functional                                |
| `polymer_genome`            | 1073                  | Electronic bandgap and dielectric constants of crystalline polymers in polymer genome database |
| `omdb`                      | 12500                 | Bandgaps for organic polymers in OMDB database                 |
| `halide_peroskites`         | 229                   | Halide perovskite dataset                                      |
| `supercon_chem`             | 16414                 | Superconductor chemical formula dataset                        |
| `mag2d_chem`                | 226                   | Magnetic 2D materials chemical formula dataset                 |
| `ssub`                      | 1726                  | SSUB formation energy for chemical formula dataset             |
| `mlearn`                    | 1730                  | Machine learning force-field for elements datasets             |
| `foundry_ml_exp_bandgaps`   | 2069                  | Foundry ML experimental bandgaps dataset                       |

### Text and NLP databases

| Database name     | Number of data-points | Description                                                    |
|-------------------|-----------------------|----------------------------------------------------------------|
| `arXiv`           | 1796911               | arXiv dataset 1.8 million title, abstract and id dataset       |
| `arxiv_summary`   | 137927                | arXiv summary dataset (cond-mat)                               |
| `cord19`          | 223k                  | CORD-19 COVID-19 research articles dataset                     |


All these datasets can be obtained using jarvis-tools as follows,
exception to `stm`, `wtbh_electron`, `wtbh_phonon` which have their own
modules in `jarvis.db.figshare`:

``` python
from jarvis.db.figshare import data
d = data('dft_3d') #choose a name of dataset from above
# See available keys
print (d[0].keys())
# Dataset size
print(len(d))

# Visualize an atoms object
from jarvis.core.atoms import Atoms
a = Atoms.from_dict(d[0]['atoms'])
#You can visualize this in VESTA or other similar packages
print(a)

# If pandas framework needed
import pandas as pd
df = pd.DataFrame(d)
print(df)
```

[Open in SLMat]: https://img.shields.io/badge/Open-SLMat-blue

[Open in Colab]: https://colab.research.google.com/assets/colab-badge.svg
