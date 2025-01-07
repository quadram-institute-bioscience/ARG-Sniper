#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with ariba
process ariba_run {
    cpus "${params.NCPUS}"
    memory "${params.MEM}"
    executor "slurm"
    container "${params.container__ariba}"
    publishDir "${params.results_dir}/ariba", mode: 'copy'


    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    path "ariba_report_${sample_name}.tsv"

    shell:
    '''
    ariba run !{params.ariba_ref_database}  !{R1_fastq} !{R2_fastq} ./results --threads !{params.NCPUS}
    mv results/report.tsv ariba_report_!{sample_name}.tsv
    '''
}

// Summarise ariba results
process ariba_summarise {
    cpus "${params.NCPUS}"
    memory "${params.MEM}"
    executor "slurm"
    container "${params.container__ariba}"
    publishDir "${params.results_dir}/ariba", mode: 'copy'


    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    path "groot_report_${sample_name}.tsv"
    path "groot_${sample_name}.log"

    shell:
    '''
    ariba align -i !{params.indexed_ariba_database}  -f !{R1_fastq},!{R2_fastq} -p !{params.NCPUS} | groot report -c 0.95 > groot_report_!{sample_name}.tsv
    mv groot.log groot_!{sample_name}.log
    '''
}
