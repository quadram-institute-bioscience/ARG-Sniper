# ARG-Sniper

A Nextflow pipeline for antibiotic resistance gene detection from paired-end sequencing reads.

## Introduction

ARG-Sniper is a Nextflow DSL-2 pipeline designed for metagenomic analysis that processes paired-end FASTQ files to detect antibiotic resistance genes using multiple bioinformatics tools. The pipeline runs five different analysis tools in parallel: GROOT, ARIBA, KMA (adopted from ARGprofiler), KARGA, and SRST2, each requiring their respective databases.
Users can selectively skip any of the five tools using command-line flags (--skip_groot, --skip_ariba, etc.), allowing for customized analysis workflows. The pipeline takes FASTQ and processes them through the selected tools.
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
## Expected Output

Upon successful execution with all tools, ARG-Sniper generates the following directory structure with results for each sample:

```
results/
├── argprofiler_results/
│   └── ARGprofiler_report_{sample}.txt
├── ariba_results/
│   ├── ariba_report_{sample}.tsv
│   └── ariba_summary_{sample}.csv
├── groot_results/
│   └── groot_report_{sample}.tsv
├── karga_results/
│   └── karga_report_{sample}.csv
├── srst2_results/
│   └── srst2_report_{sample}_fullgenes_sequence_results.txt
└── summary/
    └── summary_{sample}.tsv
```

**Example output for multiple samples:**
```
results/
├── argprofiler_results/
│   ├── ARGprofiler_report_dataset-100x-depth.txt
│   ├── ARGprofiler_report_dataset-90x-depth.txt
│   └── ARGprofiler_report_dataset-95x-depth.txt
├── ariba_results/
│   ├── ariba_report_dataset-100x-depth.tsv
│   ├── ariba_report_dataset-90x-depth.tsv
│   ├── ariba_report_dataset-95x-depth.tsv
│   ├── ariba_summary_dataset-100x-depth.csv
│   ├── ariba_summary_dataset-90x-depth.csv
│   └── ariba_summary_dataset-95x-depth.csv
├── groot_results/
│   ├── groot_report_dataset-100x-depth.tsv
│   ├── groot_report_dataset-90x-depth.tsv
│   └── groot_report_dataset-95x-depth.tsv
├── karga_results/
│   ├── karga_report_dataset-100x-depth.csv
│   ├── karga_report_dataset-90x-depth.csv
│   └── karga_report_dataset-95x-depth.csv
├── srst2_results/
│   ├── srst2_report_dataset-100x-depth_fullgenes_sequence_results.txt
│   ├── srst2_report_dataset-90x-depth_fullgenes_sequence_results.txt
│   └── srst2_report_dataset-95x-depth_fullgenes_sequence_results.txt
└── summary/
    ├── summary_dataset-100x-depth.tsv
    ├── summary_dataset-90x-depth.tsv
    └── summary_dataset-95x-depth.tsv
```

The `summary/` directory contains consolidated results from all tools for each sample.