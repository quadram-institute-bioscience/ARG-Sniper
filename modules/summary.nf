process summarize_results {
    tag "Summary"
    publishDir "${params.OUTPUT}", mode: 'copy'
    
    input:
    tuple val(sample_name), val(groot_file), val(ariba_file), val(ariba_summary_file), val(karga_file), val(srst2_fullgenes_file), val(kma_file), val(metadata_file)

    output:
    path("summary_${sample_name}.tsv")

    script:
        def args = []
    
        // Add sample name to arguments

        if (groot_file != '')           args << "--groot_results ${groot_file}"
        if (ariba_file != '')            args << "--ariba_results ${ariba_file}"
        if (ariba_summary_file != '')   args << "--ariba_summary ${ariba_summary_file}"
        if (karga_file != '')           args << "--karga_results ${karga_file}"
        if (srst2_fullgenes_file != '') args << "--srst2_results ${srst2_fullgenes_file}"
        if (kma_file != '')             args << "--argprofiler_results ${kma_file}"
        if (metadata_file != '')        args << "--metadata ${metadata_file}"
        args << "--output_file summary_${sample_name}.tsv"
        """
        python3 ${projectDir}/bin/summarize_results.py ${args.join(' ')}
        """
}