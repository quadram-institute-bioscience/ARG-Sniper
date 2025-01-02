#!/bin/bash
# Create database
db="database"

create_dir() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        echo "Directory '$dir_path' does not exist. Creating now..."
        mkdir -p "$dir_path"
    else
        echo "Directory '$dir_path' already exists."
    fi
}

echo "1. Download AMRfinderPlus"
FTP_URL="https://ftp.ncbi.nlm.nih.gov/pathogen/Antimicrobial_resistance/AMRFinderPlus/database/3.12/2024-07-22.1/AMR_CDS"
DEST_DIR="AMRfinderPlus_db"
create_dir "$db/$DEST_DIR"
curl -o $db/$DEST_DIR/AMR_CDS $FTP_URL
echo "Done!!!"

echo "2. Download ARG-ANNOT"
DEST_DIR="arg-annot_db"
create_dir "$db/$DEST_DIR"
curl -o $db/$DEST_DIR/ARG-ANNOT_NT_V6_July2019.fasta https://www.mediterranee-infection.com/wp-content/uploads/2019/09/ARG-ANNOT_NT_V6_July2019.txt
curl -o $db/$DEST_DIR/ARG-ANNOT_AA_V6_July2019.fasta https://www.mediterranee-infection.com/wp-content/uploads/2019/09/ARG-ANNOT_AA_V6_July2019.txt
echo "Done!!!"

echo "3. Download CARD"
DEST_DIR="card_db"
create_dir "$db/$DEST_DIR"
curl -o $db/card_db.tar.bz2 https://card.mcmaster.ca/download/0/broadstreet-v3.3.0.tar.bz2
tar -xvjf $db/card_db.tar.bz2 -C $db/$DEST_DIR
rm $db/card_db.tar.bz2
echo "Done!!!"

echo "4. Download MEGARES"
DEST_DIR="megares_db"
create_dir "$db/$DEST_DIR"
curl -o $db/$DEST_DIR/megares_v3.00.zip https://www.meglab.org/downloads/megares_v3.00.zip
unzip $db/$DEST_DIR/megares_v3.00.zip -d $db/$DEST_DIR
echo "Done!!!"

echo "5. Download ResFinder"
DEST_DIR="resfinder_db"
create_dir "$db/$DEST_DIR"
git clone https://bitbucket.org/genomicepidemiology/resfinder_db/ $db/$DEST_DIR
echo "Done!!!"

echo "6. Download ResFinder-FG"
DEST_DIR="resfinder_fg"
create_dir "$db/$DEST_DIR"
curl -o $db/$DEST_DIR/ResFinder-FG_2.0.fasta https://raw.githubusercontent.com/RemiGSC/ResFinder_FG_Construction/main/output/RFG_db/ResFinder_FG.fasta
echo "Done!!!"

echo "7. Download Metal-resistance"
RECORD_URL="https://zenodo.org/api/records/8108201"
DEST_DIR="bacmet_db"
create_dir "$db/$DEST_DIR"
# Use curl to fetch the record data and jq to parse the JSON
curl -s "$RECORD_URL" | jq -r '.files[] | .links.self + " " + .key' | while read -r url filename; do
    # Download the file using curl, specifying the output filename
    data=`basename $filename`
    curl -o "$db/$DEST_DIR/$data" "$url"
    echo "Downloaded: $data"
    if file "$db/$DEST_DIR/$data" | grep -q "Zip archive data"; then
        unzip "$db/$DEST_DIR/$data" -o $db/$DEST_DIR/
    fi
done