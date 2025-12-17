#!/usr/bin/env python3
"""
xyz_add_gen_msite - Generalized M-site Addition Tool

Adds M-site virtual atoms to .ref files based on user-defined patterns.
"""

import sys

def print_help():
    """Print help message."""
    print("""
=== xyz_add_gen_msite - Generalized M-site Addition ===

PURPOSE:
  Add M-site virtual atoms based on a user-defined definition file.
  Calculates M-site positions as a weighted average of specified atoms.

USAGE:
  xyz_add_gen_msite <msite_definition_file> [input_ref_file]

  Example: xyz_add_gen_msite msite_def system.ref > system_with_msites.ref

  If input_ref_file is not provided, reads from stdin.

M-SITE DEFINITION FILE FORMAT:
  The definition file consists of 3-line blocks defining M-site rules:

  Line 1: <MoleculeType> (e.g., DMA, DMM)
  Line 2: <Atom1> <Atom2> ... <AtomN> <MSiteName>
  Line 3: <Coeff1> <Coeff2> ... <CoeffN>

  Example:
    DMA
    C1 H2 C1 EM
    0.2 0.2 0.2

DETAILS:
  - Patterns are matched within each molecule instance
  - For repeated atom names (e.g., C1 H2 C1), the script finds the 1st C1,
    1st H2, and 2nd C1 within that molecule
  - M-site position = sum(coefficient[i] * atom_position[i])
  - M-sites are inserted after the atoms of each molecule
""")

def parse_msite_definitions(def_file):
    """Parse M-site definition file and return list of definitions."""
    definitions = []

    with open(def_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    i = 0
    while i < len(lines):
        if i + 2 >= len(lines):
            break

        mol_type = lines[i]
        pattern_parts = lines[i + 1].split()
        coeff_parts = lines[i + 2].split()

        if len(pattern_parts) < 2:
            print(f"Warning: Invalid pattern line for {mol_type}", file=sys.stderr)
            i += 3
            continue

        atom_names = pattern_parts[:-1]
        msite_name = pattern_parts[-1]

        try:
            coefficients = [float(c) for c in coeff_parts]
        except ValueError:
            print(f"Warning: Invalid coefficients for {mol_type}", file=sys.stderr)
            i += 3
            continue

        if len(coefficients) != len(atom_names):
            print(f"Warning: Coefficient count mismatch for {mol_type}", file=sys.stderr)
            i += 3
            continue

        definitions.append({
            'mol_type': mol_type,
            'atom_names': atom_names,
            'msite_name': msite_name,
            'coefficients': coefficients
        })

        i += 3

    return definitions

def get_molecule_id(line):
    """Extract molecule ID from a line (last field)."""
    parts = line.split()
    if len(parts) >= 8:
        # Atom lines have at least 8 fields
        return parts[-1]
    return None

def is_atom_line(line):
    """Check if line is an atom line (has coordinates)."""
    parts = line.split()
    if len(parts) < 4:
        return False
    # Try to parse coordinates
    try:
        float(parts[1])
        float(parts[2])
        float(parts[3])
        return True
    except (ValueError, IndexError):
        return False

def find_pattern_in_molecule(atoms, pattern):
    """
    Find pattern atoms in molecule.

    Args:
        atoms: List of dicts with 'name', 'x', 'y', 'z'
        pattern: List of atom names to find (e.g., ['C1', 'H2', 'C1'])

    Returns:
        List of atom dicts in pattern order, or None if pattern not found
    """
    # Count how many of each atom name we need
    needed_counts = {}
    for name in pattern:
        needed_counts[name] = needed_counts.get(name, 0) + 1

    # Track which occurrence of each atom name we need
    pattern_occurrences = []
    seen_counts = {}
    for name in pattern:
        seen_counts[name] = seen_counts.get(name, 0) + 1
        pattern_occurrences.append((name, seen_counts[name]))

    # Find the atoms
    found_atoms = [None] * len(pattern)
    atom_counts = {}

    for atom in atoms:
        name = atom['name']
        if name in needed_counts:
            atom_counts[name] = atom_counts.get(name, 0) + 1
            current_occurrence = atom_counts[name]

            # Check if this is one of the pattern atoms we need
            for i, (pattern_name, needed_occurrence) in enumerate(pattern_occurrences):
                if pattern_name == name and needed_occurrence == current_occurrence:
                    if found_atoms[i] is None:
                        found_atoms[i] = atom
                    break

    # Check if we found all atoms
    if all(atom is not None for atom in found_atoms):
        return found_atoms
    return None

def process_molecule(mol_lines, definitions):
    """
    Process a molecule's lines and add M-sites.

    Args:
        mol_lines: List of lines belonging to one molecule
        definitions: List of M-site definitions

    Returns:
        List of output lines with M-sites added
    """
    # Parse atoms from molecule
    atoms = []
    atom_line_indices = []

    for i, line in enumerate(mol_lines):
        if is_atom_line(line):
            parts = line.split()
            atoms.append({
                'name': parts[0],
                'x': float(parts[1]),
                'y': float(parts[2]),
                'z': float(parts[3]),
                'line_index': i
            })
            atom_line_indices.append(i)

    # Start with original lines
    output_lines = list(mol_lines)
    insertions = []  # Track (index, line) to insert

    # Try each definition
    for defn in definitions:
        pattern_atoms = find_pattern_in_molecule(atoms, defn['atom_names'])

        if pattern_atoms:
            # Calculate M-site position
            mx = sum(defn['coefficients'][i] * atom['x'] for i, atom in enumerate(pattern_atoms))
            my = sum(defn['coefficients'][i] * atom['y'] for i, atom in enumerate(pattern_atoms))
            mz = sum(defn['coefficients'][i] * atom['z'] for i, atom in enumerate(pattern_atoms))

            # Format M-site line to match atom line format
            # Extract other fields from last atom in pattern
            last_pattern_atom = pattern_atoms[-1]
            last_pattern_atom_line = mol_lines[last_pattern_atom['line_index']]
            parts = last_pattern_atom_line.split()

            # Build M-site line with same format: NAME X Y Z (and copy remaining fields)
            if len(parts) >= 8:
                # Copy forces, mass, mol_id from template
                msite_line = f"{defn['msite_name']:<8s} {mx:11.7f} {my:11.7f} {mz:11.7f}"
                # Add zero forces and copy mass and mol_id
                msite_line += f"     0.0000000     0.0000000     0.0000000     {parts[7]}     {parts[8]}\n"
            else:
                msite_line = f"{defn['msite_name']:<8s} {mx:11.7f} {my:11.7f} {mz:11.7f}\n"

            # Insert after last atom in pattern (not last atom in molecule)
            insert_index = last_pattern_atom['line_index'] + 1
            insertions.append((insert_index, msite_line))

    # Insert M-sites (reverse order to maintain indices)
    for index, line in reversed(insertions):
        output_lines.insert(index, line)

    return output_lines

def main():
    """Main function."""
    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)

    def_file = sys.argv[1]
    input_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Parse definitions
    try:
        definitions = parse_msite_definitions(def_file)
    except Exception as e:
        print(f"Error reading definition file: {e}", file=sys.stderr)
        sys.exit(1)

    if not definitions:
        print("Warning: No M-site definitions found", file=sys.stderr)

    # Open input
    if input_file:
        try:
            f = open(input_file, 'r')
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        f = sys.stdin

    # Process input file
    current_mol_id = None
    current_mol_lines = []
    header_mode = True

    for line in f:
        mol_id = get_molecule_id(line)

        # Detect end of header (first line with molecule ID)
        if header_mode and mol_id is not None:
            header_mode = False

        # In header mode, just output the line
        if header_mode:
            sys.stdout.write(line)
            continue

        # Group by molecule ID
        if mol_id == current_mol_id:
            # Same molecule, accumulate
            current_mol_lines.append(line)
        else:
            # New molecule or non-molecule line
            if current_mol_lines:
                # Process previous molecule
                output_lines = process_molecule(current_mol_lines, definitions)
                for out_line in output_lines:
                    sys.stdout.write(out_line)

            # Start new molecule or output non-molecule line
            if mol_id is not None:
                current_mol_id = mol_id
                current_mol_lines = [line]
            else:
                # Line without molecule ID (shouldn't happen after header)
                sys.stdout.write(line)
                current_mol_lines = []
                current_mol_id = None

    # Process last molecule
    if current_mol_lines:
        output_lines = process_molecule(current_mol_lines, definitions)
        for out_line in output_lines:
            sys.stdout.write(out_line)

    if f != sys.stdin:
        f.close()

if __name__ == '__main__':
    main()
