import csv, os
import click
import pandas as pd
from collections import defaultdict
from functools import reduce
pd.set_option('future.no_silent_downcasting', True)

def parse_groot_results(groot_output_file):
    file_name = os.path.basename(groot_output_file)
    click.echo(f"Processing GROOT output: {file_name}")
    try:
        output = pd.read_csv(groot_output_file, sep="\t") # Assuming TSV format
        output.columns.values[0] = "Gene"
        output[file_name] = 1
        output=output[["Gene",file_name]]
    except pd.errors.EmptyDataError:
        print(f"Warning GROOT output: {file_name} is empty.")
        output[file_name]=0
    return output

def parse_ariba_results(ariba_output_file, ariba_summary_file):
    mapping={}
    file_name = os.path.basename(ariba_output_file)
    click.echo(f"Processing ARIBA output: {file_name}")
    try:
        output = pd.read_csv(ariba_output_file, sep="\t", header=0) # Assuming TSV format
        if 'ref_name' in output.columns and 'cluster' in output.columns:
            for _, row in output.iterrows():
                ref_name = row['ref_name']
                cluster = row['cluster']
                if cluster not in mapping:
                    mapping[cluster] = ref_name
    except pd.errors.EmptyDataError:
        print(f"Warning ARIBA output: {ariba_output_file}")
    
    ## Parse summary file
    try:
        summary = pd.read_csv(ariba_summary_file, sep=",", header=0) # Assuming CSV format
        summary = summary.replace({"yes": 1, "no": 0}).infer_objects(copy=False)
        summary.columns = summary.columns.str.replace(r"\.match$", "", regex=True)
        summary.rename(columns=mapping, inplace=True)
        summary=summary.T
        summary.columns = summary.iloc[0]
        summary = summary[1:].reset_index()
        summary.columns.values[0]="Gene"
        summary=summary[["Gene",file_name]]
        summary = summary[summary[file_name] != 0]
    except pd.errors.EmptyDataError:
        print(f"Warning ARIBA summary: {ariba_summary_file} is empty")

    return summary

def parse_karga_results(karga_output_file):
    file_name = os.path.basename(karga_output_file)
    click.echo(f"Processing KARGA output: {file_name}")  # Print current file being processed
    try:
        output = pd.read_csv(karga_output_file, sep=",", header=0) # Read CSV file
        output["PercentGeneCovered"] = output["PercentGeneCovered"].str.rstrip('%').astype(float) # Process PercentGeneCovered column
        output=output[output["PercentGeneCovered"] >= 80]
        output["PercentGeneCovered"]=1
        output["GeneIdx"]=output["GeneIdx"].str.lstrip('>').astype(str)
        output=output[["GeneIdx", "PercentGeneCovered"]].rename(columns={"GeneIdx": "Gene", "PercentGeneCovered": file_name})
    except pd.errors.EmptyDataError:
        print(f"Warning: {file_name} is empty.")
        output[file_name]=0
    
    return output

def parse_srst2_results(srst2_output_file):

    #file = srst2_output_file.replace("__genes__", "__fullgenes__")
    file_name = os.path.basename(srst2_output_file).replace("_fullgenes_sequence_results.txt", "")
    click.echo(f"Processing ARGprofiler output: {file_name}")
    try:
        output = pd.read_csv(srst2_output_file, sep="\t", header=0) # Read txt file
        output = output[["gene"]]
        output[file_name]=1
        output.rename(columns={"gene": "Gene"}, inplace=True)
            
    except pd.errors.EmptyDataError:
        print(f"Warning: {srst2_output_file} is empty.")
        output[file_name]=0
            
    except FileNotFoundError:
        print(f"Warning: {srst2_output_file} not found.")
        output[file_name] = 0  # Add missing file column with zeros

    return output

def parse_argprofiler_results(argprofiler_output_file):
    file_name = os.path.basename(argprofiler_output_file)
    click.echo(f"Processing ARGprofiler output: {file_name}")
    try:
        # Parase the file where first 6 lines are comments and 7 line is the header
        output = pd.read_csv(argprofiler_output_file, sep="\t", header=0, skiprows=6) # Read txt file
        output = output[["# refSequence"]]
        output[file_name]=1
        output.rename(columns={"# refSequence": "Gene"}, inplace=True)

    except pd.errors.EmptyDataError:
        print(f"Warning: {file_name} is empty.")
        output[file_name]=0

    except FileNotFoundError:
        print(f"Warning: {file_name} not found.")
        output[file_name] = 0
    return output

@click.command()
#@click.argument('abricate_result', type=click.Path(exists=True))
@click.option('--groot_results', type=click.Path(exists=True), required=False, help='Path to groot output file')
@click.option('--ariba_results', type=click.Path(exists=True), required=False, help='Path to ARIBA output TSV/CSV files')
@click.option('--ariba_summary', type=click.Path(exists=True), required=False, help='Path to ARIBA summary CSV file')
@click.option('--karga_results', type=click.Path(exists=True), required=False, help='Path to KARGA output TSV/CSV files')
@click.option('--srst2_results', type=click.Path(exists=True), required=False, help='Path to SRST2 output TXT files')
@click.option('--argprofiler_results', type=click.Path(exists=True), required=False, help='Path to ARGprofiler output TXT files')
@click.option('--metadata', type=click.Path(exists=True), required=False, help='Path to metadata file (panARG_annotation.tsv)')
@click.option('--output_file', required=True, help='Name of the output file to write the combined results')

def summary_report(groot_results, ariba_results, ariba_summary, karga_results, srst2_results, argprofiler_results, metadata, output_file):   
    dfs = []
    if groot_results:
        groot = parse_groot_results(groot_results)
        dfs.append(groot)
    
    if ariba_results:
        ariba = parse_ariba_results(ariba_results, ariba_summary)
        dfs.append(ariba)

    if karga_results:
        karga = parse_karga_results(karga_results)
        dfs.append(karga)

    if srst2_results:
        srst2 = parse_srst2_results(srst2_results)
        dfs.append(srst2)
    
    if argprofiler_results:
        argprofiler = parse_argprofiler_results(argprofiler_results)
        dfs.append(argprofiler)
    
    if not dfs:
        raise ValueError("No DataFrames available to merge. Exiting.")
    else:
        merged_df = reduce(lambda left, right: pd.merge(left, right, on='Gene', how='outer'), dfs)
        merged_df.fillna(0, inplace=True)
        # replace .csv, .tsv, .txt with "" in column names
        merged_df.columns = merged_df.columns.str.replace(r'\.(csv|tsv|txt)$', '', regex=True)

    if metadata:
        metadata_df = pd.read_csv(metadata, sep="\t")  # Assuming metadata is a TSV file
        if 'userGeneName' in metadata_df.columns:
            metadata_df.rename(columns={'userGeneName': 'Gene'}, inplace=True)
            merged_df = pd.merge(merged_df, metadata_df, on="Gene", how="inner")
            merged_df.fillna(0, inplace=True)
            print(f"Summary: Finalized report {output_file}")
            merged_df.to_csv(output_file, sep="\t", index=False)
            # Drop column "entry_count"
            merged_df.drop(columns=['entry_count'], inplace=True)
        else:
            print("Warning: 'userGeneName' column not found in metadata file.")
    else:
        # Writer reference to a file
        merged_df.to_csv(output_file, sep="\t", index=False)
        print(f"Summary: Finalized report {output_file}")

        
if __name__ == '__main__':
    summary_report()
