#!/bin/bash

# nastavenia
FAKULTA="FMFI"

LAST_YEAR=$(date +%Y -d "last year")
THIS_YEAR=$(date +%Y)
SEASON="$LAST_YEAR%252F$THIS_YEAR"
URL="https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty"


# spracovanie SK informacnych listov
lynx --dump "$URL/$SEASON/$FAKULTA/SK/" | awk '/http/{print $2}' | grep xml > files_sk.txt;

mkdir -p xml_files_sk;
wget -N -q -i files_sk.txt -P xml_files_sk;

python AIS_XML2HTML.py xml_files_sk "../public/SK"

# spracovanie EN informacnych listov
lynx --dump "$URL/$SEASON/$FAKULTA/EN/" | awk '/http/{print $2}' | grep xml > files_en.txt;

mkdir -p xml_files_en;

wget -N -q -i files_en.txt -P xml_files_en;
python AIS_XML2HTML.py --lang en xml_files_en "../public/EN"


# predmety statnych skusok maju inu sablonu aj ine XML, preto sa spracuvaju samostatne
./vygeneruj_statne-skusky.sh
