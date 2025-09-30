# AFMTools Documentation

> **Note:** This is **NOT** the official AFMTools release. This repository contains enhanced documentation for the AFMTools suite.
>
> **For the official AFMTools software release, please visit the Wang Group website.**

Comprehensive documentation for the Adaptive Force Matching (AFM) Tools suite - a collection of scripts and utilities for quantum mechanical/molecular mechanical (QM/MM) simulations, force field development, and molecular dynamics workflows.

## Overview

AFMTools is a sophisticated toolkit designed for multi-scale molecular simulations, combining quantum mechanical calculations with classical molecular dynamics. This documentation project provides detailed, user-friendly guides for all AFMTools scripts across five major categories:

- **QM/MM Selection and Preparation** (`scr_QMMM_select/`)
- **QM Input File Generation** (`scr_QMMM_inp/`)
- **Force Processing and Analysis** (`scr_ref/`)
- **Force Field Parameter Conversion** (`scr_off2ff/`)
- **Topology File Generation** (`scr_off2top/`)

## Documentation Files

### Core Documentation

| File | Description |
|------|-------------|
| [`scr_QMMM_select_documentation.md`](scr_QMMM_select_documentation.md) | QM/MM atom selection and molecular marking tools |
| [`scr_QMMM_inp_documentation.md`](scr_QMMM_inp_documentation.md) | QM input file generation for Gaussian, Molpro, GAMESS, ORCA, PQS |
| [`scr_ref_documentation.md`](scr_ref_documentation.md) | Reference file (.ref) processing, force extraction, and analysis |
| [`scr_off2ff_documentation.md`](scr_off2ff_documentation.md) | OFF to FF force field parameter conversion |
| [`scr_off2top_documentation.md`](scr_off2top_documentation.md) | OFF to topology file conversion for MD simulations |

### Enhanced Scripts

The following scripts have been enhanced with comprehensive help functions:

- **`scr_off2ff/ff_gen_charge_constr`** - Generate charge constraint equations for force field fitting with CRYOFF

## Key Features

### QM/MM Selection Tools (`scr_QMMM_select/`)
- Convert between GROMACS `.gro` and `.pxyz` formats
- Mark and select atoms/molecules based on distance, proximity, and isolation criteria
- Create QM/MM partitions with buffer regions
- Recenter and sort molecular systems
- Visualization preparation tools

### QM Input Generation (`scr_QMMM_inp/`)
- Support for major QM packages: Gaussian, Molpro, GAMESS, ORCA, PQS
- Template-based input file generation
- Geometry and charge lattice updates
- QM/MM point charge integration
- Software-specific format handling

### Force Processing (`scr_ref/`)
- Extract forces/gradients from QM program outputs
- Calculate D2/D3 dispersion corrections
- Interface with GROMACS and DL_POLY
- Net force and torque calculations
- M-site (virtual site) handling for advanced water models
- Comprehensive unit conversion utilities

### Force Field Conversion (`scr_off2ff/`)
- OFF library to FF parameter file conversion
- Protocol-driven parameter extraction
- Charge product processing and constraint generation
- Parameter selection based on distance, value, and charge criteria
- Integration with CRYOFF optimization workflows

### Topology Generation (`scr_off2top/`)
- OFF to GROMACS topology conversion
- Tabulated potential generation for custom interactions
- Support for bonded and non-bonded parameters
- Comprehensive protocol file operations
- Parameter type and interaction list generation

## File Format Reference

### .pxyz Format
Extended XYZ format with molecular information and marking:
```
NATOMS
box_x box_y box_z
atomname x y z molname mark
...
```

### .ref Format
Central data structure for forces and coordinates:
```
NATOMS
COMMENT
AtomName X Y Z ForceX ForceY ForceZ SolvFlag MoleculeID
...
NetF CenterX CenterY CenterZ NetFX NetFY NetFZ SolvFlag MoleculeID
Torq CenterX CenterY CenterZ TorqX TorqY TorqZ SolvFlag MoleculeID
```

### OFF Format
Force field library format with parameter sections:
- Inter-Potential: Non-bonded parameters (COU, EXP, SRD, POW)
- Molecular-Definition: Bonded parameters (bonds, angles, dihedrals)
- MOLTYP: Molecular topology definitions

### FF Format
CRYOFF-compatible force field files:
- [COU], [EXP], [SRD]: Non-bonded interaction types
- [bondtypes], [angletypes], [dihedraltypes]: Bonded parameters

## Typical Workflows

### 1. QM/MM System Preparation
```bash
# Convert GROMACS to pxyz format
gro2pxyz system.gro > system.pxyz

# Select center QM molecule randomly
markup_random -9 4 system.pxyz > step1.pxyz

# Add QM fitting region
mark_boundary 3.0 4 2 step1.pxyz

# Add buffer and MM regions
mark_boundary 2.6 3 2 step1.pxyz
mark_boundary 9.0 4 1 step1.pxyz

# Clean and sort
pxyz_dropoff 0 step1.pxyz | pxyz_sort | pxyz_recenter 1 > final.pxyz
```

### 2. QM Input File Generation
```bash
# Extract QM region
pxyz_select 4 final.pxyz > qm_center.pxyz
pxyz_select 1 final.pxyz > mm_charges.pxyz

# Generate Gaussian input
pxyz_gaussian_upd_geom template.gjf gaussian.nucinfo qm_center.pxyz > step1.gjf
pxyz_gaussian_upd_lattice step1.gjf gaussian.chginfo mm_charges.pxyz > final.gjf

# Or ORCA input
pxyz_orca_upd_xyz template.inp orca.nucinfo qm_center.pxyz > step1.inp
pxyz_orca_upd_chg step1.inp orca.chginfo mm_charges.pxyz > final.inp
```

### 3. Force Processing
```bash
# Generate initial .ref file
ref_gen_step1_cord molinfo system.xyz > initial.ref

# Add QM forces
orca_extract_grad calculation.engrad > qm_grad.dat
ref_upd_orca_grad qm_grad.dat initial.ref > step1.ref

# Add dispersion corrections
getd3force b3lyp system.xyz
ref_upd_d3_grad system.d3grad step1.ref > step2.ref

# Handle M-sites and calculate net forces
ref_fix_msite MW step2.ref | ref_upd_net > final.ref
```

### 4. Force Field Development
```bash
# Convert OFF to FF format
off2ff protocol.txt input.off template.ff output.ff

# Generate charge constraints
ff_gen_charge_constr cou_terms.dat constraint.dat > constraints.out

# Convert to topology
off2top protocol.off2top input.off template.top output.top

# Generate tabulated potentials
off2tab protocol.off2tab input.off template.top
```

## Integration with Simulation Packages

### Quantum Chemistry
- **Gaussian** - Input generation, force extraction
- **Molpro** - Geometry and lattice updates, gradient extraction
- **GAMESS** - EFP fragments, gradient processing
- **ORCA** - .engrad file processing, QM/MM calculations
- **PQS** - Coordinate and force extraction

### Molecular Dynamics
- **GROMACS** - Topology generation, force extraction, tabulated potentials
- **DL_POLY** - Force integration, REVCON file processing
- **CRYOFF** - Force field optimization, constraint equations

## Unit Conversions

The tools handle various unit conversions automatically:

| Conversion | Factor | Usage |
|------------|--------|-------|
| Hartree/Bohr → kcal/mol/Å | 627.5095/0.5291772083 | QM forces |
| Bohr → Angstrom | 0.5291772083 | Distances |
| kJ/mol/nm → kcal/mol/Å | 1.0/41.84 | GROMACS |
| kcal/mol → kJ/mol | 4.184 | Energy parameters |
| Angstrom → nm | 0.1 | Distance conversion |

## Installation and Requirements

### Prerequisites
- Perl with standard modules (List::Util)
- Python (for utility scripts)
- Fortran compiler (for special function utilities)
- Quantum chemistry software (Gaussian, ORCA, etc.)
- Molecular dynamics software (GROMACS, DL_POLY, etc.)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/AFMTools_Documentation.git

# Add AFMTools scripts to your PATH
export PATH=$PATH:/path/to/AFMTools/scr_QMMM_select
export PATH=$PATH:/path/to/AFMTools/scr_QMMM_inp
export PATH=$PATH:/path/to/AFMTools/scr_ref
export PATH=$PATH:/path/to/AFMTools/scr_off2ff
export PATH=$PATH:/path/to/AFMTools/scr_off2top
```

## Getting Help

### Script-Level Help
Most scripts include built-in help accessible via:
```bash
script_name -h
script_name -help
```

Enhanced scripts with comprehensive help:
- `ff_gen_charge_constr -h` - Detailed usage, examples, and integration notes

### Documentation Structure
Each documentation file includes:
- **Overview** - Purpose and scope of the toolset
- **File Format Reference** - Detailed format specifications
- **Script Documentation** - Individual tool descriptions with usage, parameters, and examples
- **Workflow Examples** - Real-world usage scenarios
- **Integration Notes** - How tools work together
- **Best Practices** - Recommendations and tips

## Contributing

Contributions to documentation improvements are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request with clear descriptions

## Citation

If you use AFMTools in your research, please cite the appropriate publications related to Adaptive Force Matching and the specific tools you employed.

## License

Please refer to the original AFMTools distribution for licensing information.

## Contact

For questions about the documentation or AFMTools usage:
- Open an issue on GitHub
- Refer to the detailed documentation files
- Check script help functions with `-h` flag

## Recent Improvements

### Documentation Enhancements
- **Comprehensive coverage** of all five script categories
- **Detailed file format specifications** with examples
- **Complete workflow guides** for common use cases
- **Unit conversion reference** for all supported packages
- **Integration documentation** showing how tools work together

### Script Enhancements
- **ff_gen_charge_constr** - Added comprehensive help function with:
  - Detailed usage instructions
  - Input/output format specifications
  - Working examples
  - Integration notes for CRYOFF workflows

## Version History

### v1.0.0 (2025-09-30)
- Initial comprehensive documentation release
- Complete coverage of scr_QMMM_select, scr_QMMM_inp, scr_ref, scr_off2ff, scr_off2top
- Enhanced ff_gen_charge_constr script with detailed help function
- Workflow examples and integration guides
- File format reference documentation

---

**AFMTools Documentation** - Empowering multi-scale molecular simulations through comprehensive, accessible documentation.
