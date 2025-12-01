import click
import pandas as pd
import os
import math
from Bio import SeqIO

def merge_and_filter_data(genomes_file, metadata_file, amr_count):
    """Merge and filter genome and metadata files."""
    # Read input files
    genomes = pd.read_csv(genomes_file, header=0, sep="\t")
    metadata = pd.read_csv(metadata_file, header=0, sep="\t")
    
    # Add metadata
    genomes['#FILE'] = genomes['#FILE'] + '.gz'
    merged_df = pd.merge(genomes, metadata, left_on='#FILE', right_on='genome_file', how='left')
    
    # Filter strains
    strains_w_amr = merged_df[merged_df['NUM_FOUND'] > amr_count]
    strains_wo_amr = merged_df[merged_df['NUM_FOUND'] == 0]
    
    return strains_w_amr, strains_wo_amr

def sample_strains(strains_w_amr, strains_wo_amr, sample_size, random_state, 
                  sequencing_depth):
    """Sample strains with and without AMR."""
    amr = strains_w_amr.sample(n=sample_size, random_state=random_state)
    non_amr = strains_wo_amr.sample(n=sample_size, random_state=random_state)
    
    # Add coverage
    amr['coverage'] = sequencing_depth
    non_amr['coverage'] = sequencing_depth

    return pd.concat([amr, non_amr])
    #return amr



def process_genome(file_name, file_path, output_handle):
    """Process individual genome files."""
    base_name = file_name.replace('.fna.gz', '')
    
    try:
        concatenated_sequence = ""
        # Parse the FASTA file
        for record in SeqIO.parse(file_path, "fasta"):
            concatenated_sequence += str(record.seq)
            
        # write out the FASTA file
        new_header = f">{base_name}\n"
        output_handle.write(new_header)
        output_handle.write(f"{concatenated_sequence}\n")

    except OSError as e:
        click.echo(f"Error accessing file {file_path}: {e}", err=True)

@click.command()
@click.option('--genomes-file', required=True, 
              help='Path to the genomes TSV file')
@click.option('--metadata-file', required=True,
              help='Path to the metadata TSV file')
@click.option('--output-prefix', required=True,
              help='Output path for combined FASTA file')
@click.option('--sample-size', default=10, type=int,
              help='Number of samples to select from each group (default: 10)')
@click.option('--random-state', default=42, type=int,
              help='Random seed for sampling (default: 42)')
@click.option('--amr-count', default=1, type=int,
              help='Coverage value for AMR-positive strains (default: 1)')
@click.option('--sequencing-depth', default=1, type=int,
              help='Depth for sequences (X) (default: 1)')
@click.option('--read-length', default=125.0, type=int,
              help='Max read length (default: 125)')
def main(genomes_file, metadata_file, output_prefix, 
         sample_size, random_state, amr_count, sequencing_depth, read_length):
    """Process genome files and create coverage and combined FASTA outputs."""
    
    # Validate input files
    for file_path in [genomes_file, metadata_file]:
        if not os.path.exists(file_path):
            raise click.BadParameter(f"File does not exist: {file_path}")
    
    # Validate coverage values
    if amr_count < 1 or sequencing_depth <= 0 :
        raise click.BadParameter("AMR count and sequencing depth values must be positive numbers")
    
    click.echo("Processing input files...")
    strains_w_amr, strains_wo_amr = merge_and_filter_data(genomes_file, metadata_file, amr_count)
    
    click.echo(f"Sampling {sample_size} strains from each group...")
    df = sample_strains(strains_w_amr, strains_wo_amr, sample_size, random_state, sequencing_depth)
    #print(df['genome_type'])
    
    # Save coverage file
    click.echo(f"Saving {sequencing_depth}X coverage file...")
    df["#FILE"] = df['#FILE'].str.replace(r'\.fna.gz$', '', regex=True)
    #df["#FILE"] = df['#FILE'].str.replace(r'\.fasta.gz$', '', regex=True)
    genome_size = df["genome_size"].sum()
    click.echo(f"Total genome size: {genome_size}")
    number_of_reads = math.ceil(sequencing_depth*genome_size/read_length)
    click.echo(f"Number of reads required for {sequencing_depth}X coverage: {number_of_reads}")
    print(df['GENOME_LOC'])
    df["n_reads"] = (sequencing_depth*df["genome_size"]/read_length).apply(math.ceil)
    df["genome_size"] = df["genome_size"].apply(int)
    df[["#FILE", "coverage","genome_size","n_reads"]].to_csv(output_prefix+'.txt', 
                                    header=False, 
                                    index=False, 
                                    sep="\t")
    # Process genomes and create combined FASTA
    click.echo("Creating combined FASTA file...")
    with open(output_prefix + '_complete_genomes.fasta', 'w') as complete_genome, open(output_prefix + '_draft_genomes.fasta', 'w') as draft_genome :
        with click.progressbar(df.iterrows(), 
                             length=len(df), 
                             label='Processing genomes') as bar:
            for _, row in bar:
                if row['genome_type'] == 'Complete Genome':
                    process_genome(row['#FILE'], row['GENOME_LOC'], complete_genome)
                else:
                    process_genome(row['#FILE'], row['GENOME_LOC'], draft_genome)
    
    click.echo(f"Coverage file:{output_prefix}.txt")
    click.echo(f"Complete genomes:{output_prefix}_complete_genomes.fasta")
    click.echo(f"Draft genomes:{output_prefix}_draft_genomes.fasta")
    click.echo("Processing complete!")

if __name__ == '__main__':
    main()
