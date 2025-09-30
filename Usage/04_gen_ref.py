#!/usr/bin/env python3
"""Script related to creating final .ref files using ORCA forces.

Usage: ./04_gen_ref.py

This tool will generate ref files in the 04_ref_files directory using .pxyz files in 02_pxyz_files
 (output from 02_gen_pxyz.py) and MyMol.engrad files in 03_force_calculations/ subdirectories.

This tool expects a number of files:
    04_ref_files/molinfo
    02_pxyz_files/*pxyz
    03_force_calculations/final* (directories)
    03_force_calculations/final*/MyMol.engrad (files)
    03_force_calculations/name_translation
    03_force_calculations/charge_info (If MM region is used)

name_translation and charge_info have been documented in the 03_gen_force_input.py script and do
 not need to be reiterated here.

The format of the molinfo file must match one of the following 2 formats.

If the system is Neat:
-------
REPLACE
15 UNK  1.0
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
-------

Where the "15", atom types, and "UNK" may change depending on your molecule and molname.

If the system is hydrated:
-------
REPLACE
15 UNK  1.0
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
-------

Where "OW3", "OW2", "OW1" should be replaced with whatever atom name your first Fitting, Buffer, MM
 atoms are, while the "3, 2, 1" are the same, and obviously update molnames, atom types, and atom
 numbers where necessary.

"""


import os
import subprocess
import shutil
from pathlib import Path


class AFMRefFileError(Exception):
    """Custom exception for AFM Ref File validation errors"""


def validate_dependencies():
    """Makes sure AFMTools are in the path

    Returns:
        None
    """
    required_tools = ["gro2pxyz"]

    for tool in required_tools:
        if not shutil.which(tool):
            raise AFMRefFileError(
                "AFMTools must be sourced/in the path to use this script. "
            )


def get_pxyzfiles():
    """Gets list of pxyz files.

    Return:
        List of pxyz file paths
    """
    filenames = subprocess.run('ls -d1 02_pxyz_files/*pxyz', text=True, shell=True, check=True,
        capture_output=True)
    return filenames.stdout.strip().split('\n')


def get_dirnames(files):
    """Returns list of directories which contain MyMol.engrad directories


    Returns:
        list
    """

    force_dir = "03_force_calculations/"
    return [force_dir + Path(i).stem for i in files]


def check_for_mm(pxyz_file):
    """Checks if the pxyz files will contain MM region molecules (solvation factor 1)

    Returns:
        boolean, True if contains MM molecules, False if no MM molecules
    """
    mm_mols = len(subprocess.run(f'pxyz_select 1 {pxyz_file}', text=True, shell=True, check=True,
        capture_output=True).stdout.strip())

    if mm_mols > 0:
        contains_mm = True
    else:
        contains_mm = False
    return contains_mm


def check_for_files(contains_mm):
    """Checks if necessary files exist to produce orca input

    Returns:
        None
    """
    force_dir = "03_force_calculations/"
    files_to_check = [force_dir + "name_translation", force_dir + "charge_info"]
    if not contains_mm:
        files_to_check = files_to_check[:-1]
    for file in files_to_check:
        if not os.path.exists(file):
            raise AFMRefFileError(
                f"Necessary file {file} is missing. This should be present from when you ran "
                f" ./03_gen_force_input.py ; something is seriously wrong, check your work"
            )


def get_pxyz_atoms():
    """Gets atoms from first row of name_translation file

    Returns:
        list of pxyz atoms
    """
    with open('03_force_calculations/name_translation', 'r') as f:
        prefixes = [line.split()[0] for line in f if line.strip()]
    return prefixes


def get_mm_atoms():
    """Gets mm atoms from first row of charge_info file

    Returns:
        list of mm atoms
    """
    with open('03_force_calculations/charge_info', 'r') as f:
        prefixes = [line.split()[0] for line in f if line.strip()]
    return prefixes


def remove_msite(qm_atoms, mm_atoms):
    """Removes the msite, returns a list of all other atoms.

    It is assumed that any atoms in mm_atoms that are not in qm_atoms are m-site atoms.

    Returns:
        list of all atoms excluding m-sites
    """
    l1, l2 = set(qm_atoms), set(mm_atoms)

    return list(l1.union(l1 & l2))

def select_atoms(atom_list, pxyz_file):
    """Selects atoms from .pxyz file which are in the provided list

    Returns:
        None
    """
    matched_lines = []
    with open(pxyz_file, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if any(stripped_line.startswith(atom) for atom in atom_list):
                matched_lines.append(line)

    with open('matched.pxyz', 'w') as out:
        out.writelines(matched_lines)
    subprocess.run(f'xyz_add_linenu matched.pxyz > real_atoms.pxyz', shell=True, check=True)
    subprocess.run('rm matched.pxyz', shell=True, check=True)


def ref_gen_step1(contains_mm):
    """Generate first part of .ref file

    Returns:
        None
    """

    if not contains_mm:
        subprocess.run(f'tail -n+3 real_atoms.pxyz | ref_gen_step1_cord 04_ref_files/molinfo > '
        'step1.ref', shell=True, check=True)
    else:
        subprocess.run(f'pxyz_2vxyz real_atoms.pxyz | tail -n+3 | ref_gen_step1_cord '
        '04_ref_files/molinfo > step1.ref', shell=True, check=True)


def ref_upd_forces(dirname):
    """Updates forces in .ref file

    Returns:
        None
    """

    subprocess.run(f'ref_upd_orca_grad {dirname}/MyMol.engrad step1.ref | '
        'ref_upd_net > add_netf.ref', shell=True, check=True)


def add_fix_msite(contains_mm, dirname):
    """Adds and fixes m-sites where necessary if needed and creates final ref file

    Returns:
        None
    """

    file_name = Path(dirname).stem + '.ref'
    if contains_mm:
        subprocess.run('xyz_add_msite Ow Hw Hw Ew add_netf.ref | ref_fix_msite Ew |'
            'xyz_add_msite Omm Hmm Hmm Emm | ref_fix_msite Emm | xyz_fix_linenu > '
            f'{file_name}', shell=True, check=True)
    else:
        subprocess.run(f'xyz_fix_linenu add_netf.ref > {file_name}', shell=True, check=True)

    subprocess.run(f'mv {file_name} 04_ref_files', shell=True, check=True)


def remove_files():
    """Removes real_atoms.pxyz, step1.ref, add_netf.ref

    Returns:
        None
    """

    subprocess.run('rm real_atoms.pxyz step1.ref add_netf.ref', shell=True, check=True)







if __name__ == '__main__':
    validate_dependencies()
    pxyz_files = get_pxyzfiles()
    directory_names = get_dirnames(pxyz_files)
    contains_mm = check_for_mm(pxyz_files[0])
    check_for_files(contains_mm)
    print(f'Checks completed. Generating {len(pxyz_files)} .ref files...\n')
    qm_atoms = get_pxyz_atoms()
    if contains_mm:
        mm_atoms = get_mm_atoms()
    else:
        mm_atoms = []
    non_msite_atoms = remove_msite(qm_atoms, mm_atoms)
    for file, dirname in zip(pxyz_files, directory_names):
        select_atoms(non_msite_atoms, file)
        ref_gen_step1(contains_mm)
        ref_upd_forces(dirname)
        add_fix_msite(contains_mm, dirname)
        remove_files()
    print('Done generating .ref files\n')
