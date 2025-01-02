#!/usr/bin/env python3

import click
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Set, List, Tuple

class DatabaseAnalyzer:
    def __init__(self, input_file: str):
        """Initialize the analyzer with input file path."""
        self.input_file = input_file
        self.data = None
        self.gene_sets = {}
        self.databases = []
        
    def read_data(self) -> None:
        """Read and validate input data."""
        try:
            # Read the file with flexible whitespace delimiter
            self.data = pd.read_csv(self.input_file, sep="\t")
            required_columns = ['userGeneName', 'database']
            
            # Validate required columns exist
            if not all(col in self.data.columns for col in required_columns):
                raise ValueError(f"Input file must contain columns: {required_columns}")
                
        except Exception as e:
            raise click.ClickException(f"Error reading input file: {str(e)}")
            
    def process_data(self) -> None:
        """Process data into gene sets for each database."""
        try:
            # Group genes by database
            for db, group in self.data.groupby('database'):
                self.gene_sets[db] = set(group['userGeneName'])
            self.databases = sorted(self.gene_sets.keys())
            
        except Exception as e:
            raise click.ClickException(f"Error processing data: {str(e)}")
            
    def generate_matrix(self) -> pd.DataFrame:
        """Generate the sharing matrix."""
        try:
            # Create empty matrix
            n_dbs = len(self.databases)
            matrix = pd.DataFrame(
                np.zeros((n_dbs, n_dbs), dtype=int),
                index=self.databases,
                columns=self.databases
            )
            
            # Fill matrix with intersection sizes
            for i, db1 in enumerate(self.databases):
                for j, db2 in enumerate(self.databases):
                    if i <= j:  # Fill upper triangle and diagonal
                        intersection = len(self.gene_sets[db1] & self.gene_sets[db2])
                        matrix.iloc[i, j] = intersection
                        matrix.iloc[j, i] = intersection  # Mirror for lower triangle
                        
            return matrix
            
        except Exception as e:
            raise click.ClickException(f"Error generating matrix: {str(e)}")
            
    def generate_percentage_matrix(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """Generate percentage sharing matrix."""
        try:
            # Get database sizes
            db_sizes = {db: len(genes) for db, genes in self.gene_sets.items()}
            
            # Create percentage matrix
            percent_matrix = pd.DataFrame(
                np.zeros((len(self.databases), len(self.databases)), dtype=float),
                index=self.databases,
                columns=self.databases
            )
            
            # Calculate percentages
            for i, db1 in enumerate(self.databases):
                for j, db2 in enumerate(self.databases):
                    intersection = matrix.iloc[i, j]
                    # Calculate percentage based on the smaller database
                    smaller_db_size = min(db_sizes[db1], db_sizes[db2])
                    percent = (intersection / smaller_db_size * 100) if smaller_db_size > 0 else 0
                    percent_matrix.iloc[i, j] = round(percent, 1)
                    
            return percent_matrix
            
        except Exception as e:
            raise click.ClickException(f"Error generating percentage matrix: {str(e)}")
            
    def plot_heatmap(self, matrix: pd.DataFrame, output_file: str, title: str) -> None:
        """Generate heatmap visualization."""
        try:
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                matrix,
                annot=True,
                fmt='.1f' if 'percent' in title.lower() else 'd',
                cmap='YlOrRd',
                square=True,
                mask=np.triu(np.ones_like(matrix, dtype=bool))
            )
            plt.title(title)
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            raise click.ClickException(f"Error generating heatmap: {str(e)}")

@click.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Input file path (space/tab-separated with columns: userGeneName, database)'
)
@click.option(
    '--output', '-o',
    required=True,
    type=click.Path(),
    help='Output directory path'
)
@click.option(
    '--prefix', '-p',
    default='sharing_matrix',
    help='Prefix for output files'
)
def main(input: str, output: str, prefix: str):
    """Generate database sharing matrix and visualizations from input gene data."""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzer
        analyzer = DatabaseAnalyzer(input)
        
        # Process data
        click.echo("Reading input data...")
        analyzer.read_data()
        
        click.echo("Processing data...")
        analyzer.process_data()
        
        # Generate matrices
        click.echo("Generating sharing matrices...")
        count_matrix = analyzer.generate_matrix()
        percent_matrix = analyzer.generate_percentage_matrix(count_matrix)
        
        # Save matrices to CSV
        count_matrix.to_csv(output_path / f"{prefix}_counts.csv")
        percent_matrix.to_csv(output_path / f"{prefix}_percentages.csv")
        
        # Generate and save heatmaps
        click.echo("Generating visualizations...")
        analyzer.plot_heatmap(
            count_matrix,
            output_path / f"{prefix}_counts_heatmap.png",
            "Database Gene Sharing (Counts)"
        )
        analyzer.plot_heatmap(
            percent_matrix,
            output_path / f"{prefix}_percentages_heatmap.png",
            "Database Gene Sharing (Percentages)"
        )
        
        click.echo(f"Results saved to: {output_path}")
        
        # Print summary statistics
        click.echo("\nSummary Statistics:")
        for db in analyzer.databases:
            click.echo(f"{db}: {len(analyzer.gene_sets[db])} genes")
            
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    main()