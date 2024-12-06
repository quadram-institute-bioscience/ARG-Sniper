#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Align a genome with groot
process groot_align {
    conda '${params.work_dir}/ARG-snipper/envs/groot.yaml'

    input:
    path genome_fasta

    output:
    path "a.report"

    script:
    'groot align -i ${params.indexed_groot_database}  -f ${genome_fasta} -p 8 | groot report -c 0.95'

}
