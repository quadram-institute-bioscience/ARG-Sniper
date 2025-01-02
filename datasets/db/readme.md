## How to build panARG
To build a comprehensive **A**ntimicrobial **R**esistant **G**enes (panARG), the following AMR databases have been used:
  - AMRFinderplus (v3.12)
  - ARGANNOT (V6_July2019)
  - BacMet (v1.1)
  - CARD (v3.3.0)
  - MEGARES (v3.00)
  - ResFinder
  - ResFinder_FG (v2.0)

## Method
1. **Download the AMR databases:**
   Run the following script to download all AMR databases into the `databases` directory:  
   ```bash
   utils/download_AMRdb.sh
2. **Prepare the AMR databases:**
   We retained AMR gene sequences with start and stop codons or those translatable into proteins using `ariba prepareref`.
   > **Note:** Genes requiring SNP confirmation for resistance were discarded as needed using `utils/filterGenes.py`.
3. **Merge AMR Databases:**
   Use [*gene_assimilator*](https://github.com/genomicepidemiology/gene_assimilator) to combine the AMR gene collections from different databases and build a consensus AMR database panARG.
4. **Automate Steps 2–3:**
   All filtering and merging steps are automated using:
   ```bash
   utils/build_panARG.sh
   ```
   > **Note**: Before running provide the paths for the following variables withing the script
   ```bash
   ariba="singularity exec ariba_2.14.6--py39heaaa4ec_6.img ariba"
   db="path/to/directory/containing/AMR/databases" 
   scripts="utils"
   GeneAssimilatoR="singularity exec gene_assimilator.img GeneAssimilatoR.R"
