#!/usr/bin/env bash
DIR=$( cd "$( dirname "$0" )" && pwd )


# Flavonoids Database
# http://www.ars.usda.gov/Services/docs.htm?docid=6231
#
# The database contains values for 506 food items for five subclasses of flavonoids:
#
# FLAVONOLS: Quercetin, Kaempferol, Myricetin, Isorhamnetin
# FLAVONES: Luteolin, Apigenin
# FLAVANONES: Hesperetin, Naringenin, Eriodictyol
# FLAVAN-3-OLS: (+)-Catechin, (+)-Gallocatechin, (-)-Epicatechin, (-)-Epigallocatechin, (-)-Epicatechin 3-gallate, (-)-Epigallocatechin 3-gallate, Theaflavin, Theaflavin 3-gallate, Theaflavin 3'-gallate, Theaflavin 3,3' digallate, Thearubigins
# ANTHOCYANIDINS: Cyanidin, Delphinidin, Malvidin, Pelargonidin, Peonidin, Petunidin
function dl_flavonoid() {
(
echo "download USDA Flavonoid Database"
mkdir $DIR/data/usda_flavonoid_db
cd $DIR/data/usda_flavonoid_db
wget \
  http://www.ars.usda.gov/SP2UserFiles/Place/12354500/Data/Flav/Flav_R03-1.mdb \
  -nc -c
echo "...extracting tables to csv"
mdb-tables ./Flav_R03-1.mdb \
  |tr -s ' ' '\n'\
  |xargs -I{} sh -c 'mdb-export ./Flav_R03-1.mdb {} > "{}.csv"'
)
}


# Food Nutrition Database (Standard Reference)
# http://www.ars.usda.gov/Services/docs.htm?docid=8964

function dl_nutrution() {
(
echo "download USDA Food Nutrition Database (Standard Reference)"
mkdir $DIR/data/usda_nutrition_db/
cd $DIR/data/usda_nutrition_db
wget \
  https://www.ars.usda.gov/SP2UserFiles/Place/12354500/Data/SR27/dnload/sr27db.zip \
  -nc -c
[ -e "sr27.accdb" ] || unzip *.zip
echo "...extracting tables to csv"
mdb-tables ./sr27.accdb \
  |tr -s ' ' '\n'\
  |xargs -I{} sh -c 'mdb-export ./sr27.accdb {} > "{}.csv"'
)
}


dl_flavonoid
dl_nutrution
