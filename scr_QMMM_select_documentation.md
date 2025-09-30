# AFMTools QMMM Selection Scripts Documentation

This documentation provides detailed information about the scripts in the `scr_QMMM_select/` directory, which are primarily used for preparing QM/MM calculations by selecting and marking atoms/molecules in molecular systems.

## File Format Overview

These tools work primarily with two file formats:

### .gro format (GROMACS structure file)
- Line 1: Comment/title
- Line 2: Number of atoms
- Lines 3-N+2: Atom records with format: `resnum resname atomname atomnum x y z [vx vy vz]`
- Last line: Box dimensions

### .pxyz format (Extended XYZ with marking)
- Line 1: Number of atoms
- Line 2: Box dimensions (cubic box: `x y z`)
- Lines 3-N+2: Atom records with format: `atomname x y z molname mark`
- The `mark` field is used to classify atoms (e.g., QM=4, QM_fitting=3, QM_buffer=2, MM=1, unselected=-9)

## Core Conversion Tools

### gro2pxyz
**Purpose**: Converts GROMACS .gro files to .pxyz format
**Usage**: `gro2pxyz [file.gro]`
**Input**: GROMACS .gro file (via stdin or file argument)
**Output**: .pxyz format to stdout
**Details**: 
- Converts nm to Angstrom units (multiplies coordinates by 10.0)
- Sets all initial mark values to -9 (unselected)
- Only supports cubic simulation boxes
- Handles both 5-field and 8-field .gro formats (with/without velocities)

### pxyz_2gro
**Purpose**: Converts .pxyz files back to GROMACS .gro format
**Usage**: `pxyz_2gro [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: GROMACS .gro format to stdout
**Details**:
- Converts Angstrom to nm units (multiplies coordinates by 0.1)
- Assigns sequential molecule numbers
- Extracts residue names from molecule identifiers
- Assigns sequential atom indices

### pxyz_2vxyz
**Purpose**: Creates visualization-friendly format by combining atom names with mark values
**Usage**: `pxyz_2vxyz [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz format to stdout where atom names include mark values
**Details**:
- Concatenates atom name with mark value (e.g., "C4" for carbon atom with mark 4)
- Useful for visualizing different atom classifications in VMD or similar programs
- Does not include the separate mark column in output

## Molecular Selection and Marking Tools

### mark_byname
**Purpose**: Marks all molecules containing a specific name pattern
**Usage**: `mark_byname targetname mark_val [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz file to stdout with updated marks
**Details**:
- Performs case-insensitive pattern matching on molecule names
- Marks all atoms belonging to molecules whose name contains the target string
- Useful for selecting specific molecule types (e.g., solute vs solvent)

### markup_random
**Purpose**: Randomly selects one molecule from those with a specific mark value and assigns it a new mark
**Usage**: `markup_random mark_old mark_new [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz file to stdout
**Details**:
- Identifies all unique molecules with mark value `mark_old`
- Randomly selects one of these molecules
- Changes the mark of all atoms in the selected molecule to `mark_new`
- Prints selected molecule name to stderr
- Only supports orthorhombic (cubic/rectangular) simulation boxes

### markup_mol
**Purpose**: Marks molecules based on isolation criteria - only marks molecules if no lower-marked atoms are within cutoff distance
**Usage**: `markup_mol rcut mark_old mark_new [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz file to stdout
**Details**:
- For each atom with mark `mark_old`, checks if any atoms with mark < `mark_old` are within `rcut` distance
- Only marks entire molecules where ALL atoms pass this isolation test
- Changes qualifying molecules from `mark_old` to `mark_new`
- Uses periodic boundary conditions for distance calculations
- Useful for identifying "bulk" molecules away from surfaces or interfaces

## Distance-Based Selection Tools

### mark_within
**Purpose**: Marks molecules within a specified distance of a reference atom
**Usage**: `mark_within atom_index rcut mark_val [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz file to stdout
**Details**:
- `atom_index` is 1-based indexing
- Calculates distances using periodic boundary conditions
- Marks entire molecules (not individual atoms) if any atom is within `rcut`
- Only increases mark values (mark_val must be higher than existing mark)
- Prints reference atom coordinates to stderr

### mark_boundary
**Purpose**: Marks molecules within cutoff distance of atoms with a specific mark value
**Usage**: `mark_boundary rcut mark_val mark_val_boundary file.pxyz`
**Input**: .pxyz file (specified as argument, file is modified in-place)
**Output**: Modifies the input file in-place
**Details**:
- Finds all atoms with mark value `mark_val`
- For each found atom, calls `mark_within` to mark surrounding molecules
- **MODIFIES INPUT FILE DIRECTLY** - use with caution
- Uses temporary files during processing
- Useful for creating buffer regions around selected atoms

### mark_within_range
**Purpose**: Marks molecules within cutoff distance of a range of atoms
**Usage**: `mark_within_range atom_id_start atom_id_end rcut mark_val file.pxyz`
**Input**: .pxyz file (specified as argument, file is modified in-place)
**Output**: Modifies the input file in-place
**Details**:
- Applies `mark_within` for each atom in the specified range
- **MODIFIES INPUT FILE DIRECTLY**
- Uses 1-based indexing for atom IDs
- Prints commands to stdout for transparency

### mark_within_list  
**Purpose**: Marks molecules within cutoff distance of a list of specified atoms
**Usage**: `mark_within_list rcut mark_val file.pxyz atom_id1 atom_id2 atom_id3 ...`
**Input**: .pxyz file (specified as argument, file is modified in-place)
**Output**: Modifies the input file in-place
**Details**:
- Applies `mark_within` for each atom ID in the list
- **MODIFIES INPUT FILE DIRECTLY**
- Validates that all provided IDs are numeric
- Uses 1-based indexing for atom IDs

## Nearest Neighbor Selection Tools

### mark_nextnearest
**Purpose**: Finds and marks the nearest molecule to a range of atoms
**Usage**: `mark_nextnearest atom_id_start atom_id_end mark_val [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Modified .pxyz file to stdout
**Details**:
- Searches for the closest molecule to any atom in the specified range
- Only considers molecules with marks smaller than `mark_val`
- Marks all atoms of the closest molecule with `mark_val`
- Uses periodic boundary conditions for distance calculations
- Prints marked molecule information to stderr

### mark_nextnearest_n
**Purpose**: Iteratively marks the N nearest molecules to a range of atoms
**Usage**: `mark_nextnearest_n atom_id_start atom_id_end N mark_val file.pxyz`
**Input**: .pxyz file (specified as argument, file is modified in-place)
**Output**: Modifies the input file in-place
**Details**:
- Calls `mark_nextnearest` N times to mark N closest molecules
- **MODIFIES INPUT FILE DIRECTLY**
- Each iteration finds the next-closest unmarked molecule
- Prints progress information to stdout

## Atom/Molecule Selection and Filtering Tools

### pxyz_select
**Purpose**: Extracts atoms with a specific mark value
**Usage**: `pxyz_select val [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Selected atoms to stdout (without header lines)
**Details**:
- Outputs only atoms matching the specified mark value
- Does not include the atom count or box dimension lines
- Counts and reports number of atoms and molecules to stderr
- Output can be used with other tools or for analysis

### pxyz_select_n
**Purpose**: Extracts atoms with any of multiple specified mark values
**Usage**: `pxyz_select_n file.pxyz val1 val2 val3 ...`
**Input**: .pxyz file (must be specified as first argument)
**Output**: Selected atoms to stdout (without header lines)
**Details**:
- Can select atoms with multiple different mark values in one operation
- For each mark value, reports counts to stderr
- Processes the file once for each mark value specified

### pxyz_dropoff
**Purpose**: Removes atoms with mark values at or below a threshold
**Usage**: `pxyz_dropoff val [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Filtered .pxyz file to stdout
**Details**:
- Keeps only atoms with mark > val
- Outputs complete .pxyz format with updated atom count
- Commonly used to remove unselected atoms (mark -9) or create final selections

## System Manipulation Tools

### pxyz_recenter
**Purpose**: Centers the simulation box around a specified atom and unwraps molecules
**Usage**: `pxyz_recenter center_atom_index [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Recentered .pxyz file to stdout
**Details**:
- Uses 1-based indexing for center_atom_index
- Translates all coordinates so the specified atom is at the origin
- Unwraps molecules that are split across periodic boundaries
- Only supports orthorhombic (cubic/rectangular) boxes
- Prints original center coordinates to stderr
- Essential for proper visualization and analysis

### pxyz_sort
**Purpose**: Sorts atoms by their mark values (highest to lowest)
**Usage**: `pxyz_sort [file.pxyz]`
**Input**: .pxyz file (via stdin or file argument)
**Output**: Sorted .pxyz file to stdout
**Details**:
- Preserves all atom information while reordering
- Sorts in descending order of mark values
- Useful for organizing output and ensuring consistent atom ordering

## XYZ File Utilities

### xyz_add_lineno
**Purpose**: Adds standard XYZ headers to a headerless coordinate file
**Usage**: `xyz_add_lineno [file.xyz]`
**Input**: Headerless coordinate file (via stdin or file argument)
**Output**: Standard XYZ format to stdout
**Details**:
- Counts total number of lines in input
- Adds atom count as first line
- Adds "comment" as second line
- Useful for converting partial coordinate files to standard format

### xyz_add_linenu
**Purpose**: Identical to xyz_add_lineno (duplicate script)
**Usage**: `xyz_add_linenu [file.xyz]`
**Input**: Headerless coordinate file (via stdin or file argument)
**Output**: Standard XYZ format to stdout
**Details**: Same functionality as xyz_add_lineno

### xyz_fix_lineno
**Purpose**: Corrects the atom count in XYZ files that have incorrect headers
**Usage**: `xyz_fix_lineno [file.xyz]`
**Input**: XYZ file with potentially incorrect atom count (via stdin or file argument)
**Output**: XYZ file with corrected atom count to stdout
**Details**:
- Reads existing first line (atom count) and second line (comment)
- Counts actual coordinate lines
- Outputs corrected atom count, preserves original comment
- Useful for fixing files that have been manually edited

### xyz_fix_linenu
**Purpose**: Identical to xyz_fix_lineno (duplicate script)
**Usage**: `xyz_fix_linenu [file.xyz]`
**Input**: XYZ file with potentially incorrect atom count (via stdin or file argument)
**Output**: XYZ file with corrected atom count to stdout
**Details**: Same functionality as xyz_fix_lineno

## Typical Workflow Usage

Based on the `02_gen_pxyz.py` example, a typical QM/MM selection workflow involves:

1. **Convert format**: `gro2pxyz input.gro > system.pxyz`
2. **Select center molecule**: `markup_random -9 4 system.pxyz > step1.pxyz`
3. **Add QM fitting region**: `mark_boundary 3.0 4 2 step1.pxyz` (creates temporary marks)
4. **Select fitting molecules**: `markup_random 2 3 step1.pxyz > step2.pxyz` (repeat as needed)
5. **Add QM buffer**: `mark_boundary 2.6 3 2 step2.pxyz`
6. **Add MM region**: `mark_boundary 9.0 4 1 step2.pxyz` and `mark_boundary 9.0 3 1 step2.pxyz`
7. **Clean up**: `pxyz_dropoff 0 step2.pxyz | pxyz_sort > final.pxyz`
8. **Recenter**: `pxyz_recenter 1 final.pxyz > recentered.pxyz`

## Important Notes

- **In-place modification**: Several tools (mark_boundary, mark_within_range, mark_within_list, mark_nextnearest_n) modify input files directly. Always work with copies of important data.
- **Indexing**: All tools use 1-based indexing for atom numbers, consistent with typical molecular file formats.
- **Periodic boundaries**: Distance calculations properly account for periodic boundary conditions.
- **Box limitations**: Most tools only support orthorhombic (cubic/rectangular) simulation boxes.
- **Mark value hierarchy**: Higher mark values typically represent more important regions (QM > MM > unselected).
- **Error handling**: Most scripts provide basic help with `-h` or `-help` flags.

## Standard Mark Value Conventions

- **4**: Center QM molecule (primary QM region)
- **3**: QM fitting molecules  
- **2**: QM buffer molecules
- **1**: MM molecules
- **-9**: Unselected atoms (initial default)

This marking system allows for systematic construction of QM/MM regions with appropriate chemical environments and computational boundaries.