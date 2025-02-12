#!/bin/bash
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --account project_2012524
#SBATCH --partition medium

bash batch_hpc.sh
