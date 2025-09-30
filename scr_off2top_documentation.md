# AFMTools scr_off2top Scripts Documentation

The scr_off2top directory contains scripts for converting OFF (Off Force Field) library files to topology files (.top/.itp) for molecular dynamics simulation packages, primarily GROMACS. These tools are essential for translating optimized force field parameters from AFM calculations into production-ready simulation input files.

## Overview

The off2top ecosystem facilitates the conversion between OFF library format (used for parameter storage and optimization) and topology file format (used by MD simulation packages). The main workflow involves:

1. **Topology conversion** using `off2top` with protocol-driven parameter transfer
2. **Tabulated potential generation** using `off2tab` for custom potentials
3. **Parameter processing** using specialized `off2top_*` scripts
4. **Table generation** using `gentab_*` scripts for various potential types
5. **Topology manipulation** using utility scripts for updates and modifications

## File Formats

### OFF File Format
OFF files contain force field parameters in structured sections:
- **Inter-Potential**: Non-bonded interaction parameters (COU, EXP, SRD, etc.)
- **Molecular-Definition**: Intramolecular parameters (bonds, angles, dihedrals)
- **MOLTYP**: Molecular topology definitions
- **Table-Potential**: Custom/tabulated potential specifications

### Topology File Format (.top/.itp)
GROMACS topology files with sections:
- **[atoms]**: Atomic definitions with charges and types
- **[bonds]**, **[angles]**, **[dihedrals]**: Bonded interactions
- **[nonbond_params]**: Non-bonded parameter specifications
- **[bondtypes]**, **[angletypes]**, **[dihedraltypes]**: Parameter type definitions

### Protocol Files
Protocol files define conversion operations:
- **mol.**: Operations on molecule definitions (charges, bonds, angles, etc.)
- **pam.**: Operations on parameter files (recommended approach)
- **list.**: Generation of interaction lists
- **tab.**: Tabulated potential generation specifications

## Core Scripts

### Main Conversion Tools

#### off2top
**Purpose**: Primary script for OFF to topology conversion using protocol files
**Function**: Orchestrates the conversion process by reading protocol files and executing appropriate sub-scripts
**Key Features**:
- Protocol-driven conversion workflow
- Supports molecule and parameter file operations
- Handles bonded and non-bonded parameters
- Charge assignment and transfer
- Temporary file management for safe updates
- Prevention of output file overwriting

#### off2tab
**Purpose**: Generate tabulated potential files from OFF parameters
**Function**: Creates .xvg table files for custom potentials in MD simulations
**Key Features**:
- Protocol-driven table generation
- Support for various potential types
- Grid specification (cutoff, spacing)
- Integration with GROMACS table format
- Custom potential scaling and prefixes

### Parameter Processing Scripts

#### off2top_molecule_charge
**Purpose**: Transfer molecular charges from OFF to topology files
**Function**: Updates charge assignments in molecule definitions
**Key Features**:
- Charge extraction from COU sections
- File-based charge assignments
- Unit conversion support
- Atom type mapping capabilities

#### off2top_molecule_define
**Purpose**: Update molecular definitions in topology files
**Function**: Transfers atomic definitions and molecular structure
**Key Features**:
- Atom type assignments
- Molecular topology updates
- Parameter column specifications
- Unit conversion handling

#### off2top_molecule_param
**Purpose**: Transfer molecular parameters (bonds, angles, dihedrals)
**Function**: Updates bonded parameter values in molecule sections
**Key Features**:
- Bond parameter updates
- Angle parameter updates
- Dihedral parameter updates
- Unit conversion support
- Extra column handling

#### off2top_bonded_param
**Purpose**: Update bonded parameters in parameter files
**Function**: Transfers bonded parameters to parameter type definitions
**Key Features**:
- Parameter type updates
- Force constant conversions
- Multiple parameter types support
- Atom type pattern matching

#### off2top_nonbonded_param
**Purpose**: Update non-bonded parameters in topology files
**Function**: Transfers non-bonded interaction parameters
**Key Features**:
- Multiple potential type support
- Unit conversion capabilities
- Parameter column specifications
- Atom type matching

#### off2top_nonbonded_charge
**Purpose**: Update non-bonded charges in parameter files
**Function**: Handles charge assignments for non-bonded interactions
**Key Features**:
- Charge product calculations
- File-based charge reading
- Unit conversions
- Atom type mappings

### List Generation Scripts

#### off2top_bonded_list
**Purpose**: Generate bonded interaction lists
**Function**: Creates lists of bonded interactions from molecular definitions
**Key Features**:
- Bond list generation
- Angle list generation
- Dihedral list generation
- Atom type filtering

#### off2top_nonbonded_list
**Purpose**: Generate non-bonded interaction lists
**Function**: Creates comprehensive non-bonded interaction lists
**Key Features**:
- Exclusion pattern handling
- Atom type pair enumeration
- Interaction filtering
- Parameter assignment

### Tabulated Potential Generation Scripts

#### gen_nonbonded_tab
**Purpose**: Universal tabulated potential generator
**Function**: Generates tables for various potential types with proper units
**Key Features**:
- Multiple potential type support (POW, TTP, SRD, EXP, COU, etc.)
- Unit conversion handling
- Grid specification
- Dispersion corrections
- GROMACS format output

#### gentab_cou
**Purpose**: Generate Coulomb potential tables
**Function**: Creates electrostatic interaction tables
**Key Features**:
- Coulomb potential calculations
- Dielectric constant handling
- Cutoff specifications
- Force and potential tabulation

#### gentab_exp_buck
**Purpose**: Generate exponential and Buckingham potential tables
**Function**: Creates repulsive exponential potential tables
**Key Features**:
- Exponential potential: A*exp(-B*r)
- Buckingham potential support
- Parameter scaling
- Energy and force calculations

#### gentab_pow_ttp_srd
**Purpose**: Generate power-law, Tang-Toennies, and SRD potential tables
**Function**: Creates various dispersion and repulsion potential tables
**Key Features**:
- Power-law potentials: C6/r^n
- Tang-Toennies damping functions
- Short-range damping (SRD)
- Dispersion corrections

#### gentab_strc
**Purpose**: Generate structure-based potential tables
**Function**: Creates custom structure-dependent potentials
**Key Features**:
- Structure-specific potentials
- Custom functional forms
- Parameter interpolation

#### gentab_thc
**Purpose**: Generate THC (Three-body correlation) potential tables
**Function**: Creates specialized three-body potential tables
**Key Features**:
- Three-body interactions
- Correlation function handling
- Angular dependencies

#### gentab_quarbond
**Purpose**: Generate quartic bond potential tables
**Function**: Creates quartic bond stretch potential tables
**Key Features**:
- Quartic bond potentials
- Anharmonic corrections
- Bond length dependencies

### Topology Manipulation Scripts

#### topget_param_moldef
**Purpose**: Extract parameters from molecular definitions
**Function**: Retrieves specific parameters from topology molecule sections
**Key Features**:
- Parameter extraction
- Column and line specifications
- Multiple parameter types
- Format preservation

#### topget_param_paramfile
**Purpose**: Extract parameters from parameter files
**Function**: Retrieves parameters from topology parameter sections
**Key Features**:
- Parameter type handling
- Section-specific extraction
- Line range specifications
- Format consistency

#### topupd_moldef
**Purpose**: Update molecular definitions in topology files
**Function**: Modifies molecular parameters and definitions
**Key Features**:
- Parameter updates
- Structure modifications
- Safe file handling
- Backup preservation

#### topupd_paramfile
**Purpose**: Update parameter files
**Function**: Modifies parameter type definitions
**Key Features**:
- Parameter type updates
- Section modifications
- Multi-parameter handling
- File integrity preservation

#### topadd_list_paramfile
**Purpose**: Add interaction lists to parameter files
**Function**: Appends new interaction lists to topology files
**Key Features**:
- List addition capabilities
- Format consistency
- Duplicate prevention
- Section management

### Utility Scripts

#### adjust_charge
**Purpose**: Adjust charges for electroneutrality
**Function**: Corrects molecular charges to ensure neutrality
**Key Features**:
- Charge balancing
- Neutrality enforcement
- Multiple molecule support
- Precision control

#### checkxvg
**Purpose**: Validate XVG table files
**Function**: Checks tabulated potential files for correctness
**Key Features**:
- File format validation
- Data consistency checks
- Error reporting
- Table verification

#### tabcombine
**Purpose**: Combine multiple tabulated potential files
**Function**: Merges tables for complex potential combinations
**Key Features**:
- Table addition
- Grid compatibility checking
- Format preservation
- Error handling

#### getcharge
**Purpose**: Calculate charges from charge products
**Function**: Utility for charge calculations (shared with scr_off2ff)
**Key Features**:
- Charge product division
- Square root operations
- Precision formatting
- Input validation

#### rename_table.py
**Purpose**: Rename and organize table files
**Function**: Python utility for table file management
**Key Features**:
- File renaming automation
- Directory organization
- Pattern-based operations
- Batch processing

### Supporting Utilities

#### igamma / igamma.f90
**Purpose**: Incomplete gamma function calculations
**Function**: Mathematical utility for special function calculations
**Key Features**:
- Incomplete gamma functions
- Numerical integration
- High precision calculations
- Fortran implementation

#### mdpupd_engtab
**Purpose**: Update MDP files for energy tables
**Function**: Modifies GROMACS run parameter files for table usage
**Key Features**:
- MDP file updates
- Energy table specifications
- Run parameter modifications
- Table integration

## Protocol File Operations

### Parameter Specification Key

All protocol operations follow a standardized parameter specification format. Understanding these components is essential for creating effective protocol files:

**OFF Source Specifications:**
- `COU,atm1,divisor,line_specs`: Charge extraction from Coulomb section
  - `COU`: Coulomb section identifier in OFF file
  - `atm1/atm2`: Use first or second atom type from charge products
  - `divisor`: Value to divide charge products by (e.g., 0.6645 for specific charge calculations)
  - `line_specs`: Line specifications (ln1-40, ln1,ln5,ln10, etc.)

- `molecule_section,column`: Parameter extraction from molecular definitions
  - `molecule_section`: Name of molecule in OFF file (e.g., ALA7, SOL, UNK)
  - `column`: Column number containing parameters (col3, col4, col5, etc.)

- `OFF_section,column[,line_specs]`: Parameter extraction from Inter-Potential sections
  - `OFF_section`: Section type (EXP, SRD, POW, STRC, BUC, etc.)
  - `column`: Column containing parameter values
  - `line_specs`: Optional line range specifications

**Topology Destination Specifications:**
- `molecule_section,column,line_range`: Target location in molecule definitions
  - `molecule_section`: Target molecule name in topology file
  - `column`: Column number for parameter placement (col4, col7, etc.)
  - `line_range`: Lines to update (ln1-73, ln10-50, ln1,ln5,ln10)

- `parameter_section,column,line_range`: Target location in parameter files
  - `parameter_section`: Section name (nonbond_params, bondtypes, angletypes, etc.)
  - `column`: Column number for parameter placement
  - `line_range`: Lines to update in the section

**Unit Conversion Factors:**
- `1.0`: No unit conversion (same units)
- `4.184`: kcal/mol → kJ/mol (energy conversion)
- `418.4`: kcal/mol/rad² → kJ/mol/rad² (angle force constants)
- `0.1`: Å → nm (distance conversion)
- Custom factors for specific parameter types

**Pattern Options:**
- `default`: Standard processing with direct atom type matching
- `type=atmtype`: Use external atom type mapping file
- `no`: Use atom types exactly as specified
- `extra:col5=col8`: Copy additional columns during transfer
- Combinations: `type=atmtype,extra:col5=col8`

### Molecule Operations (mol.)

#### mol.charge
```
mol.charge COU,atm1,divisor,line_specs molecule_section,column,line_range unit_conversion pattern
```

**Purpose**: Updates molecular charges in topology molecule definitions from OFF charge data

**Parameter Details**:
- **Source**: `COU,atm1,0.6645,ln1-40` 
  - Extract from Coulomb section, use first atom type, divide by 0.6645, process lines 1-40
- **Destination**: `ALA7,col7,ln1-73`
  - Update ALA7 molecule, column 7 (charges), lines 1-73
- **Unit conversion**: Typically `1.0` (charges are dimensionless)
- **Pattern**: `default` or `type=atmtype` for atom type mapping

**Alternative syntax**: `mol.charge file=charge_file` to read charges from external file

#### mol.Bond / mol.Angle / mol.Dih
```
mol.Bond molecule_section,column molecule_topology,section,column,line_range unit_conversion pattern
```

**Purpose**: Updates bonded parameters (bonds, angles, dihedrals) in molecule definitions

**Parameter Details**:
- **Source**: `ALA7,col4`
  - Extract from ALA7 molecule definition, column 4 (force constants)
- **Destination**: `ALA7,bonds,col4,ln1-90`
  - Update ALA7 molecule, bonds section, column 4, lines 1-90
- **Unit conversion**: `4.184` for energy parameters (kcal/mol → kJ/mol)
- **Pattern**: `default`, `type=atmtype`, or `extra:col5=col8` for additional columns

**Examples**:
- `mol.Bond ALA7,col4 ALA7,bonds,col4,ln1-90 4.184 default`
- `mol.Angle ALA7,col4 ALA7,angles,col4,ln1-70 1.0 type=atmtype`
- `mol.Dih ALA7,col4 ALA7,dihedrals,col7,ln1-50 1.0 extra:col5=col8`

#### mol.define
```
mol.define molecule_section,column molecule_topology,section,column,line_range unit_conversion pattern
```

**Purpose**: Updates atomic definitions and atom types in molecule definitions

**Parameter Details**:
- **Source**: `ALA7,col4`
  - Extract atom type definitions from ALA7 molecule, column 4
- **Destination**: `ALA7,atoms,col4,ln1`
  - Update ALA7 molecule, atoms section, column 4 (atom types), line 1
- **Unit conversion**: Typically `1.0` (atom types are categorical)
- **Pattern**: `default` or `type=atmtype` for atom type translation

**Example**: `mol.define ALA7,col4 ALA7,atoms,col4,ln1 1.0 default`

### Parameter File Operations (pam.)

Parameter file operations (pam.*) are the **recommended approach** for topology conversion as they provide greater flexibility and better integration with force field workflows.

#### pam.charge
```
pam.charge COU,atm1,divisor,line_specs parameter_section,column,line_range unit_conversion pattern
```

**Purpose**: Updates charges in parameter files (more flexible than molecule-based operations)

**Parameter Details**:
- **Source**: `COU,atm1,0.6645,ln8,ln12,ln16,ln20,ln24,ln28,ln32,ln36,ln40,ln44,ln48,ln52,ln56,ln60`
  - Extract from Coulomb section, first atom type, divide by 0.6645, specific lines
- **Destination**: `nonbond_params,col7,ln1-100`
  - Update nonbond_params section, column 7 (charges), lines 1-100
- **Unit conversion**: Typically `1.0` (charges are dimensionless)
- **Pattern**: `default` or `type=atmtype` for atom type mapping

**Alternative syntax**: `pam.charge file,charge_file parameter_section,column,line_range 1.0 type=atmtype`

**Examples**:
- `pam.charge COU,atm1,0.6645,ln1-40 nonbond_params,col7,ln1-100 1.0 default`
- `pam.charge file,charges.dat nonbond_params,col7,ln1-73 1.0 type=atmtype`

#### pam.nonbond
```
pam.nonbond OFF_section,column[,line_specs] parameter_section,column,line_range unit_conversion pattern
```

**Purpose**: Updates non-bonded parameters in parameter type definitions

**Parameter Details**:
- **Source**: `STRC,col3,ln1-20` or `EXP,col4` or `COU,col3,ln5,ln10,ln15`
  - Extract from Inter-Potential sections (STRC, EXP, SRD, POW, BUC, etc.)
  - Specify column and optional line ranges
- **Destination**: `nonbond_params,col4,ln1-100`
  - Update parameter section, specific column and line range
- **Unit conversion**: `4.184` for energy parameters, `1.0` for dimensionless
- **Pattern**: `default`, `type=atmtype`, or `no`

**Examples**:
- `pam.nonbond STRC,col3,ln1-20 nonbond_params,col4,ln1-100 4.184 default`
- `pam.nonbond EXP,col4 nonbond_params,col5,ln1-50 1.0 type=atmtype`

#### pam.bonded (pam.bond / pam.angle / pam.dih)
```
pam.bonded OFF_section,column parameter_section,column,line_range unit_conversion pattern
```

**Purpose**: Updates bonded parameter type definitions (bonds, angles, dihedrals)

**Parameter Details**:
- **Source**: `ALA7,col4` (from Molecular-Definition section)
  - Extract bonded parameters from specific molecule definition
- **Destination**: `bondtypes,col4,ln1-50` or `angletypes,col4,ln1-50` or `dihedraltypes,col7,ln1-8,ln10`
  - Update parameter type sections with force constants and equilibrium values
- **Unit conversion**: Various factors based on parameter type
  - `1.0`: Distances, angles (already in correct units)
  - `4.184`: Energy parameters (kcal/mol → kJ/mol)
  - `418.4`: Angle force constants (kcal/mol/rad² → kJ/mol/rad²)
- **Pattern**: `default`, `type=atmtype`, `extra:col5=col8` for additional columns

**Examples**:
- `pam.bond ALA7,col4 bondtypes,col4,ln1-50 1.0 default`
- `pam.angle ALA7,col4 angletypes,col4,ln1-50 1.0 type=atmtype`
- `pam.dih ALA7,col4 dihedraltypes,col7,ln1-8,ln10 1.0 extra:col5=col8`

### List Generation Operations (list.)

List generation operations create comprehensive interaction lists for force field parameter files, automatically enumerating all possible atom type combinations.

#### list.nonbond
```
list.nonbond exclusion_patterns parameter_section[,scaling_factors] pattern_options
```

**Purpose**: Generates comprehensive non-bonded interaction parameter lists

**Parameter Details**:
- **Exclusion patterns**: `HW~MW,HW~OW,HMM,MMM` or `HW:MW,HW:OW`
  - `~`: Exclude atom pair interactions
  - `:`: Alternative exclusion syntax
  - Multiple exclusions separated by commas
- **Parameter section**: `nonbond_params[,col1,factor1,factor2]`
  - `nonbond_params`: Target section name
  - Optional scaling factors for generated parameters
- **Pattern options**: `default`, `type=atmtype`

**Examples**:
- `list.nonbond HW~MW,HW~OW,HMM,MMM nonbond_params,1,1.0,1.0 default`
- `list.nonbond HW:MW,HW:OW nonbond_params type=atmtype`

**Function**: Enumerates all possible atom type pairs, excludes specified patterns, generates parameter lines with proper formatting.

#### list.bonded
```
list.bonded molecule_name parameter_section,function_type pattern_options
```

**Purpose**: Generates bonded interaction lists from molecular topology definitions

**Parameter Details**:
- **Molecule name**: `ALA7` or other molecule identifiers
  - Must match molecule name in OFF file Molecular-Definition section
- **Parameter section**: `bondtypes,1` or `angletypes,1` or `dihedraltypes,9`
  - Section name and function type number
  - Function type corresponds to GROMACS interaction types
- **Pattern options**: `type=atmtype`, `intkey=har`, `no`
  - `intkey=har`: Use harmonic interaction keywords
  - Other patterns for specialized processing

**Examples**:
- `list.bonded ALA7 bondtypes,1 type=atmtype,intkey=har`
- `list.bonded ALA7 angletypes,1 type=atmtype`
- `list.bonded ALA7 dihedraltypes,9 no`

**Function**: Analyzes molecular topology, extracts bonded interactions (bonds, angles, dihedrals), generates corresponding parameter type entries.

### Table Generation Operations (tab.)

Table generation operations create tabulated potential files (.xvg) for custom or non-standard interactions that cannot be expressed analytically.

#### tab.nonbond
```
tab.nonbond cutoff,spacing,line_specs pattern_options
```

**Purpose**: Generates tabulated potential files for non-bonded interactions

**Parameter Details**:
- **Grid specification**: `cutoff,spacing,line_specs`
  - `cutoff`: Maximum distance for table (Angstrom or nm)
  - `spacing`: Distance resolution (deltr)
  - `line_specs`: Line ranges from OFF file to process (ln1-10)
- **Pattern options**: `type=atmtype,prefix=name`, `scale=factor`, `default`
  - `prefix=name`: Add prefix to generated table file names
  - `scale=factor`: Apply scaling factors (e.g., scale=C6 for dispersion)
  - `type=atmtype`: Use atom type mapping

**Examples**:
- `tab.nonbond 12.0,0.01,ln1-20 type=atmtype,prefix=Ala7`
  - Generate tables up to 12 Å with 0.01 Å spacing, custom prefix
- `tab.nonbond 15.0,0.005,ln1-10 scale=C6`
  - High-resolution tables with C6 dispersion scaling
- `tab.nonbond 2,0.1,ln1-10 default`
  - Simple table generation with default settings

**Function**: Extracts potential parameters from OFF Table-Potential section, calls appropriate gentab_* scripts, generates .xvg files compatible with GROMACS tabulated potentials.

**Integration**: Generated tables are used via GROMACS energygrp-table mechanisms, enabling custom potential functions in MD simulations.

## Typical Workflows

### Basic OFF to Topology Conversion
1. Prepare protocol file defining conversion operations
2. Run `off2top protocol.off2top input.off template.top output.top`
3. Verify output topology file
4. Test in molecular dynamics simulation

### Tabulated Potential Generation
1. Prepare table protocol file
2. Run `off2tab protocol.off2tab input.off template.top`
3. Verify generated .xvg files
4. Update MDP files for table usage
5. Test tables in MD simulation

### Parameter File Workflow (Recommended)
1. Use pam.* operations instead of mol.* for better flexibility
2. Generate parameter types first
3. Create interaction lists
4. Generate required tables
5. Validate complete topology

### Custom Potential Implementation
1. Define potential in OFF Table-Potential section
2. Create table generation protocol
3. Use appropriate gentab_* script
4. Combine tables if multiple potential types
5. Update topology for table usage

## Integration with AFMTools

The off2top scripts integrate with the broader AFMTools ecosystem:

1. **Input**: Receives optimized parameters from AFM calculations via OFF files
2. **Processing**: Converts parameters to MD simulation-ready format
3. **Output**: Provides topology and table files for production MD runs
4. **Validation**: Supports simulation testing and parameter validation

## File Management

- **Temporary Files**: Uses `/tmp/tempoff2top.$$` for safe operations
- **Overwrite Protection**: Prevents accidental output file overwriting
- **Table Organization**: Systematic naming for generated table files
- **Backup Strategy**: Preserves original topology files during conversions

## Best Practices

1. **Protocol Validation**: Always validate protocol files before conversion
2. **Parameter Consistency**: Check parameter units and physical reasonableness
3. **Charge Neutrality**: Verify molecular electroneutrality
4. **File Backup**: Maintain backups of original topology files
5. **Testing**: Test converted topologies in short MD simulations
6. **Table Validation**: Check generated tables for continuity and correctness
7. **Documentation**: Document conversion protocols for reproducibility

## Common Use Cases

### Force Field Development
- Convert research parameters to production topology format
- Integrate new parameter types into existing force fields
- Update topology databases with optimized parameters

### Custom Potential Implementation
- Implement non-standard potential functions
- Generate tabulated potentials for complex interactions
- Combine multiple potential types for comprehensive models

### Multi-Scale Integration
- QM/MM parameter integration into topology files
- Scale-specific parameter selection
- Hierarchical force field construction

### Production Workflows
- Batch processing of multiple systems
- Automated topology generation pipelines
- Parameter optimization to production deployment

## Error Handling and Troubleshooting

- **File Access**: Check file permissions and paths
- **Format Validation**: Verify OFF and topology file formats
- **Parameter Ranges**: Validate parameter physical reasonableness
- **Charge Conservation**: Ensure molecular electroneutrality
- **Units**: Verify consistent unit systems throughout conversion
- **Table Continuity**: Check tabulated potentials for smoothness
- **Topology Integrity**: Validate topology file syntax

## Dependencies

- Perl with standard modules
- AFMTools core utilities (offget_*, etc.)
- GROMACS utilities (for table format compatibility)
- Compatible OFF and topology file formats
- Protocol file syntax compliance
- Mathematical libraries (for special functions)

## Supported MD Packages

While primarily designed for GROMACS, the topology conversion framework can be adapted for:
- **GROMACS**: Native support with .top/.itp files
- **LAMMPS**: Via format conversion utilities
- **NAMD**: Through parameter translation scripts
- **OpenMM**: Via topology conversion tools
- **CHARMM**: Through parameter mapping utilities

This documentation provides comprehensive guidance for using the scr_off2top scripts in force field parameter conversion workflows, enabling the translation of AFM-optimized parameters into production-ready molecular dynamics simulation input files.