#!/bin/bash

# nastavenia
FAKULTA="FMFI"
SCRIPTS="$(readlink -f "$(dirname $0)")"
TARGET_DIR="/var/www/sluzby/infolist"

if [ `date +%m` -gt 8 ]; then
    # zimny semester
    LAST_YEAR=$(date +%Y)
    THIS_YEAR=$(date +%Y -d "next year")
else
    # letny semester
    LAST_YEAR=$(date +%Y -d "last year")
    THIS_YEAR=$(date +%Y)
fi
SEASON="$LAST_YEAR-$THIS_YEAR"
URL="https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty"

download_data() {
    lang="$1"
    filelist="$SCRIPTS/files_${lang,,}.txt"
    xmldir="$SCRIPTS/xml_files_${lang,,}"

    lynx --dump "$URL/$SEASON/$FAKULTA/${lang^^}/" | awk '/http/{print $2}' | grep xml > "$filelist";
    
    mkdir -p "$xmldir";
    wget -N -q -i "$filelist" -P "$xmldir";
}


process_data() {
    # Spracujeme stiahnute subory
    python "$SCRIPTS/AIS_XML2HTML.py" "$SCRIPTS/xml_files_sk" "$TARGET_DIR/public/SK";
    python "$SCRIPTS/AIS_XML2HTML.py" --lang en "$SCRIPTS/xml_files_en" "$TARGET_DIR/public/EN";

    # predmety statnych skusok maju inu sablonu aj ine XML, preto sa spracuvaju samostatne
    sh "$SCRIPTS/vygeneruj_statne-skusky.sh";
}

download_data sk
download_data en

if [ "$1" != "--download-only" ]
then
    process_data
fi
