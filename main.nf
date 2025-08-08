#!/usr/bin/env nextflow

//1. DSL: Using DSL-2
nextflow.enable.dsl=2

//2. Default parameters: All of the default parameters are being set in `nextflow.config`

//3. if `true` this prevents a warning of undefined parameter 
params.help = false

//4. Help menu: Function which prints help message text
log.info """
QIB: NF ARG-SNIPER (by default)
=====================================
reads               : ${params.reads}
grootdb             : ${params.grootdb}
aribadb             : ${params.aribadb}
kargadb             : ${params.kargadb}
srst2db             : ${params.srst2db}
argprofilerdb       : ${params.argprofilerdb}
groot_cov           : ${params.groot_cov}
output              : ${params.output}
work_dir            : ${params.work_dir}
metadata_file       : ${params.metadata_file}
"""
.stripIndent()
//4. 1 Help if --help is specified.

def helpMessage() {
    log.info """
Usage:
    nextflow run ARG-Sniper-pipeline.nf --offline -with-report <ARGUMENTS>

Required Arguments:
    Input:
        --reads       Folder containing reads with file name *_R{1,2}.fastq.gz
        --gootdb      Path of indexed GROOT database
        --aribadb     Path to ARIBA database
        --kargadb     Path to KARG database
        --srst2db     Path to SRST2 database
        --argprofilerdb Path to ARGprofiler database
        --output      Folder for output files

# By default, the pipeline will run all supported tools.
Optional Arguments:
    Skipping specific tools:
        --skip_groot      Skip running GROOT
        --skip_kma        Skip running KMA
        --skip_ariba      Skip running ARIBA
        --skip_karga      Skip running KARGA
        --skip_srst2      Skip running SRST2
"""
}

// Show help message if the user specifies the --help flag at runtime
if ( params.help ){
    // Invoke the function above which prints the help message
    helpMessage()
    // Exit out and do not run anything else
    exit 1
}
/*
 * Defining the output folders. if required, then
 */
grootOutputDir = "${params.output}/groot_results"
aribaOutputDir = "${params.output}/ariba_results"
srst2OutputDir = "${params.output}/srst2_results"
kargaOutputDir = "${params.output}/karga_results"
argprofilerOutputDir = "${params.output}/argprofiler_results"
argSummaryOutputDir = "${params.output}/summary"


//5. IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS / WORKFLOWS
include { groot_align } from './modules/groot' addParams(OUTPUT: grootOutputDir)
include { ariba_run } from './modules/ariba' addParams(OUTPUT: aribaOutputDir)
include { ariba_summary } from './modules/ariba' addParams(OUTPUT: aribaOutputDir)
include { srst2 } from './modules/srst2' addParams(OUTPUT: srst2OutputDir)
include { karga } from './modules/karga' addParams(OUTPUT: kargaOutputDir)
include { kma_align } from './modules/argprofiler' addParams(OUTPUT: argprofilerOutputDir)
include { summarize_results } from './modules/summary' addParams(OUTPUT: argSummaryOutputDir)


// Define the pattern which will be used to find the FASTQ files
fastq_pattern = "${params.reads}"

// Set up a channel from the pairs of files found with that pattern
fastq_ch = Channel
    .fromFilePairs(fastq_pattern, flat: true)
    .ifEmpty { error "No files found matching the pattern ${fastq_pattern}" }

// Main workflow
// Set default values to skip a tool default: run all
params.skip_groot = false
params.skip_kma = false
params.skip_ariba = false
params.skip_karga = false
params.skip_srst2 = false

workflow {

    groot_ch = params.skip_groot ? Channel.empty() : groot_align(fastq_ch)
    kma_ch = params.skip_kma ? Channel.empty() : kma_align(fastq_ch)
    ariba_ch = params.skip_ariba ? Channel.empty() : ariba_run(fastq_ch)
    ariba_summary_ch = params.skip_ariba ? Channel.empty() : ariba_summary(ariba_ch)
    karga_ch = params.skip_karga ? Channel.empty() : karga(fastq_ch)
    srst2_ch = params.skip_srst2 ? Channel.empty() : srst2(fastq_ch)

    summary_inputs = groot_ch
        .mix(kma_ch)
        .mix(ariba_ch)
        .mix(ariba_summary_ch)
        .mix(karga_ch)
        .mix(srst2_ch)
        .groupTuple()
    
    summary_inputs
        .map { sample_name, files ->
            // Identify the output file by name
            def getFile = { pattern -> files.find { it.name.contains(pattern) } ?: '' }

            tuple(
                sample_name,
                getFile("groot_report_${sample_name}.tsv"),
                getFile("ariba_report_${sample_name}.tsv"),
                getFile("ariba_summary_${sample_name}.csv"),
                getFile("karga_report_${sample_name}.csv"),
                getFile("srst2_report_${sample_name}_fullgenes_sequence_results.txt"),
                getFile("ARGprofiler_report_${sample_name}.txt"),
                file(params.metadata_file)  // or however you pass metadata
            )
    }
    .set { final_inputs }
    // Call the summarize_results process with the final inputs
    summarize_results(final_inputs)
}