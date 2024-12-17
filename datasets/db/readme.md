# How to build panARG
**Introduction:** \
To build a comprehensive **A**ntimicrobial **R**esistant **G**enes (panARG), the following AMR databases have been used:
  - AMRFinderplus (v3.12)
  - ARGANNOT (V6_July2019)
  - BacMet (v1.1)
  - CARD (v3.3.0)
  - MEGARES (v3.00)
  - ResFinder
  - ResFinder_FG (v2.0)

1. Download the AMR databases using: `./scripts/{db}_download.sh`
2. Discard the sequence without start and stop code at the beginning and end, respectively of the sequence. Retaining the coding sequences only.
3. Move the AMR-cds to a single directory.
4. Use [*gene_assimilator*](https://github.com/genomicepidemiology/gene_assimilator) to create a single gene collection by combining the different AMR gene collections.
   ```
   Rscript GeneAssimilatoR.R -d /qib/research-groups/CoreBioInfo/projects/arg-snipper/databases/panARG/sequences/ -o /qib/research-groups/CoreBioInfo/projects/arg-snipper/databases/panARG/ -p panARG
   ```
