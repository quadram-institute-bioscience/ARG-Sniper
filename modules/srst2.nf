#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with SRST2
process srst2 {
    maxRetries 5
    container "${params.container__srst2}"
    publishDir params.OUTPUT, mode: 'copy'


    input:
    tuple val(sample_name), path(R1_fastq), path(R2_fastq)

    output:
    tuple val(sample_name), path("srst2_report_${sample_name}_fullgenes_sequence_results.txt"), emit: srst2_report

    shell:
    '''
    srst2 --forward '_R1' --reverse '_R2' --input_pe !{R1_fastq} !{R2_fastq} --output srst2_report_!{sample_name} --log --gene_db !{params.srst2db} --threads !{params.NCPUS}
    mv srst2_report_!{sample_name}__genes__sequence__results.txt srst2_report_!{sample_name}_genes_sequence_results.txt
    
    if [ -f srst2_report_!{sample_name}__fullgenes__sequence__results.txt ]; then
        mv srst2_report_!{sample_name}__fullgenes__sequence__results.txt srst2_report_!{sample_name}_fullgenes_sequence_results.txt
    else
        touch srst2_report_!{sample_name}_fullgenes_sequence_results.txt
    fi
    '''
}
