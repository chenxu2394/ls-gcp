#!/bin/bash
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --account project_2012524
#SBATCH --partition medium

srun batch_hpc.sh
