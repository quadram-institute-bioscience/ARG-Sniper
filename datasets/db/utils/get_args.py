import click
import pandas as pd
import re

def filter_amr_rows(row):
    """
    Function to filter AMR rows based on specific criteria.
    """
    if row.database=="AMRfinderPlus_cds":
        a, *b = row.id.split('_')
        if b[0]=='WP':
            id = "_".join(b[0:2])
        else:
            id = b[0]
    elif row.database=="card_cds":
        match = re.search(r'ARO_\d+', row.id)
        if match:
            id = match.group()
            id = id.replace('_', ':')
    elif row.database=="ARG-ANNOT_cds":
        _, *b = row.id.split('_')
        if b[-4].isdigit():
            id = "_".join(b[-5:-3])
        else:
            id = b[-4]
    elif row.database=="megares_cds":
        match = re.search(r'MEG_\d+', row.id)
        if match:
            id = match.group()
    elif row.database=="ResFinder_cds":
        a, *b = row.id.split('_')
        id = b[-1]
    else:
        id = row.id
    return id
def process_amrfinderplus(AMRFinderPlus_df):
    # replace NAN values in 'refseq_protein_accession' with values from 'genbank_protein_accession'
    AMRFinderPlus_df['refseq_protein_accession'] = AMRFinderPlus_df['refseq_protein_accession'].fillna(AMRFinderPlus_df['genbank_protein_accession'])
    AMRFinderPlus_df['allele']=AMRFinderPlus_df['allele'].fillna(AMRFinderPlus_df['gene_family'])
    AMRFinderPlus_df=AMRFinderPlus_df[['subtype','allele','gene_family','class','refseq_protein_accession']]
    return AMRFinderPlus_df

def process_card(card_df):
    card_df['subtype']="AMR"
    card_df = card_df[["ARO Accession", "AMR Gene Family", "CARD Short Name","subtype", "Drug Class"]]
    #card_df.rename(columns={"Protein Accession": "refseq_protein_accession", "AMR Gene Family": "gene_family", "Drug Class": "class", "CARD Short Name": "allele"}, inplace=True)
    return card_df

def summarize_arg(merged_df):
    summary = merged_df.groupby("userGeneName").agg({
        "gene_len": "first",
        "shortname": lambda x: ",".join(sorted(set(x.dropna()))),
        "database": lambda x: ",".join(sorted(set(x.dropna()))),
        "fa_header": "count",  # Number of entries
        "id": lambda x: ",".join(sorted(set(x.dropna()))),
        "allele": lambda x: ",".join(sorted(set(x.dropna()))),
        "gene_family": lambda x: ",".join(sorted(set(x.dropna()))),
        "subtype": lambda x: ",".join(sorted(set(x.dropna()))),
        "class": lambda x: ",".join(sorted(set(x.dropna())))
    }).rename(columns={"fa_header": "entry_count"})
    
    # Remove duplicates within the strings in "type" column
    summary["subtype"] = summary["subtype"].apply(
        lambda x: ",".join(sorted(set(str(x).split(",")))) if pd.notna(x) and "," in str(x) else x
    )

    summary.reset_index(inplace=True)


    return summary


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--amrfinderplus', type=str, default='ReferenceGeneCatalog.txt', help='Mapping file for AMRFinderPlus')
@click.option('--card', type=str, default='aro_index.tsv', help='Mapping file for CARD')
@click.option('--megares', type=str, default='megares_annotations_v3.00.csv', help='Megares annotations file')
@click.option('--resfinder', type=str, default='notes.txt', help='Notes file for ResFinder')
@click.option('--summary', type=str, default='summary.txt', help='Summary File name')

def main(filename, amrfinderplus, card, megares, resfinder, summary):
    df = pd.read_csv(filename, sep="\t", header=0)
    
    # Parse AMR databases metadata files
    AMRFinderPlus_df = pd.read_csv(amrfinderplus, sep="\t", header=0) # AMRFinderPlus
    
    card_df = pd.read_csv(card, sep="\t", header=0) # CARD
    
    megares_df = pd.read_csv(megares, sep=",", header=0) # MEGARes
    megares_df["header"] = megares_df["header"].str.extract(r"(MEG_\d+)") # MEGARes
    # if type = Multi-compound, copy value from class to type
    megares_df.loc[megares_df["type"] == "Multi-compound", "type"] = megares_df["class"]
    # now replace word resistance with nothing in the "type" column
    megares_df["type"] = megares_df["type"].str.replace(" resistance", "")
    # replace Drug with AMR in the "type" column and replace "and" with ","
    megares_df["type"] = megares_df["type"].str.replace(" and ", ",")
    # replace Drug or Drugs with AMR in the "type" column
    megares_df["type"] = megares_df["type"].str.replace("Drugs", "AMR")
    megares_df["type"] = megares_df["type"].str.replace("Drug", "AMR")
    megares_df["type"] = megares_df["type"].str.replace("Biocides", "Biocide")
    megares_df["type"] = megares_df["type"].str.replace("Metals", "Metal")
    
    resfinder_df = pd.read_csv(resfinder, sep=":", comment="#",names=["Gene allele", "class","empty"])# ResFinder
    # class remove "resistance" word
    resfinder_df['class'] = resfinder_df['class'].str.replace("resistance", "")
    # Substitute special characters in "Gene allele" with "_"
    resfinder_df['Gene symbol'] = resfinder_df['Gene allele'].str.replace(r'[^a-zA-Z0-9]', '_', regex=True)
    
    # Process AMR databases
    AMRFinderPlus_df=process_amrfinderplus(AMRFinderPlus_df)
    card_df=process_card(card_df)

    df['id'] = df['fa_header']
    for row in df.itertuples(index=True):  # or index=True if you want the index
        df.at[row.Index, 'id']=filter_amr_rows(row)


    merged_df = pd.merge(df, AMRFinderPlus_df, left_on='id', right_on='refseq_protein_accession', how='left')
    merged_df = pd.merge(merged_df, card_df , left_on='id', right_on='ARO Accession', how='left')
    
    merged_df['subtype'] = merged_df['subtype_x'].combine_first(merged_df['subtype_y'])
    merged_df['allele'] = merged_df['allele'].combine_first(merged_df['CARD Short Name'])
    merged_df['gene_family'] = merged_df['gene_family'].combine_first(merged_df['AMR Gene Family'])
    merged_df['class'] = merged_df['class'].combine_first(merged_df['Drug Class'])
    
    # Drop column subtype_x and subtype_y
    merged_df.drop(columns=['chosenSeq','fa_name','AMR Gene Family','subtype_x', 'subtype_y', 'refseq_protein_accession', 'ARO Accession', 'CARD Short Name','Drug Class'], inplace=True)

    for row in merged_df.itertuples(index=True):
        if row.database == 'ARG-ANNOT_cds':
            merged_df.at[row.Index, 'subtype'] = "AMR"
            # split 'fa_header' by '_ and join 2 and 3 elements
            # and assign to 'allele'
            #_, *b = row.fa_header.split('_')
            # check if 3rd element in b is integer
            ##if b[2].isdigit():
            merged_df.at[row.Index, 'allele'] = row.fa_header
            else:
                merged_df.at[row.Index, 'allele'] = b[1]
            
            merged_df.at[row.Index, 'gene_family'] = b[1]
        
        if row.database == 'MetalResistance_cds':
            merged_df.at[row.Index, 'subtype'] = "Metal"
            # split 'fa_header' by '_ and join 2 and 3 elements
            # and assign to 'allele'
            a, *b = row.fa_header.split('_')
            merged_df.at[row.Index, 'id'] = b[-1]
            merged_df.at[row.Index, 'allele'] = a
            merged_df.at[row.Index, 'gene_family'] = a
        
        if row.database == 'ResFinder_cds':
            merged_df.at[row.Index, 'subtype'] = "AMR"
            # split 'fa_header' by '_ and join 2 and 3 elements
            # and assign to 'allele'
            a = row.fa_header.split('_')
            merged_df.at[row.Index, 'gene_allele'] = "_".join(a[:-2])
            merged_df.at[row.Index, 'gene_family'] = a[0]
        
    
    merged_df = pd.merge(merged_df, megares_df , left_on='id', right_on='header', how='left')
    merged_df['subtype'] = merged_df['subtype'].combine_first(merged_df['type'])
    merged_df['gene_family'] = merged_df['gene_family'].combine_first(merged_df['group'])
    merged_df['class'] = merged_df['class_x'].combine_first(merged_df['class_y'])
    # Drop column subtype_x and subtype_y
    merged_df.drop(columns=['type','group','class_x','class_y','header','mechanism'], inplace=True)

    # Merge with ResFinder
    merged_df = pd.merge(merged_df, resfinder_df , left_on='gene_allele', right_on='Gene symbol', how='left')
    merged_df['class'] = merged_df['class_x'].combine_first(merged_df['class_y'])
    merged_df['allele'] = merged_df['allele'].combine_first(merged_df['Gene allele'])
    merged_df.drop(columns=['Gene allele','gene_allele','Gene symbol','class_x','class_y','empty'], inplace=True)
    
    # Summarize ARGs
    # make all in uppercase subtype column
    merged_df['subtype'] = merged_df['subtype'].str.upper()
    # Remove duplicates within the "type" column
    summary_df=summarize_arg(merged_df)

    # write the merged dataframe to a new file
    summary_df.to_csv(summary, sep="\t", index=False)

if __name__ == '__main__':
    main()

