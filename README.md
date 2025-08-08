# ARG-Sniper

A Nextflow pipeline for antibiotic resistance gene detection from paired-end sequencing reads.

## Introduction

ARG-Sniper is a Nextflow DSL-2 pipeline designed for metagenomic analysis that processes paired-end FASTQ files to detect antibiotic resistance genes using multiple bioinformatics tools. The pipeline runs five different analysis tools in parallel: GROOT, ARIBA, KMA (via ARGprofiler), KARGA, and SRST2, each requiring their respective databases.
Users can selectively skip any of the five tools using command-line flags (--skip_groot, --skip_ariba, etc.), allowing for customized analysis workflows. The pipeline takes FASTQ files matching the pattern *_R{1,2}.fastq.gz and processes them through the selected tools.
After individual tool execution, the pipeline collects all results and generates a summary report that consolidates findings from each analysis. The workflow outputs separate directories for each tool's results along with a final summary directory containing the integrated analysis.

Note: This pipeline focuses on detecting antibiotic resistance genes and does not report SNP-based resistance mechanisms.


## How-2-Run
Before running the pipeline make sure all the required databases and tool-dependencies were met.

### Software Requirements
- **Nextflow** (≥22.04.0) with DSL-2 support
- **Singularity** container runtime

### Bioinformatics Tools (via Singularity containers)
- **SRST2** v2.0.0 - Short Read Sequence Typing
- **GROOT** v1.1.2 - Graph-based resistance gene detection  
- **ARIBA** v2.14.6 - Antimicrobial Resistance Identification
- **KARGA** v1.02 - K-mer based resistance gene analysis
- **KMA** v1.4.9 - K-mer alignment tool (used by ARGprofiler)

### Required Databases
All tools require pre-built databases from the panARG v2 collection:
- grootdb (indexed database)
- aribadb (prepared database)
- srst2db (FASTA sequences)
- kargadb (FASTA sequences) 
- argprofilerdb (KMA indexed database)
- panARG annotations (TSV metadata file)

### System Requirements
- **CPU:** 8 cores (default)
- **Memory:** 16 GB RAM (default)
- **Scheduler:** SLURM (for HPC execution)

### Usage

Run `--help` to see available options:

```bash
nextflow run ARG-sniper/main.nf --help
```

```
Usage:
    nextflow run ARG-Sniper-pipeline.nf --offline -with-report <ARGUMENTS>

Required Arguments:
    Input:
        --reads           Folder containing reads with file name *_R{1,2}.fastq.gz
        --gootdb          Path of indexed GROOT database
        --aribadb         Path to ARIBA database
        --kargadb         Path to KARG database
        --srst2db         Path to SRST2 database
        --argprofilerdb   Path to ARGprofiler database
        --output          Folder for output files

# By default, the pipeline will run all supported tools.
Optional Arguments:
    Skipping specific tools:
        --skip_groot      Skip running GROOT
        --skip_kma        Skip running KMA
        --skip_ariba      Skip running ARIBA
        --skip_karga      Skip running KARGA
        --skip_srst2      Skip running SRST2
```
