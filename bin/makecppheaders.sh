#!/usr/bin/env bash

# This script hacks at making header files from c++ files.
# It is a fun experiment that ended up being very useful.
#
# Obviously, it's not a makeheaders replacement, though it does
# identify namespaces (but doesn't close them!)
#

fp="/tmp/makeheader.1.$$"

# grep: extract includes
# grep: extract namespace definitions (but not closing curly bracket)
# grep: extract function definitions (but not entirely if they continue onto two lines)
# sed: add semicolons where appropriate
# tac sed: inject 2 blank lines after last include
# 2 seds: add notes where user should complete the header file.

include='^#include +("\S+"|<\S+>)'
namespace='^ *namespace +(\w|\d)+ *\{'
funcdef='\s*(\w|\d)+( *(\w|\d)+| *(\w|\d)+ +(\w|\d)+|) +(\w|\d)+'\
'\(((\w|\d)+=.*? *,? *|(\w|\d)+| *$|\s*\)\s*{)'

grep -E '('\
"$include"\
"|$namespace"\
"|$funcdef"\
')' $1 \
  | cut -f2- -d: \
  | sed -E 's/ +\{/;/'\
  | sed -E 's/ *(namespace *(\w|\d)+);/\1 {/'\
  | tac | sed -E '0,/'"$include"'/s/('"$include"').*?$/\n\n\1/' | tac\
  |sed -E 's/(.*\( *$)/\1  \/\/ TODO: COMPLETE THIS LINE.../'\
  |sed -E 's/('"$namespace"')/\1  \/\/ TODO: CLOSE THIS SECTION/'\



