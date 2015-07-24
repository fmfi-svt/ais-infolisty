#!/bin/bash

# nastavenia
if [[ -z "$FAKULTA" ]]
then
  FAKULTA="FMFI"
fi

SCRIPTS="$(readlink -f "$(dirname $0)")"
TARGET_DIR="../infolist"

if [ `date +%m` -gt 7 ]; then
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
    datadir="$SCRIPTS/$FAKULTA"
    filelist="$datadir/files_${lang,,}.txt"
    xmldir="$datadir/xml_files_${lang,,}"
    
    mkdir -p "$datadir"

    lynx --dump "$URL/$SEASON/$FAKULTA/${lang^^}/" | awk '/http/{print $2}' | grep xml > "$filelist";
    
    mkdir -p "$xmldir";
    wget -N -q -i "$filelist" -P "$xmldir";
}

download_data_py() {
    python "$SCRIPTS/update_infolists.py" --source $URL --faculty $FAKULTA --lang $1;
}


process_data() {
    # Spracujeme stiahnute subory
    python "$SCRIPTS/AIS_XML2HTML.py" "$SCRIPTS/$FAKULTA/xml_files_sk" "$TARGET_DIR/public/SK" "templates/template_table_sk.html";
    python "$SCRIPTS/AIS_XML2HTML.py" --lang en "$SCRIPTS/$FAKULTA/xml_files_en" "$TARGET_DIR/public/EN" "templates/template_table_en.html";

    python "$SCRIPTS/AIS_XML2HTML.py" --mode statnice "$SCRIPTS/$FAKULTA/xml_files_sk" "$TARGET_DIR/public/SK" "templates/template_statne-skusky_table_sk.html";
    python "$SCRIPTS/AIS_XML2HTML.py" --mode statnice --lang en "$SCRIPTS/$FAKULTA/xml_files_en" "$TARGET_DIR/public/EN" "templates/template_statne-skusky_table_en.html";

    # statnice

    # predmety statnych skusok maju inu sablonu aj ine XML, preto sa spracuvaju samostatne
    # python "$SCRIPTS/AIS_XML2HTML_statne-skusky.py" "$SCRIPTS/$FAKULTA/xml_files_sk" "$TARGET_DIR/public/SK";
    # python "$SCRIPTS/AIS_XML2HTML_statne-skusky.py" --lang en "$SCRIPTS/$FAKULTA/xml_files_en" "$TARGET_DIR/public/EN";
}

download_data_py sk
download_data_py en

if [ "$1" != "--download-only" ]
then
    process_data
fi
