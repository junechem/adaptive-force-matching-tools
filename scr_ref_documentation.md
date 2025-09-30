# AFMTools Reference File Processing Scripts Documentation

This documentation provides detailed information about the scripts in the `scr_ref/` directory, which process `.ref` files - the central data structure for storing atomic coordinates, forces, and molecular information in quantum mechanical (QM) calculations and molecular dynamics simulations.

## Overview

The `scr_ref` directory contains tools for:
- Extracting forces/gradients from various quantum chemistry programs
- Converting between different units and file formats
- Updating and managing `.ref` files with force data
- Calculating dispersion corrections (D2/D3)
- Interfacing with molecular dynamics programs
- Post-processing and analysis of force data

## Key Concepts

### .ref File Format

The `.ref` format is the central data structure used throughout AFMTools for storing molecular systems with associated force information:

**Structure**:
```
NATOMS
COMMENT_LINE
AtomName  X      Y      Z      ForceX  ForceY  ForceZ  SolvFlag  MoleculeID
AtomName  X      Y      Z      ForceX  ForceY  ForceZ  SolvFlag  MoleculeID
...
NetF      CenterX CenterY CenterZ NetFX   NetFY   NetFZ   SolvFlag MoleculeID
Torq      CenterX CenterY CenterZ TorqX   TorqY   TorqZ   SolvFlag MoleculeID
(more atoms for next molecule)
NetF      CenterX CenterY CenterZ NetFX   NetFY   NetFZ   SolvFlag MoleculeID
Torq      CenterX CenterY CenterZ TorqX   TorqY   TorqZ   SolvFlag MoleculeID
...
```

**Real Example**:
```
911
REPLACE
O0     0.00000     0.00000     0.00000     18.783494     34.837498     -9.113416     1.0     1UNK
C1     -0.26000    -1.33000     0.33000     -12.679902    2.132636      -18.999808    1.0     1UNK
...
NetF   -0.9680000  -1.9000000  -1.2260000  9.6527747     -2.4638781    2.5248805     1.0     1UNK
Torq   -0.9680000  -1.9000000  -1.2260000  -0.0853329    23.1817591    -17.1094585   1.0     1UNK
O0     -2.82000    -5.79000     2.00000     15.651961     -24.992812    12.581207     1.0     2UNK
...
```

**Fields**:
- **Coordinates**: X, Y, Z in Angstrom
- **Forces**: ForceX, ForceY, ForceZ in kcal/mol/Å
- **SolvFlag**: 1.0 for solvated/QM atoms, 0.0 for MM atoms or M-sites
- **MoleculeID**: Format like "1UNK", "2UNK" - identifies molecule number and residue name
- **NetF/Torq**: Net force and torque entries appear after each complete molecule

**Important Format Notes**:
- NetF and Torq entries use the center of mass coordinates for the molecule
- M-site atoms (virtual sites) have zero forces and SolvFlag=0.0
- The file can contain hundreds of molecules with interleaved NetF/Torq entries
- Some .ref files may not have NetF/Torq entries if `ref_upd_net` hasn't been run

### molinfo File Format

The `molinfo` file specifies molecular structure and atom counting for different molecule types:

**Structure**:
```
REPLACE
NATOMS_IN_MOLECULE RESNAME SOLVFLAG
AtomName Weight
AtomName Weight
...
next [RESIDUE_NAME]
NATOMS_IN_MOLECULE RESNAME SOLVFLAG
AtomName Weight
...
next [RESIDUE_NAME]
...
next
```

**Example for Neat System**:
```
REPLACE
15 UNK 1.0
C 1
C 1
C 1
C 1
C 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
next
```

**Example for Hydrated System**:
```
REPLACE
15 UNK 1.0
C 1
C 1
C 1
C 1
C 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
H 1
next    OW3
3   H2OQM 1.0
Ow   1.0
Hw   1.0
Hw   1.0
next    OW2
3   H2OQM 0.0
Ow   1.0
Hw   1.0
Hw   1.0
next    OW1
3   H2OMM 0.0
Omm 0.0
Hmm 0.0
Hmm 0.0
next
```

**Usage Notes**:
- First entry defines primary molecule (usually organic compound)
- Subsequent entries define different water/solvent types
- "OW3", "OW2", "OW1" correspond to QM fitting, QM buffer, MM water respectively
- SolvFlag: 1.0 for QM/solvated regions, 0.0 for MM regions
- **Weight field**: Used for calculating center of mass - typically 1.0 for normal atoms, 0.0 for virtual sites (M-sites)
- M-site atoms have weight=0.0 so they don't contribute to center of mass calculation
- "next" marks end of molecule definition

**Center of Mass Calculation**:
- Each atom's position is weighted by its weight value: `COM = Σ(position × weight) / Σ(weight)`
- Normal atoms use weight=1.0 (equal weighting)
- M-sites use weight=0.0 (excluded from COM calculation)
- NetF and Torq entries are placed at the calculated center of mass

## Utility Scripts

### chunk
**Purpose**: Extract specific line ranges from files (general text processing utility)

**Usage**: `chunk nskip nlines [file1 file2 ...]`

**Parameters**:
- `nskip`: Number of lines to skip from beginning
- `nlines`: Number of lines to extract
- `files`: Input files (optional, reads from stdin if not provided)

**Input**: Text files or stdin
**Output**: Selected lines written to stdout
**Details**: Useful for extracting portions of large output files from QM calculations

**Example**:
```bash
chunk 100 50 large_output.log  # Skip first 100 lines, extract next 50
```

## QM Force/Gradient Extraction Scripts

These scripts extract forces or gradients from quantum chemistry program output files and convert them to standardized units.

### gaussian_extract_frc
**Purpose**: Extract forces from Gaussian output files

**Usage**: `gaussian_extract_frc gaussian_output`

**Input**: Gaussian .out or .log files containing force calculations
**Output**: Forces in Hartree/Bohr units written to stdout
**Details**: Searches for "Forces (Hartrees/Bohr)" section in Gaussian output and extracts x, y, z force components

**Example**:
```bash
gaussian_extract_frc molecule.out > forces.dat
```

### gms_extract_grad
**Purpose**: Extract gradients from GAMESS output files

**Usage**: `gms_extract_grad gamess_output`

**Input**: GAMESS output files with gradient calculations
**Output**: Gradients in Hartree/Bohr units to stdout
**Details**: Searches for "UNITS ARE HARTREE" section and extracts gradient components

**Example**:
```bash
gms_extract_grad molecule.out > gradients.dat
```

### molpro_extract_grad
**Purpose**: Extract gradients from Molpro output files

**Usage**: `molpro_extract_grad molpro_output`

**Input**: Molpro output files containing gradient calculations
**Output**: Gradients to stdout
**Details**: Parses Molpro's gradient output section

### molpro_extract_xyz
**Purpose**: Extract atomic coordinates from Molpro output files

**Usage**: `molpro_extract_xyz molpro_output`

**Input**: Molpro output files with geometry information
**Output**: Standard XYZ format coordinates to stdout
**Details**: Converts coordinates from Bohr to Angstrom (conversion factor: 0.5291772083)

**Example**:
```bash
molpro_extract_xyz calculation.out > final_geometry.xyz
```

### orca_extract_grad
**Purpose**: Extract gradients from ORCA .engrad files

**Usage**: `orca_extract_grad name.engrad`

**Input**: ORCA .engrad files (gradient files generated by ORCA)
**Output**: Gradients to stdout
**Details**: Specialized parser for ORCA's gradient file format

**Example**:
```bash
orca_extract_grad molecule.engrad > orca_gradients.dat
```

### pqs_extract_frc
**Purpose**: Extract forces from PQS output files

**Usage**: `pqs_extract_frc PQS_output`

**Input**: PQS output files with force calculations
**Output**: Forces to stdout
**Details**: Searches for "force-x" keyword in PQS output

### pqs_extract_xyz
**Purpose**: Extract coordinates from PQS output files

**Usage**: `pqs_extract_xyz PQS_output`

**Input**: PQS output files with coordinate information
**Output**: Coordinates to stdout
**Details**: Parses PQS coordinate sections

## Dispersion Correction Scripts

### dftd3
**Type**: Binary executable (Grimme's DFT-D3 program)

**Purpose**: Calculate DFT-D3 dispersion corrections and gradients

**Function**: Compiled binary for computing dispersion energy corrections using Grimme's D3 method

### getd2force
**Purpose**: Calculate D2 dispersion forces using the dftd3 program

**Usage**: `getd2force functional file.xyz`

**Parameters**:
- `functional`: DFT functional name (e.g., "b3lyp", "pbe", "blyp")
- `file.xyz`: XYZ coordinate file

**Input**: XYZ coordinate files
**Output**: Creates `.d3grad` files with D2 dispersion gradients
**Details**: Wrapper script for dftd3 program using D2 parameters

**Example**:
```bash
getd2force b3lyp molecule.xyz  # Creates molecule.d3grad
```

### getd3force
**Purpose**: Calculate D3 dispersion forces using the dftd3 program with Becke-Johnson damping

**Usage**: `getd3force functional file.xyz`

**Parameters**:
- `functional`: DFT functional name
- `file.xyz`: XYZ coordinate file

**Input**: XYZ coordinate files
**Output**: Creates `.d3grad` and `.eng` files with D3 corrections
**Details**: Uses dftd3 with Becke-Johnson damping (-bj flag) for improved accuracy

**Example**:
```bash
getd3force pbe0 system.xyz  # Creates system.d3grad and system.eng
```

## Molecular Dynamics Interface Scripts

### get_gmx_frc
**Purpose**: Perform GROMACS calculations and extract forces

**Usage**: `get_gmx_frc file.gro templatedir`

**Parameters**:
- `file.gro`: GROMACS coordinate file
- `templatedir`: Directory containing GROMACS topology and parameter files

**Input**: 
- `.gro` coordinate file
- Template directory with topology files, parameter files, and mdrun setup

**Output**: GROMACS force files
**Details**: 
- Updates topology file using `top_upd_mol_nu`
- Runs GROMACS MD simulation with energy minimization
- Extracts forces from trajectory files
- Uses MPI-enabled mdrun with custom force field tables

**Workflow**:
1. Copy and update topology files
2. Run energy minimization
3. Extract forces from resulting trajectory
4. Clean up temporary files

**Example**:
```bash
get_gmx_frc system.gro /path/to/gromacs_templates/
```

### top_upd_mol_nu
**Purpose**: Update water molecule count in GROMACS topology files

**Usage**: `top_upd_mol_nu file.gro file.top`

**Parameters**:
- `file.gro`: GROMACS coordinate file
- `file.top`: GROMACS topology file

**Input**: GROMACS .gro and .top files
**Output**: Corrected topology file with proper molecule counts
**Details**: 
- Counts OW (water oxygen) atoms in .gro file
- Updates SOL (solvent) entries in topology file accordingly
- Essential for proper GROMACS simulations with varying water counts

**Example**:
```bash
top_upd_mol_nu system.gro topol.top > corrected_topol.top
```

## Reference File Management Scripts

### ref_gen_step1_cord
**Purpose**: Generate initial .ref files from coordinates and molecular information

**Usage**: `ref_gen_step1_cord mol_info [xyzfile]`

**Parameters**:
- `mol_info`: Molecular information file (molinfo format)
- `xyzfile`: XYZ coordinate file (optional, reads from stdin if not provided)

**Input**:
- Molinfo file specifying molecular structure
- XYZ coordinate file with atomic positions

**Output**: Initial .ref file with coordinates and zero forces to stdout
**Details**:
- Creates .ref file structure with placeholder zero forces
- Calculates center of mass for each molecule
- Assigns molecule IDs and solvation flags
- Essential first step in force calculation workflows

**Example**:
```bash
ref_gen_step1_cord molinfo system.xyz > initial.ref
```

### ref_fix_linenu
**Purpose**: Fix atom count in XYZ or .ref files

**Usage**: `ref_fix_linenu [file.xyz|file.ref]`

**Input**: XYZ or .ref files (potentially with incorrect atom counts)
**Output**: Corrected file with proper atom count in first line
**Details**: 
- Counts actual atoms in file and updates the first line accordingly
- Works with both XYZ and .ref file formats
- Essential after adding M-sites or other modifications

**Note**: There is also `xyz_fix_linenu` in scr_QMMM_select/ with identical functionality

**Example**:
```bash
ref_fix_linenu broken.ref > fixed.ref
xyz_fix_linenu broken.xyz > fixed.xyz  # Alternative in scr_QMMM_select/
```

### ref_fix_msite
**Purpose**: Set forces to zero for water M-site atoms (virtual sites)

**Usage**: `ref_fix_msite M_site_name [file.ref]`

**Parameters**:
- `M_site_name`: Name of M-site atoms (e.g., "MW", "OM")
- `file.ref`: Reference file (optional, reads from stdin if not provided)

**Input**: .ref files containing M-site atoms
**Output**: .ref file with zeroed forces for M-site atoms
**Details**: 
- Handles special treatment of water model dummy atoms
- M-sites are virtual sites that should not have forces applied
- Essential for proper water model behavior

**Example**:
```bash
ref_fix_msite MW water_system.ref > corrected.ref
```

## Force Integration Scripts

These scripts add forces/gradients from various QM programs to existing .ref files, handling proper unit conversions.

### ref_upd_gaussian_frc
**Purpose**: Add Gaussian forces to existing .ref file

**Usage**: `ref_upd_gaussian_frc gaussian_forces_file [file.ref]`

**Input**:
- Gaussian forces file (from `gaussian_extract_frc`)
- Existing .ref file (optional, reads from stdin if not provided)

**Output**: Updated .ref file with added Gaussian forces
**Unit Conversion**: 627.5095/0.5291772083 (Hartree/Bohr → kcal/mol/Å)
**Details**: Adds QM forces from Gaussian calculations to the .ref file force field

**Example**:
```bash
gaussian_extract_frc qm.out | ref_upd_gaussian_frc /dev/stdin system.ref > updated.ref
```

### ref_upd_gms_grad
**Purpose**: Add GAMESS gradients to .ref file

**Usage**: `ref_upd_gms_grad gamess_gradients_file [file.ref]`

**Input**:
- GAMESS gradients file (from `gms_extract_grad`)
- Existing .ref file

**Output**: Updated .ref file with GAMESS gradient contributions
**Unit Conversion**: -627.5095/0.5291772083 (gradients have opposite sign of forces)
**Details**: Converts GAMESS gradients to forces and adds to existing force data

### ref_upd_molpro_grad
**Purpose**: Add Molpro gradients to .ref file

**Usage**: `ref_upd_molpro_grad molpro_gradients_file [file.ref]`

**Input**:
- Molpro gradients file (from `molpro_extract_grad`)
- Existing .ref file

**Output**: Updated .ref file with Molpro contributions
**Unit Conversion**: -627.5095/0.5291772083
**Details**: Integrates Molpro gradients into the force framework

### ref_upd_orca_grad
**Purpose**: Add ORCA gradients from .engrad files to .ref file

**Usage**: `ref_upd_orca_grad molecule.engrad [file.ref]`

**Input**:
- ORCA .engrad file
- Existing .ref file

**Output**: Updated .ref file with ORCA gradient contributions
**Unit Conversion**: -627.5095/0.5291772083
**Details**: Directly processes ORCA .engrad files and integrates gradients

**Example**:
```bash
ref_upd_orca_grad molecule.engrad system.ref > updated.ref
```

### ref_upd_pqs_frc
**Purpose**: Add PQS forces to .ref file

**Usage**: `ref_upd_pqs_frc pqs_forces_file [file.ref]`

**Input**:
- PQS forces file (from `pqs_extract_frc`)
- Existing .ref file

**Output**: Updated .ref file with PQS force contributions
**Unit Conversion**: 627.5095/0.5291772083
**Details**: Integrates PQS forces into the reference framework

### ref_upd_gmx_frc
**Purpose**: Add GROMACS forces to .ref file

**Usage**: `ref_upd_gmx_frc gromacs_forces_file [file.ref]`

**Input**:
- GROMACS forces file (specialized format with f[n]={x,y,z} notation)
- Existing .ref file

**Output**: Updated .ref file with GROMACS force field contributions
**Unit Conversion**: 1.0/41.84 (kJ/mol/nm → kcal/mol/Å)
**Details**: Handles GROMACS-specific force file format and unit conversion

### ref_upd_dlpoly_frc
**Purpose**: Add DL_POLY forces to .ref file

**Usage**: `ref_upd_dlpoly_frc REVCON_file [file.ref]`

**Input**:
- DL_POLY REVCON file containing forces
- Existing .ref file

**Output**: Updated .ref file with DL_POLY contributions
**Unit Conversion**: 1.0/418.4 (DL_POLY units → kcal/mol/Å)
**Details**: Integrates DL_POLY molecular dynamics forces

### ref_upd_d3_frc and ref_upd_d3_grad
**Purpose**: Add D3 dispersion corrections to .ref file

**Usage**: `ref_upd_d3_grad d3_gradients_file [file.ref]`

**Input**:
- D3 gradients file (from `getd3force`)
- Existing .ref file

**Output**: Updated .ref file with dispersion corrections
**Unit Conversion**: -627.5095/0.529177
**Details**: Adds Grimme D3 dispersion corrections to existing forces

**Example**:
```bash
getd3force b3lyp system.xyz
ref_upd_d3_grad system.d3grad forces.ref > corrected.ref
```

## Analysis and Post-Processing Scripts

### ref_upd_net
**Purpose**: Calculate net forces and torques for molecules

**Usage**: `ref_upd_net [file.ref]`

**Input**: .ref file with atomic forces
**Output**: Updated .ref file with calculated NetF and Torq entries
**Details**:
- Sums atomic forces for each molecule to calculate net force
- Calculates torque around center of mass using: **τ** = **r** × **F**
- Updates NetF and Torq entries in .ref file
- Essential for analyzing molecular motion and rotational dynamics

**Calculation**:
- **Net Force**: Σ(atomic forces) for each molecule
- **Torque**: Σ(**r**ᵢ - **r**ₒₘ) × **F**ᵢ, where **r**ₒₘ is center of mass

**Example**:
```bash
ref_upd_net final_forces.ref > analyzed.ref
```

### xyz_add_msite
**Purpose**: Add M-site for BLYPSP-4F/WAIL water model

**Usage**: `xyz_add_msite OW_name HW1_name HW2_name M_name [file.xyz]`

**Parameters**:
- `OW_name`: Oxygen atom name (e.g., "Ow", "Omm")
- `HW1_name`: First hydrogen atom name (e.g., "Hw", "Hmm") 
- `HW2_name`: Second hydrogen atom name (e.g., "Hw", "Hmm")
- `M_name`: M-site atom name (e.g., "Ew", "Emm")

**Input**: .ref or XYZ file with water molecules
**Output**: File with added M-site virtual atoms
**Details**:
- Calculates M-site position using: **M** = 0.6×**O** + 0.2×(**H1**+**H2**)
- Adds virtual site for improved water electrostatics
- Essential for advanced water models with virtual interaction sites
- **Works on both XYZ and .ref file formats**

**Usage in AFMTools Workflow**:
```bash
# Add M-sites for different water types
xyz_add_msite Ow Hw Hw Ew system.ref | ref_fix_msite Ew |
xyz_add_msite Omm Hmm Hmm Emm | ref_fix_msite Emm > final.ref
```

**Water Model Types**:
- **QM Water**: Ow/Hw atoms → Ew M-sites
- **MM Water**: Omm/Hmm atoms → Emm M-sites  
- Provides better electrostatic representation
- M-site positioned along bisector of HOH angle

**Example**:
```bash
xyz_add_msite Ow Hw Hw Ew water.ref > water_with_msites.ref
```

## Unit Conversions Reference

The scripts handle conversions between different unit systems commonly used in quantum chemistry:

**Energy/Force Conversions**:
- Hartree/Bohr → kcal/mol/Å: ×627.5095/0.5291772083
- Gradients → Forces: ×(-1) (gradients have opposite sign)
- kJ/mol/nm → kcal/mol/Å: ×1.0/41.84 (GROMACS)
- DL_POLY units → kcal/mol/Å: ×1.0/418.4

**Length Conversions**:
- Bohr → Angstrom: ×0.5291772083

## Typical Workflow Examples

### AFMTools Integrated QM/MM Workflow (04_gen_ref.py)

This is the primary workflow used in the AFMTools ecosystem, as demonstrated in `Usage/04_gen_ref.py`:

1. **Prerequisites** (from previous steps):
```bash
# Step 02: Generate .pxyz files with QM/MM selections
02_gen_pxyz.py  # Creates 02_pxyz_files/*.pxyz

# Step 03: Generate QM input files and run calculations  
03_gen_force_input.py  # Creates 03_force_calculations/final*/MyMol.engrad
```

2. **Generate .ref files**:
```bash
# Step 04: Automated .ref file generation
04_gen_ref.py  # Processes all .pxyz files -> 04_ref_files/*.ref
```

**Internal Workflow of 04_gen_ref.py**:
```bash
# For each .pxyz file:
# 1. Filter atoms (exclude M-sites from force calculations)
select_atoms(non_msite_atoms, pxyz_file)

# 2. Generate initial .ref structure
ref_gen_step1_cord molinfo real_atoms.pxyz > step1.ref

# 3. Add ORCA forces and calculate net forces
ref_upd_orca_grad MyMol.engrad step1.ref | ref_upd_net > add_netf.ref

# 4. Handle M-sites for water models (if MM region present)
xyz_add_msite Ow Hw Hw Ew add_netf.ref | ref_fix_msite Ew |
xyz_add_msite Omm Hmm Hmm Emm | ref_fix_msite Emm |
xyz_fix_linenu > final.ref
```

### Manual QM/MM Force Calculation Workflow

For custom workflows or different QM programs:

1. **Initial Setup**:
```bash
# Create initial .ref file from coordinates and molinfo
ref_gen_step1_cord molinfo system.xyz > initial.ref
```

2. **QM Calculations** (run quantum chemistry programs):
```bash
# Run Gaussian, ORCA, Molpro, etc. on QM region
gaussian < qm_input.gjf > qm_output.out
orca qm_input.inp > qm_output.out
```

3. **Extract QM Forces**:
```bash
# Extract forces from QM calculations
gaussian_extract_frc qm_output.out > qm_forces.dat
orca_extract_grad qm_output.engrad > qm_gradients.dat
```

4. **Add QM Forces to .ref**:
```bash
# Add QM contributions
ref_upd_gaussian_frc qm_forces.dat initial.ref > step1.ref
ref_upd_orca_grad qm_gradients.dat step1.ref > step2.ref
```

5. **Add Dispersion Corrections**:
```bash
# Calculate and add D3 corrections
getd3force b3lyp system.xyz
ref_upd_d3_grad system.d3grad step2.ref > step3.ref
```

6. **Add MM Forces**:
```bash
# Add classical force field contributions
get_gmx_frc system.gro /gromacs/templates/ > mm_forces.dat
ref_upd_gmx_frc mm_forces.dat step3.ref > step4.ref
```

7. **Handle Special Cases**:
```bash
# Fix M-site forces and calculate net forces
ref_fix_msite MW step4.ref > step5.ref
ref_upd_net step5.ref > final.ref
```

### Water Model Enhancement Workflow

```bash
# Add M-sites to water coordinates
xyz_add_msite OW HW1 HW2 MW water.xyz > water_msites.xyz

# Generate .ref file with M-sites
ref_gen_step1_cord molinfo_with_msites water_msites.xyz > water.ref

# ... perform calculations ...

# Ensure M-site forces are zero
ref_fix_msite MW final_forces.ref > corrected.ref
```

## Important Notes

### AFMTools Integration
- **Primary Usage**: Most users should use `04_gen_ref.py` for automated .ref generation
- **Dependencies**: Requires completed steps 02 (pxyz generation) and 03 (QM calculations)
- **File Structure**: Expected directory structure: `02_pxyz_files/`, `03_force_calculations/`, `04_ref_files/`
- **molinfo**: Must be placed in `04_ref_files/molinfo` before running 04_gen_ref.py

### File Handling
- Most scripts read from stdin if no input file specified
- All scripts write to stdout (redirect to save results)
- Always backup original files before processing
- Scripts handle various QM program output formats automatically
- .ref files can contain hundreds to thousands of molecules

### M-site and Water Model Handling
- M-sites are virtual atoms that must have zero forces (`ref_fix_msite`)
- Different water types require different M-site names (Ew for QM, Emm for MM)
- M-sites are excluded from QM force calculations but included in final .ref files
- The workflow: `xyz_add_msite` → `ref_fix_msite` → `xyz_fix_linenu`

### Error Handling
- Scripts include basic error checking for file existence
- Unit conversions are handled automatically
- Always verify output formats match expected results
- Check stderr for warnings and error messages
- Invalid molinfo files will cause failures in ref_gen_step1_cord

### Performance Considerations
- Scripts are optimized for typical molecular system sizes (100-1000 molecules)
- Large systems may require memory optimization
- File I/O is the primary bottleneck for most operations
- Parallel QM calculations can be processed independently
- .ref files can be several MB in size for large systems

### Integration with Other AFMTools
- .ref files are the final output for force analysis workflows  
- Coordinates come from .pxyz files (scr_QMMM_select output)
- QM input preparation uses scr_QMMM_inp tools
- Results can be analyzed with molecular dynamics analysis tools
- Force data can be used for geometry optimization workflows
- Compatible with GROMACS, DL_POLY, and other MD programs

This comprehensive toolkit enables sophisticated multi-scale simulations combining quantum mechanical calculations with molecular dynamics, dispersion corrections, and classical force fields in a unified framework centered around the .ref file format.