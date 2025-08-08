#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with ariba
process ariba_run {
    container "${params.container__ariba}"
    publishDir params.OUTPUT, mode: 'copy'

    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    tuple val(sample_name), path("ariba_report_${sample_name}.tsv"), emit: ariba_report

    when:

    shell:
    '''
    ariba run !{params.aribadb} !{R1_fastq} !{R2_fastq} ./results --threads !{params.NCPUS}
    mv results/report.tsv ariba_report_!{sample_name}.tsv
    '''
}

// Summarise ariba results
process ariba_summary {
    container "${params.container__ariba}"
    publishDir params.OUTPUT, mode: 'copy'

    input:
    tuple val(sample_name), path(sample_reports)

    output:
    tuple val(sample_name), path("ariba_summary_${sample_name}.csv"), emit: ariba_summary

    shell:
    '''
    ariba summary ariba_summary  !{sample_reports}
    mv ariba_summary.csv ariba_summary_!{sample_name}.csv
    '''
}
