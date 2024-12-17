#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with groot
process groot_align {
    container "${params.container__groot}"
    publishDir params.results_dir

    input:
    path fastq_file

    output:
    path "groot-graphs-*", emit: results

    shell:
    '''
    groot align -i !{params.indexed_groot_database}  -f !{fastq_file} -p !{params.NCPUS} | groot report -c 0.95
    '''
}
