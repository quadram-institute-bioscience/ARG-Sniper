#!/bin/bash
#SBATCH -t 1-00:00
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -J ARG-Sniper
#SBATCH --mail-type=end
#SBATCH --mail-user=zaf24vof@nbi.ac.uk
#SBATCH -o /hpc-home/zaf24vof/logs/%x_%j_results.txt
#SBATCH -e /hpc-home/zaf24vof/logs/%x_%j_error.txt
#SBATCH -p qib-medium

source activate nextflow
export NXF_OFFLINE=true &&
export NXF_SINGULARITY_HOME_MOUNT=true &&
nextflow run /hpc-home/zaf24vof/Documents/ARG-Sniper/ARG-Sniper-pipeline.nf\
 -with-report \
 -profile qib
