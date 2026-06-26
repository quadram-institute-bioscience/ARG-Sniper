#!/usr/bin/env python3
import click
import csv, re
from Bio import SeqIO
from typing import Dict, Set, Tuple

@click.command(help="""
Process AMRFinderPlus gene sequences based on subtypes.

Required Arguments:\n
    INPUT_TXT: ReferenceGeneCatalog.txt from AMRfinderPlus database\n
    INPUT_FASTA: AMR_CDS from AMRfinderPlus database           
""")
@click.argument('input_txt', type=click.Path(exists=True), default="ReferenceGeneCatalog.txt")
@click.argument('input_fasta', type=click.Path(exists=True), default="AMR_CDS.fasta")
@click.option('--output_txt', default='filtered_output.txt', help='Output text file name')
@click.option('--output_fasta', default='filtered_sequences.fasta', help='Output FASTA file name')
def filter_and_extract(input_txt, input_fasta, output_txt, output_fasta):
    """
    Get AMRfilderPlus genes with subtype AMR, BIOCIDE AND METAL.
    """
    # List of allowed subtypes
    ALLOWED_SUBTYPES = {'AMR', 'BIOCIDE', 'METAL'}
    
    def get_accession(row: Dict) -> Set[str]:
        """
        Extract valid accession pairs from a row.
        Returns patterns to search for in FASTA headers.
        """
        patterns = set()
        
        # Check RefSeq pair
        refseq_nucleotide_accession = row['refseq_nucleotide_accession']
        refseq_start=row['refseq_start']
        refseq_stop=row['refseq_stop']
        genbank_nucleotide_accession = row['genbank_nucleotide_accession']
        genbank_start=row['genbank_start']
        genbank_stop=row['genbank_stop']
        
        if refseq_nucleotide_accession:
            if refseq_start and refseq_stop:
                pattern = f"{refseq_nucleotide_accession}:{refseq_start}-{refseq_stop}"
                patterns.add(pattern)
                if genbank_nucleotide_accession:
                    pattern = f"{genbank_nucleotide_accession}:{refseq_start}-{refseq_stop}"
                    patterns.add(pattern)

        if genbank_nucleotide_accession:
            if genbank_start and genbank_stop:
                if row['genbank_strand']== '-':
                    pattern = f"{genbank_nucleotide_accession}:{genbank_stop}-{genbank_start}"
                    patterns.add(pattern)
                    if refseq_nucleotide_accession:
                        pattern = f"{refseq_nucleotide_accession}:{genbank_stop}-{genbank_start}"
                        patterns.add(pattern)
                else:
                    pattern = f"{genbank_nucleotide_accession}:{genbank_start}-{genbank_stop}"
                    patterns.add(pattern)
                    if refseq_nucleotide_accession:
                        pattern = f"{refseq_nucleotide_accession}:{genbank_start}-{genbank_stop}"
                        patterns.add(pattern)

        return patterns
    
    try:
        # Step 1: Filter the text file and collect accession patterns
        accession_patterns = set()
        
        with open(input_txt, 'r') as infile, open(output_txt, 'w', newline='') as outfile:
            reader = csv.DictReader(infile, delimiter='\t')
            
            # Verify all required headers are present
            required_headers = [
                'allele', 'gene_family', 'whitelisted_taxa', 'product_name',
                'scope', 'type', 'subtype', 'class', 'subclass',
                'refseq_protein_accession', 'refseq_nucleotide_accession',
                'curated_refseq_start', 'genbank_protein_accession',
                'genbank_nucleotide_accession', 'genbank_strand',
                'genbank_start', 'genbank_stop', 'refseq_strand',
                'refseq_start', 'refseq_stop', 'pubmed_reference',
                'blacklisted_taxa', 'synonyms', 'hierarchy_node', 'db_version'
            ]
            
            if not all(header in reader.fieldnames for header in required_headers):
                raise ValueError("Input file is missing required headers")
            
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, delimiter='\t')
            filtered_count = 0
            total_count = 0
            # Write required_headers to the output file
            writer.writeheader()
            for row in reader:
                total_count += 1
                if row['subtype'] in ALLOWED_SUBTYPES:
                    writer.writerow(row)
                    filtered_count += 1
                    patterns = get_accession(row)            
                    accession_patterns.update(patterns)
        
        # Step 2: Extract matching sequences from FASTA file
        # Initialize a counter for sequences found as dictionary
        sequences_found = 0
        # Open both output files - one for FASTA and one for the descriptions
        with open(output_fasta, 'w') as fasta_out, open('matching_patterns.txt', 'w') as pattern_out:
            for record in SeqIO.parse(input_fasta, 'fasta'):
                # Check each pattern against the description
                for pattern in accession_patterns:
                        if pattern in record.description:
                            # Write the sequence to FASTA file
                            SeqIO.write(record, fasta_out, 'fasta')
                            # Write the description and matching pattern to pattern file
                            pattern_out.write(f"{record.description}\t{pattern}\n")
                            sequences_found +=1
                            break  # Break after first match if you want to avoid duplicate entries
        
        # Print summary
        click.echo(f"Processing complete!")
        click.echo(f"\nText file summary:")
        click.echo(f"- Total rows processed: {total_count}")
        click.echo(f"- Rows retained after subtype filtering: {filtered_count}")
        click.echo(f"- Filtered data written to: {output_txt}")
        click.echo(f"\nFASTA file summary:")
        click.echo(f"- Unique patterns found: {len(accession_patterns)}")
        click.echo(f"- Matching sequences extracted: {sequences_found}")
        click.echo(f"- Sequences written to: {output_fasta}")
                    
    except Exception as e:
        click.echo(f"Error processing files: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    filter_and_extract()