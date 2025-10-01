# AFMTools scr_off2ff Scripts Documentation

The scr_off2ff directory contains scripts for converting OFF (Off Force Field) library files to FF (Force Field) parameter files used with CRYOFF for force field fitting. These tools are essential for the adaptive force matching (AFM) workflow, enabling the transfer of optimized parameters from research libraries to CRYOFF-compatible fitting files.

## Overview

The off2ff ecosystem facilitates the conversion between OFF library format (used for parameter storage and optimization) and FF format (used by CRYOFF for force field fitting). The main workflow involves:

1. **Parameter extraction** from OFF libraries using `offget_*` scripts
2. **Parameter processing** and manipulation using utility scripts
3. **Force field updating** using `off2ff_*` and `ff*` scripts

## File Formats

### OFF File Format
OFF files contain force field parameters in a structured format with sections like:
- **Inter-Potential**: Non-bonded interaction parameters (COU, EXP, SRD, etc.)
- **Molecular-Definition**: Intramolecular parameters (bonds, angles, dihedrals)
- **MOLTYP**: Molecular topology definitions

### FF File Format
FF files are CRYOFF-compatible force field files with sections like:
- **[COU]**: Coulomb interactions
- **[EXP]**: Exponential repulsion
- **[SRD]**: Short-range damping
- **[bondtypes]**, **[angletypes]**, **[dihedraltypes]**: Bonded parameters

### Protocol Files
Protocol files define the operations to perform during conversion:
- **copy**: Copy parameters between sections
- **populate**: Add entire sections to force field files
- **charge**: Handle charge assignment and calculations
- **condition**: Conditional parameter selection based on criteria

## Core Scripts

### Main Conversion Tool

#### off2ff
**Purpose**: Primary script for OFF to FF conversion using protocol files
**Function**: Orchestrates the conversion process by reading protocol files and executing appropriate sub-scripts
**Key Features**:
- Protocol-driven conversion workflow
- Supports multiple operation types (copy, populate, charge, condition)
- Temporary file management for safe updates
- Prevention of output file overwriting

### Parameter Extraction Scripts

#### offget_inter
**Purpose**: Extract non-bonded parameters from OFF files
**Function**: Reads Inter-Potential section and extracts specific parameter types
**Key Features**:
- Supports multiple potential types (COU, EXP, SRD, POW, STRC)
- Line number and range selection
- Formatted output for different parameter types
- Charge product special formatting (13.10f vs 12.3f)

#### offget_intra
**Purpose**: Extract bonded parameters from OFF files
**Function**: Reads Molecular-Definition section for specific molecules
**Key Features**:
- Molecule-specific parameter extraction
- Supports bonds, angles, dihedrals
- Handles molecular topology definitions

#### offget_charge
**Purpose**: Extract and calculate charges from OFF files
**Function**: Processes charge products and converts to individual charges
**Key Features**:
- Charge product processing
- Support for square root calculations (sqrtp, sqrtn)
- Division-based charge calculations
- Atom type matching

#### offget_atmtype
**Purpose**: Extract atom types for specific molecules
**Function**: Reads MOLTYP section to get atom type definitions
**Key Features**:
- Molecule-specific atom type listing
- Numbered atom type output
- MOLTYP section parsing

### Parameter Manipulation Scripts

#### off2ff_copy
**Purpose**: Copy parameters from OFF to FF files
**Function**: Handles both section copying and specific parameter updates
**Key Features**:
- Section-level copying with fit/fix flags
- Line-specific parameter updates
- Column-specific modifications
- Integration with ffaddremtermbynam and ffupdbynum

#### off2ff_charge
**Purpose**: Handle charge-related operations during conversion
**Function**: Processes charge assignments from files or calculations
**Key Features**:
- File-based charge reading
- Neutral charge assignment
- Charge product calculations
- Integration with charge files

#### off2ff_bymindist
**Purpose**: Select parameters based on minimum distance criteria
**Function**: Filters parameters using distance-based selection
**Key Features**:
- Distance-based parameter filtering
- Add/remove operations
- Conditional parameter selection

#### off2ff_byvalue
**Purpose**: Select parameters based on value criteria
**Function**: Filters parameters using value-based conditions
**Key Features**:
- Value-based parameter filtering
- Threshold-based selection
- Conditional operations

#### off2ff_bymaxminpam
**Purpose**: Select parameters based on maximum/minimum values
**Function**: Identifies extreme values for parameter selection
**Key Features**:
- Maximum/minimum value identification
- Parameter ranking
- Extreme value operations

#### off2ff_bychgprot
**Purpose**: Select parameters based on charge product criteria
**Function**: Filters parameters using charge product conditions
**Key Features**:
- Charge product analysis
- Product-based filtering
- Charge-dependent selection

### Force Field Manipulation Scripts

#### ffgetpam
**Purpose**: Extract specific parameters from FF files
**Function**: Retrieves parameters from specific sections and positions
**Key Features**:
- Section-specific parameter extraction
- Column and record number specification
- Fixed parameter detection
- Warning system for non-fixed parameters

#### ffupdbynum
**Purpose**: Update FF file parameters by line number
**Function**: Modifies specific parameters at given positions
**Key Features**:
- Line-specific updates
- Column-specific modifications
- Preserves file structure
- Safe parameter replacement

#### ffaddremtermbynam
**Purpose**: Add or remove terms from FF files by name
**Function**: Manages force field terms based on atom type names
**Key Features**:
- Name-based term management
- Add/remove operations
- Maintains FF file consistency
- Term validation

### Utility Scripts

#### getcharge
**Purpose**: Calculate individual charges from charge products
**Function**: Performs mathematical operations on charge values
**Key Features**:
- Square root calculations (positive/negative)
- Division operations
- Input validation
- Precision formatting

#### offgen_tab
**Purpose**: Generate tabulated potentials from OFF files
**Function**: Creates lookup tables for non-standard potentials
**Key Features**:
- Tabulated potential generation
- Custom potential support
- Integration with simulation engines

#### ff_gen_charge_constr
**Purpose**: Generate charge constraint equations for force field fitting
**Function**: Creates constraint equations relating charge products to molecular charges for CRYOFF optimization
**Key Features**:
- Maps charge product pairs (COU terms) to constraint indices
- Processes constraint equation definitions with linear combinations
- Supports weighted constraint equations
- Error detection for missing charge product pairs

**Usage**: `ff_gen_charge_constr COU_terms constraint_equation`

**Parameters**:
- `COU_terms`: File containing Coulomb charge product pairs (atom type pairs)
- `constraint_equation`: File defining constraint equations and atomic charges

**Input Files**:

1. **COU_terms file** - Lists atom type pairs for charge products:
   ```
   atm1  atm2
   C     H
   O     H
   N     C
   ...
   ```
   - Two-column format: atom type pairs
   - Order-independent (C H = H C)
   - Each pair assigned sequential index number

2. **constraint_equation file** - Defines constraint equations:
   ```
   coeff1 atom1 + coeff2 atom2 + ... + coeffN atomN = scaling_factor
   weight
   atomX  [charge_X]
   atomY  [charge_Y]
   ...
   ```
   - **Line 1**: Neutrality/constraint equation in algebraic format
     - Format: `coeff1 atom1 + coeff2 atom2 + ... = scaling_factor`
     - Coefficients represent number of each atom type in molecule
     - Scaling factor: Value to multiply atom charges by (use 0 for neutrality)
   - **Line 2**: Weight for this constraint equation
   - **Lines 3+**: Atom types to apply constraint to, with optional charges
     - Format: `atomname [charge]`
     - If charge omitted, defaults to 0
     - Each atom listed generates one constraint equation

**Output**: Constraint equations in CRYOFF format to stdout, errors to stderr

**Format**: `ncharge num1 index1 num2 index2 ... constraint_value weight`
- `ncharge`: Number of charge products in equation
- `num1, num2, ...`: Coefficients from the neutrality equation
- `index1, index2, ...`: Indices from COU_terms mapping
- `constraint_value`: atom_charge × scaling_factor
- `weight`: Weight for constraint equation

**How It Works**:
For each atom listed in lines 3+, generates a constraint equation:
- Σ(coeff_i × q_atom × q_i) = atom_charge × scaling_factor
- Where q_atom is the charge of the listed atom
- And q_i are charges of atoms in the equation

**Use Cases**:
1. **Neutrality constraints** (scaling_factor = 0, no charges):
   - Enforces charge neutrality: 1 O0 + 1 C1 + 2 C2 + ... = 0
   - Each atom type listed must satisfy the neutrality equation
2. **Charge relationship constraints** (with charges):
   - Enforces specific interaction energies between atoms
   - Useful for fitting to QM-derived charge distributions

**Error Handling**:
- Reports "_not_found_" to stderr for unmapped atom type pairs
- Validates constraint equation format
- Checks for proper equation structure

**Example 1 - Neutrality Constraint**:
```bash
# COU terms file
cat > cou_terms.dat << EOF
C1  C1
C1  O0
C1  H1
O0  O0
O0  H1
H1  H1
EOF

# Neutrality constraint equation
cat > constraint.dat << EOF
1 O0 + 1 C1 + 2 C2 + 1 C3 + 1 H0 + 9 H1 = 0
1E5
O0
C1
H0
EOF

# Generate neutrality constraints
ff_gen_charge_constr cou_terms.dat constraint.dat > constraints.out
```

**Example 2 - Charge Relationship Constraint**:
```bash
# With specific charges and scaling
cat > constraint_charged.dat << EOF
1 O0 + 1 C1 + 2 C2 = 2.5
1.0
O0  -0.6645
C1   0.1234
EOF

# This creates constraints with values:
# O0: -0.6645 × 2.5 = -1.66125
# C1:  0.1234 × 2.5 =  0.3085
ff_gen_charge_constr cou_terms.dat constraint_charged.dat > constraints.out
```

**Integration with Force Field Fitting**:
- Constraint equations enforce physical relationships between charge products
- Maintains charge neutrality during CRYOFF optimization
- Supports fitting to QM-derived electrostatic properties
- Compatible with CRYOFF force field optimization workflow
- Essential for adaptive force matching with polarizable force fields

### Specialized Scripts

#### refcal_Pfrc
**Purpose**: Calculate forces for reference calculations
**Function**: Processes reference force calculations for AFM workflows
**Key Features**:
- Reference force calculations
- AFM workflow integration
- Force comparison utilities

## Protocol File Operations

### Copy Operation
```
copy source_section,parameters destination_section,parameters
```
- Copies parameters between sections
- Supports line ranges and column specifications
- Maintains parameter relationships

### Populate Operation
```
populate source_section destination_section,fit_flag
```
- Adds entire sections to force field files
- Supports fit/fix flag assignment
- Handles section creation

### Charge Operation
```
charge source_specification destination_section,parameters
```
- Handles charge assignments
- Supports file-based charges
- Calculates charges from products
- Neutral charge assignment

### Condition Operation
```
condition criteria action parameters
```
- Conditional parameter selection
- Distance-based filtering (dist)
- Value-based filtering (val)
- Maximum/minimum selection (max/min)
- Charge product filtering (chg)

## Typical Workflows

### Basic OFF to FF Conversion
1. Prepare protocol file defining conversion operations
2. Run `off2ff protocol.txt input.off template.ff output.ff`
3. Verify output force field file
4. Test in molecular dynamics simulation

### Advanced Parameter Selection
1. Extract specific parameters: `offget_inter input.off EXP,ln1-10`
2. Calculate charges: `offget_charge COU,atm1,0.6645,ln3-7 input.off`
3. Update force field: `off2ff_copy parameters template.ff updated.ff`
4. Validate parameter consistency

### Charge Product Processing
1. Extract charge products from OFF file
2. Calculate individual charges using getcharge
3. Update FF file with calculated charges
4. Verify electroneutrality

## Integration with AFMTools

The off2ff scripts integrate with the broader AFMTools ecosystem:

1. **Input**: Receives optimized parameters from AFM calculations
2. **Processing**: Converts parameters to simulation-ready format
3. **Output**: Provides force field files for MD simulations
4. **Validation**: Supports force comparison and validation workflows

## File Management

- **Temporary Files**: Uses `/tmp/tempoff2ff.$$` for safe operations
- **Overwrite Protection**: Prevents accidental output file overwriting
- **Error Handling**: Comprehensive error checking and reporting
- **Backup Strategy**: Preserves original files during conversions

## Best Practices

1. **Protocol Validation**: Always validate protocol files before conversion
2. **Parameter Consistency**: Check parameter units and ranges
3. **Charge Neutrality**: Verify molecular charge neutrality
4. **File Backup**: Maintain backups of original OFF and FF files
5. **Testing**: Test converted force fields in short MD simulations
6. **Documentation**: Document conversion protocols for reproducibility

## Common Use Cases

### Force Field Development
- Convert research parameters to production format
- Integrate new parameter types
- Update existing force field databases

### Parameter Optimization
- Apply AFM-optimized parameters
- Selective parameter updates
- Conditional parameter assignment

### Multi-Scale Modeling
- QM/MM parameter integration
- Scale-specific parameter selection
- Hierarchical force field construction

## Error Handling and Troubleshooting

- **File Access**: Check file permissions and paths
- **Format Validation**: Verify OFF and FF file formats
- **Parameter Ranges**: Validate parameter physical reasonableness
- **Charge Conservation**: Ensure charge neutrality
- **Units**: Verify consistent unit systems

## Dependencies

- Perl with standard modules (List::Util)
- AFMTools core utilities
- Compatible OFF and FF file formats
- Protocol file syntax compliance

This documentation provides comprehensive guidance for using the scr_off2ff scripts in force field parameter conversion and management workflows within the AFMTools ecosystem.