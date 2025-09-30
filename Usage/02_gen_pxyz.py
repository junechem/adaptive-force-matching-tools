#!/usr/bin/env python3
"""Script for selecting QM or QM/MM configurations for AFM force field development.

Usage: ./02_gen_pxyz.py

This tool selects simple QM or QM/MM configurations for developing small molecule force fields 
with adaptive force matching. The script works with both neat and solvated systems, though for 
solvated systems only 1 solute molecule is expected.

MODIFICATION: This version extends the MM region from ALL QM molecules (both the center molecule 
with mark 4 and all QM fitting molecules with mark 3), providing better coverage around the 
entire QM region for improved force field fitting.

No matter what, the final .pxyz will have these solvation factors:
4 = first molecule that is marked up (center of QM region)
3 = QM fitting molecules
2 = QM buffer molecules (if only_qm = False)
1 = MM molecules (if only_qm = False)


Parameters that need to be defined are:
:neat: boolean, set to True if creating QM(/MM) selection on neat system
    If False, a solvated system selection will be assumed.
:only_qm: boolean, set to True if creating QM only configuration
    If False, a QM/MM configuration will be assumed
:solute: string, optional, set to name of solute if doing solvated system (neat=False)
:solvent: string, optional, set to name of solvent if doing solvated system (neat=False)
:qm_fitting_radius: float, radius in Angstrom around first selected molecule from which to
    select the QM fitting region molecules
:qm_fitting_molecules: integer, number of QM fitting molecules (excluding the first selected
    molecule)
:qm_buffer_radius: float, radius in Angstrom around all QM fitting molecules to comprise QM buffer
    region. Redundant if doing QM only fit.
:mm_region_radius: float, radius in Angstrom around ALL QM molecules (mark 3 and 4) that will 
    create MM molecules. Extends from both the center QM molecule (mark 4) and all QM fitting 
    molecules (mark 3). Does not affect previously selected QM fitting or buffer region molecules. 
    Redundant if doing QM only fit

Adjust the parameters in this script; no command line options are used so that previously
    used options can be preserved.


For more information on fitting force fields, or for examples of QM/MM and QM only fitting
protocols, see the following article.
https://doi.org/10.1038/s41598-025-06558-w
"""


import sys
import os
import subprocess
import shutil
import warnings
from random import choice
import re

neat = True  # If False, assume solvated system
only_qm = False  # If False, assume QM/MM configuration is desired
qm_fitting_radius = 3  # Angstroms
qm_fitting_molecules = 5  # Number of fitting molecules besides first selected molecule
qm_buffer_radius = mm_region_radius = solute = solvent = None

if not only_qm:
    qm_buffer_radius = 2.6  # Angstroms, distance from any QM fitting atom which will create QM
        # buffer molecules
    mm_region_radius = 9.0  # Angstroms, distance from solute which will make up MM molecules

if not neat:
    solute = "UNK"  # Replace with solute molname
    solvent = "SOL"  # Replace with solvent molname

parameters = {'neat': neat, 'only_qm': only_qm, 'qm_fitting_radius' : qm_fitting_radius, 'qm_fitting_molecules': qm_fitting_molecules, 'qm_buffer_radius': qm_buffer_radius, 'mm_region_radius': mm_region_radius, 'solute': solute, 'solvent': solvent}

class AFMConfigurationError(Exception):
    """Custom exception for AFM configuration validation errors."""
    pass


def check_type(**kwargs):
    """ Validate that all input parameters have the correct type

    Returns:
        None
    """

    type_mapping = {
    'neat': bool,
    'only_qm': bool,
    'solute': (str, type(None)),
    'solvent': (str, type(None)),
    'qm_fitting_radius': (int, float, type(None)),
    'qm_fitting_molecules': int,
    'qm_buffer_radius': (int, float, type(None)),
    'mm_region_radius': (int, float, type(None))
}
    for param_name, param_value in kwargs.items():
        if param_name in type_mapping:
            expected_type = type_mapping[param_name]
            if not isinstance(param_value, expected_type):
                raise AFMConfigurationError(
                    f"Parameter '{param_name}' must be of type {expected_type}, "
                    f"got {type(param_value).__name__}: {param_value}"
                )

def validate_dependencies():
    """Makes sure AFMTools are in the path

    Returns:
        None
    """
    required_tools = ["gro2pxyz"]

    for tool in required_tools:
        if not shutil.which(tool):
            raise AFMConfigurationError(
                f"AFMTools must be sourced/in the path to use this script. "
            )

def check_solute_solvent(**kwargs):
    """Checks solute, solvent types

    Returns:
        None
    """
    if not kwargs['neat']:
        if kwargs['solute'] is None:
            raise AFMConfigurationError(
                "For solvated systems (neat=False), 'solute' parameter must be provided"
            )
        if kwargs['solvent'] is None:
            raise AFMConfigurationError(
                "For solvated systems (neat=False), 'solvent' parameter must be provided"
            )
        if kwargs['solute'] == kwargs['solvent']:
            raise AFMConfigurationError(
                "For solvated systems (neat=False), 'solute' and 'solvent' must be different"
            )

def check_radii(**kwargs):
    """Make sure reasonable parameters are used for qm_fitting_radius and mm_region_radius

    Returns:
        None
    """
    if not kwargs['only_qm']:
        min_recommended_ratio = 0.5
        actual_ratio = kwargs['qm_fitting_radius']/kwargs['mm_region_radius']
        if (actual_ratio >= min_recommended_ratio) and (actual_ratio < 1):
            warnings.warn(
                f"\n{'='*60}\n"
                f"WARNING: qm_fitting_radius ({qm_fitting_radius:.2f} Å) should be at least 50% "
                f"smaller than mm_region_radius ({mm_region_radius:.2f} Å).\n"
                f"Current ratio: {actual_ratio:.2f} (recommended: < {min_recommended_ratio:.2f})\n"
                f"This may lead to suboptimal QM/MM partitioning.\n"
                f"{'='*60}",
                UserWarning,
                stacklevel=2
            )


        if actual_ratio >= 1:
            raise AFMConfigurationError(
                "For QM/MM systems (only_qm=False), qm_fitting_radius must be smaller than "
                "mm_region_radius"
            )



def get_grofiles():
    """Gets list of gro files.

    Return:
        List of grofile paths
    """
    filenames = subprocess.run('ls -d1 01_grofiles/*gro', text=True, shell=True, check=True,
        capture_output=True)
    return filenames.stdout.strip().split('\n')


def check_neat(grofile, **kwargs):
    """Depending on if the user chose neat= (True or False), check to see if it is true.


    Returns:
        None
    """

    subprocess.run(f'gro2pxyz {grofile} > check_neat.pxyz', shell=True, check=True)
    cleaned_strings = set()

    with open('check_neat.pxyz') as f:
        for line in f:
            fields = line.split()
            if len(fields) >= 5:
                # Remove digits from 5th column
                cleaned = re.sub(r'\d+', '', fields[4]).strip()
                if cleaned:
                    cleaned_strings.add(cleaned)
    num_moltypes = len(cleaned_strings)
    subprocess.run(['rm', 'check_neat.pxyz'], check=True)

    if kwargs['neat']:
        if num_moltypes != 1:
            raise AFMConfigurationError(
            "Detecting more than one molecule type even though you chose \"neat=True\". Check "
                "your input"
            )
    else:
        if num_moltypes < 2:
            raise AFMConfigurationError(
            "Detecting only one molecule type even though you chose \"neat=False\". Check "
                "your input"
            )
            sys.exit(1)



def get_natms_per_mol(grofile, **kwargs):
    """Gets number of atoms in the solute, solvent.

    If neat = True, solvent = solute

    Returns:
        solute_natms, solvent_natms
    """
    if kwargs['neat']:
        solute = subprocess.run(f'gro2pxyz {grofile} | markup_random -9 4 | pxyz_select 4 | wc -l',
            shell=True, text=True, check=True, capture_output=True).stdout.strip().split('\n')[0]
        solvent = solute
    else:
        solute_name = kwargs['solute']
        solvent_name = kwargs['solvent']
        solute = subprocess.run(f'gro2pxyz {grofile} | mark_byname {solute_name} 4 | '
            'pxyz_select 4 | wc -l ', shell=True, text=True, capture_output=True, check=True
        ).stdout.split('\n')[0]
        solvent = subprocess.run(f'gro2pxyz {grofile} | mark_byname {solvent_name} 4 | '
            'pxyz_select 4 | xyz_add_linenu | markup_random 4 5 | pxyz_select 5 | wc -l',
            shell=True, text=True, capture_output=True, check=True
        ).stdout.strip().split('\n')[0]

    return solute, solvent


def mark_center(filename, **kwargs):
    """ Marks the middle of the QM region (the first molecule)

    Returns:
        None
    """
    if kwargs['neat']:
        subprocess.run(f'gro2pxyz {filename} | markup_random -9 4 | pxyz_sort '
        '| pxyz_recenter 1 > marked_center.pxyz', shell=True, check=True)
    elif not kwargs['neat']:
        solute = kwargs['solute']
        subprocess.run(f'gro2pxyz {filename} | mark_byname {solute} 4 | pxyz_sort | '
        'pxyz_recenter 1 > marked_center.pxyz', shell=True, check=True)


def mark_qm_fitting(**kwargs):
    """Marks QM fitting region

    Returns:
        None
    """
    marked_atoms = 0
    qm_fitting_radius = kwargs['qm_fitting_radius']
    qm_fitting_molecules = kwargs['qm_fitting_molecules']

    subprocess.run(f'mark_boundary {qm_fitting_radius} 4 2 marked_center.pxyz',
        shell=True, check=True)
    for i in range(0, int(qm_fitting_molecules)):
        subprocess.run(f'markup_random 2 3 marked_center.pxyz > marked.pxyz && '
            'mv marked.pxyz marked_center.pxyz', shell=True, check=True)

def check_qm_fitting_natms():
    """Counts number of QM fitting atoms in marked_center.pxyz

    Returns:
        None
    """
    return subprocess.run('awk \'$6 == 4 || $6 == 3 {{total++}} END {{print total}}\' '
        'marked_center.pxyz', shell=True, check=True, text=True, capture_output=True
        ).stdout.strip().split('\n')[0]


def mark_qm_buffer(**kwargs):
    """Mark QM buffer region (if needed)

    Returns:
        None
    """
    if not kwargs['only_qm']:
        qm_buffer_radius = kwargs['qm_buffer_radius']
        subprocess.run(f'mark_boundary {qm_buffer_radius} 3 2 marked_center.pxyz',
            shell=True, check=True)
    else:
        pass


def mark_mm(**kwargs):
    """Mark MM region (if needed)
    
    The MM region extends from ALL QM molecules (both mark 4 and mark 3) within 
    mm_region_radius. This ensures complete coverage around the entire QM region.

    Returns:
        None
    """
    if not kwargs['only_qm']:
        mm_region_radius = kwargs['mm_region_radius']
        # Mark MM region extending from molecules with mark value 4 (center QM molecule)
        subprocess.run(f'mark_boundary {mm_region_radius} 4 1 marked_center.pxyz',
            shell=True, check=True)
        # Mark MM region extending from molecules with mark value 3 (QM fitting molecules)
        subprocess.run(f'mark_boundary {mm_region_radius} 3 1 marked_center.pxyz',
            shell=True, check=True)

def dropoff_extra(**kwargs):
    """Removes all solvation factors at or below 0

    Returns:
        None
    """
    if not kwargs['only_qm']:
        subprocess.run(f'pxyz_dropoff 0 marked_center.pxyz | pxyz_sort > completed.pxyz',
            shell=True, check=True)
    else:
        subprocess.run(f'pxyz_dropoff 2 marked_center.pxyz | pxyz_sort > completed.pxyz',
            shell=True, check=True)


def make_filename(num_zeros, file_number):
    """Makes filename for specific configuration

    Returns:
        :filename:  string
    """
    return "02_pxyz_files/" + f"final{file_number:0{num_zeros}d}" + ".pxyz"

def move_and_clean(filename):
    """Moves QM(/MM) configuration file to proper location and cleans extra files


    Returns:
        None
    """

    subprocess.run(f'mv completed.pxyz {filename} && rm marked_center.pxyz',
        shell=True, check=True)





if __name__ == '__main__':
    validate_dependencies()
    check_type(**parameters)
    check_solute_solvent(**parameters)
    check_radii(**parameters)
    file_list = get_grofiles()
    number_of_zeros = len(str(len(file_list)))
    number_of_gro = len(file_list)
    completed_gro = []
    random_gro = choice(file_list)
    check_neat(random_gro, **parameters)
    print("All Checks Completed\n")
    print("Beginning QM(/MM) Selection...\n")
    # Get number of atoms per solute, solvent for checking
    solute_natms, solvent_natms = [int(i) for i in get_natms_per_mol(random_gro, **parameters)]
    expected_fitting = solute_natms + solvent_natms*parameters['qm_fitting_molecules']
    iterations = 0
    while len(completed_gro) != number_of_gro:
        if iterations > 3000:
            print("Cannot create all configurations with current settings. Please adjust settings")
            sys.exit(1)
        grofile = choice(file_list)
        mark_center(grofile, **parameters)
        mark_qm_fitting(**parameters)
        total_qm_fitting = check_qm_fitting_natms()
        if int(total_qm_fitting) != int(expected_fitting):  # Check if not enough QM fitting atoms are selected
            warnings.warn(
                f"WARNING: Could not mark up {expected_fitting} atoms for the QM fitting regions. "
                "Skipping this configuration...",
                UserWarning,
                stacklevel=2
            )
            subprocess.run('rm marked_center.pxyz', shell=True, check=True)
            iterations += 1
            continue
        mark_qm_buffer(**parameters)
        mark_mm(**parameters)
        dropoff_extra(**parameters)
        filename = make_filename(number_of_zeros, len(completed_gro))
        move_and_clean(filename)
        completed_gro.append(grofile)
        file_list.remove(grofile)
        iterations += 1




