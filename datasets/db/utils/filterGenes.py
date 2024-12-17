#!/usr/bin/env python3

import click

def filter_fasta(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        write_sequence = True
        for line in infile:
            if line.startswith('>'):
                if 'RequiresSNPConfirmation' in line:
                    write_sequence = False
                else:
                    write_sequence = True
                    outfile.write(line)
            elif write_sequence:
                outfile.write(line)

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--verbose', '-v', is_flag=True, help='Print verbose output')
def main(input_file, output_file, verbose):
    """
    Filter FASTA sequences, discarding those with 'RequiresSNPConfirmation' in the header.

    INPUT_FILE: Path to the input FASTA file \n
    OUTPUT_FILE: Path to the output FASTA file
    """
    filter_fasta(input_file, output_file)
    if verbose:
        click.echo(f"Filtered sequences have been written to {output_file}")

if __name__ == "__main__":
    main()
