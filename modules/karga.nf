#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Analyse a genome with KARGA
process karga {
    container "${params.container__karga}"
    publishDir "${params.results_dir}/karga", mode: 'copy'

    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    path "*_KARGA_mappedGenes.csv"

    shell:
    '''
    cat !{R1_fastq} !{R2_fastq} > !{sample_name}.fastq.gz
    java KARGA !{sample_name}.fastq.gz d:!{params.karga_ref_database}
    '''
}
