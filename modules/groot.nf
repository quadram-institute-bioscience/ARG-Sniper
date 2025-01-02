#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with groot
process groot_align {
    container "${params.container__groot}"
    publishDir params.results_dir, mode: 'copy'

    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    path "groot-graphs-${sample_name}", emit: results

    shell:
    '''
    groot align -i !{params.indexed_groot_database}  -f !{R1_fastq},!{R2_fastq} -p !{params.NCPUS} | groot report -c 0.95
    mv groot-graphs-* groot-graphs-!{sample_name}
    '''
}
