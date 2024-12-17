#!/bin/bash

##Replace the paths as needed.
ariba="singularity exec /qib/research-groups/CoreBioInfo/projects/arg-snipper/singulariy-images/ariba_2.14.6--py39heaaa4ec_6.img ariba"
db="/qib/research-groups/CoreBioInfo/projects/arg-snipper/databases" 
scripts="/qib/research-groups/CoreBioInfo/projects/arg-snipper/databases/scripts"
GeneAssimilatoR="singularity exec /qib/research-groups/CoreBioInfo/projects/arg-snipper/singulariy-images/gene_assimilator.img GeneAssimilatoR.R"

# Define the directory path
database_dir="panARG/sequences"

# Check if the directory exists
if [ -d "$db/$database_dir" ]; then
    echo "Directory '$db/$database_dir' already exists."
else
    echo "Directory '$db/$database_dir' does not exist. Creating now..."
    mkdir -p "$db/$database_dir"
    if [ $? -eq 0 ]; then
        echo "Directory '$db/$database_dir' created successfully."
    else
        echo "Failed to create directory '$db/$database_dir'."
        exit 1
    fi
fi
### Filtering the genes not having start and stop codons
echo "Preparing BacMet database"
$ariba prepareref -f "$db/bacmet_db/MetalResistance.fa" --all_coding yes --no_cdhit --force "$db/bacmet_db/prepare"
cp "$db/bacmet_db/prepare/02.cdhit.all.fa" "$db/$database_dir/MetalResistance_cds.fna"
echo "Done!!!"

echo "Preparing MEGARES database"
$ariba prepareref -f "$db/megares_db/megares_database_v3.00.fasta" --all_coding yes --no_cdhit --force "$db/megares_db/prepare"
python3 $scripts/filterGenes.py $db/megares_db/prepare/02.cdhit.all.fa $db/$database_dir/megares_cds.fna
echo "Done!!!"

echo "Preparing CARD database"
$ariba prepareref -f $db/card_db/nucleotide_fasta_protein_homolog_model.fasta --all_coding yes --no_cdhit --force $db/card_db/prepare
cp $db/card_db/prepare/02.cdhit.all.fa $db/$database_dir/card_cds.fna
echo "Done!!!"

echo "Preparing RESFINDER_FG_2.0 database"
$ariba prepareref -f $db/resfinder_fg/ResFinder-FG_2.0.fasta --all_coding yes --no_cdhit --force $db/resfinder_fg/prepare
cp $db/resfinder_fg/prepare/02.cdhit.all.fa $db/$database_dir/ResFinder-FG_cds.fna
echo "Done!!!"

echo "Preparing RESFINDER database"
$ariba prepareref -f $db/resfinder_db/all.fsa --all_coding yes --no_cdhit --force $db/resfinder_db/prepare
cp $db/resfinder_db/prepare/02.cdhit.all.fa $db/$database_dir/ResFinder_cds.fna
echo "Done!!!"

echo "Preparing AMRFinderPlus database"
$ariba prepareref -f $db/AMRfinderPlus_db/AMR_CDS --all_coding yes --no_cdhit --force $db/AMRfinderPlus_db/prepare
cp $db/AMRfinderPlus_db/prepare/02.cdhit.all.fa $db/$database_dir/AMRfinderPlus_cds.fna
echo "Done!!!"

echo "Preparing ARG-ANNOT database"
$ariba prepareref -f $db/arg-annot_db/ARG-ANNOT_NT_V6_July2019.fasta --all_coding yes --no_cdhit --force $db/arg-annot_db/prepare
cp $db/arg-annot_db/prepare/02.cdhit.all.fa $db/$database_dir/ARG-ANNOT_cds.fna
echo "Done!!!"

# Create panARG database
echo "Preparing panARG database"
$GeneAssimilatoR -d $db/$database_dir -o $db/panARG -p panARG
echo "Database: $db/panARG Done !!!"

# Plot overlapping genes across databases
python3 $scripts/gene_overlap_heatmap_plot.py -i $db/panARG/overview/panARG_master_gene_tbl.tsv -o $db/panARG/overview/plots
echo "Heatmap: $db/panARG/overview/plots"