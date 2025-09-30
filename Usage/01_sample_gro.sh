#!/bin/bash
echo "0 0" | gmx_d trjconv -f traj_comp.xtc -s topol.tpr -n index.ndx -split 2.5 -b 102.5 -dt 2.5 -o 01_grofiles/final.gro -nzero 3 -pbc mol -center
