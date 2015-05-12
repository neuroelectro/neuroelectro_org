#!/bin/bash
# The script sets all the required flags and environment variables that the Neuroelectro_setup_script relies on
# Place this script into neuroelectro_org folder and run it by typing " eval $(./Neuroelectro_script_exports.sh) "

echo "export CFLAGS=-Qunused-arguments;"
echo "export CPPFLAGS=-Qunused-arguments;"

currDir=${PWD}
parentDir="$(dirname "$currDir")" 

CMD=""
[ "$PYTHONPATH" == "" ] && CMD="export PYTHONPATH=$parentDir" || CMD="export PYTHONPATH=$PYTHONPATH:$parentDir"
echo $CMD
