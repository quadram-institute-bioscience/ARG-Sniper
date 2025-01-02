# Preparation of synthetic community

- **Stept1:** Download the datasets
The two public datasets were used to create a mock community.
  - **Dataset 1: HumGut**
    - **Description**: Human Gut Genome Collection[^1]
    - **Genomes**: [https://github.com/larssnip/HumGut?tab=readme-ov-file#fasta-files](https://github.com/larssnip/HumGut?tab=readme-ov-file#fasta-files)
    - **Metadata**: [https://github.com/larssnip/HumGut?tab=readme-ov-file#metadata-tables](https://github.com/larssnip/HumGut?tab=readme-ov-file#metadata-tables)
  - **Dataset 2: Hight resistance bacterial genomes**
    - **Description**: Collection of bacterial genomes with high resistance[^2]
    - **GitHub**:[https://github.com/ewissel/hAMRoaster](https://github.com/ewissel/hAMRoaster)

- **Step2:** Predict the AMR Genes using ABRicate[^3] within both datasets.
  ```arbicate.sh
  datadir="/qib/research-groups/CoreBioInfo/projects/arg-snipper/raw-reads/simulated_reads"
  cd $datadir/resistance_profile

  # Prepare abricate database
  makeblastdb -in sequences -title panARG -dbtype nucl -hash_index

  # Predict AMR
  ## 1. High resistance bacterial genomes
  abricate --threads 16 --datadir $datadir --db panARG --nopath $datadir/1.High_resistance_mock_community/*.fasta --minid 70 --mincov 70 >$datadir/resistance_profile/High_resistance_mock_community.tsv
  abricate --summary $datadir/resistance_profile/High_resistance_mock_community.tsv >$datadir/resistance_profile/High_resistance_mock_community_summary.tsv

  ## 2. HumGut
  abricate --threads 16 --datadir $datadir --db panARG --nopath $datadir/2.HumGut_dataset/HumGut_genomes/*.fna --minid 70 --mincov 70 >$datadir/resistance_profile/HumGut.tsv
  abricate --summary $datadir/resistance_profile/HumGut.tsv >$datadir/resistance_profile/HumGut_summary.tsv
  ```
- **Step3:** Separate resistant and non-resistant genomes within Dataset1.
  ```
  cut -f1 $datadir/resistance_profile/HumGut_summary.tsv | grep -v "#FILE" >$datadir/resistance_profile/HumGut_resistant_strains.list
  grep -vf $datadir/resistance_profile/HumGut_resistant_strains.list $datadir/2.HumGut_dataset/raw-genomes.list >$datadir/resistance_profile/genomes_wo_amr.list
  ```
- **Step4:** Merge two resistance profiles
  ```
  cut -f1,2 $datadir/resistance_profile/*_summary.tsv | grep -v "#FILE" >$datadir/resistance_profile/resistance_profile.tsv
  sed -i '1i #FILE\tNUM_FOUND' $datadir/resistance_profile/resistance_profile.tsv
  ```
- **Step5:** Join the resistance profile and non-resistance genomes.
  ```
  ## Modify non-resistant Genomes and merge them with resistant genomes.
  awk '{print $0"\t"0}' $datadir/resistance_profile/genomes_wo_amr.list > temp && cat $datadir/resistance_profile/resistance_profile.tsv temp >$datadir/resistance_profile/resistance_non-resistant_genomes.tsv && mv temp

  ## Add the full path of genomes to resistance_non-resistant_genomes.tsv
  awk -v fasta_path="$datadir/1.High_resistance_mock_community/" -v fna_path="$datadir/2.HumGut_dataset/HumGut_genomes/" 'BEGIN {OFS="\t"} 
    NR==1 {print $0, "GENOME_LOC"} 
    NR>1 {
        if ($1 ~ /\.fasta$/) 
            print $0, fasta_path $1
        else if ($1 ~ /\.fna$/) 
            print $0, fna_path $1
    }' $datadir/resistance_profile/resistance_non-resistant_genomes.tsv >$datadir/resistance_profile/res_non-res_genomes_full.tsv
  ```
 - **Step6:** Simulate reads at 1x, 5x and 25x coverage.
   ```
   subsample="/qib/research-groups/CoreBioInfo/projects/arg-snipper/raw-reads/simulated_reads/resistance_profile/subsample_genomes.py"
   insilicoseq="/qib/research-groups/CoreBioInfo/projects/arg-snipper/singulariy-images/insilicoseq-2.0.1--pyh7cba7a3_0.img"
   cd $datadir/resistance_profile

   ## Subsample genomes at 1x coverage
   python3 $subsample --genomes-file ./res_non-res_genomes_full.tsv --metadata-file $datadir/2.HumGut_dataset/HumGut.tsv --output-prefix dataset_1x --random-state 42 --sequencing-depth 1 --amr-count 2
   cut -f1,2 dataset_1x.txt >coverage-1x.txt
   ## Simulate reads at 1x coverage from selected genomes
   singularity exec $insilicoseq iss generate --cpus 1 --draft ./dataset_1x_draft_genomes.fasta --coverage_file ./coverage-1x.txt --compress --store_mutations --model HiSeq --output   dataset-1x --genomes ./dataset_1x_complete_genomes.fasta

   ## Subsample genomes at 5x coverage
   python3 $subsample --genomes-file ./res_non-res_genomes_full.tsv --metadata-file $datadir/2.HumGut_dataset/HumGut.tsv --output-prefix dataset_5x --random-state 42 --sequencing-depth 5 --amr-count 2
   cut -f1,2 dataset_5x.txt >coverage-5x.txt
   singularity exec $insilicoseq iss generate --cpus 1 --draft ./dataset_5x_draft_genomes.fasta --coverage_file ./coverage-5x.txt --compress --store_mutations --model HiSeq --output   dataset-5x --genomes ./dataset_5x_complete_genomes.fasta --seed 100 --n_reads 2M

   ## Subsample genomes at 5x coverage
   python3 $subsample --genomes-file ./res_non-res_genomes_full.tsv --metadata-file $datadir/2.HumGut_dataset/HumGut.tsv --output-prefix dataset_25x --random-state 42 --sequencing-depth 25 --amr-count 2
   cut -f1,2 dataset_25x.txt >coverage-25x.txt
   singularity $insilicoseq iss generate --cpus 1 --draft ./dataset_25x_draft_genomes.fasta --coverage_file ./coverage-25x.txt --compress --store_mutations --model HiSeq --output dataset-25x --genomes ./dataset_25x_complete_genomes.fasta --seed 100 --n_reads 9M
   ```
   
**References**
[^1]: [HumGut Dataset](https://doi.org/10.1186/s40168-021-01114-w)
[^2]: [hAMRoaster: Table 1](https://doi.org/10.1101/2022.01.13.476279)
[^3]: [ABRicate](https://github.com/tseemann/abricate)

