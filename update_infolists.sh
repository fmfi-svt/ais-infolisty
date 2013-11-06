#!/bin/bash

# nastavenia
FAKULTA="FMFI"
DIR="/var/www/sluzby/infolist"

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


# spracovanie SK informacnych listov
lynx --dump "$URL/$SEASON/$FAKULTA/SK/" | awk '/http/{print $2}' | grep xml > "$DIR/scripts/files_sk.txt";

mkdir -p "$DIR/scripts/xml_files_sk";
wget -N -q -i "$DIR/scripts/files_sk.txt" -P "$DIR/scripts/xml_files_sk";

python "$DIR/scripts/AIS_XML2HTML.py" "$DIR/scripts/xml_files_sk" "$DIR/public/SK";

# spracovanie EN informacnych listov
lynx --dump "$URL/$SEASON/$FAKULTA/EN/" | awk '/http/{print $2}' | grep xml > "$DIR/scripts/files_en.txt";

mkdir -p "$DIR/scripts/xml_files_en";

wget -N -q -i "$DIR/scripts/files_en.txt" -P "$DIR/scripts/xml_files_en";
python "$DIR/scripts/AIS_XML2HTML.py" --lang en "$DIR/scripts/xml_files_en" "$DIR/public/EN";


# predmety statnych skusok maju inu sablonu aj ine XML, preto sa spracuvaju samostatne
sh "$DIR/scripts/vygeneruj_statne-skusky.sh";

