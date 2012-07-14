#!/bin/sh
set -e
# assuming pip and virtualenv are installed...

# install dependencies in virtualenv
virtualenv ./alex_gaudio_demo
. ./alex_gaudio_demo/bin/activate

pip install numpy
pip install nltk
pip install pandas

# unzip data
tar xvzf Artist_lists_small.txt.tar.gz

# run
python frequently_occurring_pairs.py
