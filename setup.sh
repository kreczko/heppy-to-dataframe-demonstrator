#!/bin/bash

EXAMPLES_ROOT="$(dirname "$(readlink -f "$BASH_SOURCE[0]")")"
EXTERNALS=${EXAMPLES_ROOT}/external

ALPHATWIRL=${EXTERNALS}/alphatwirl
ALPHATWIRL_INTERFACE=${EXTERNALS}/alphatwirl-interface

export PYTHONPATH="${EXAMPLES_ROOT}:${ALPHATWIRL}:${ALPHATWIRL_INTERFACE}${PYTHONPATH+:${PYTHONPATH}}"

pip install --user -r ${EXAMPLES_ROOT}/requirements.txt

PS1_PREFIX=RA1-ATwirl

DataDir=data
LocalDataFile=/hdfs/SUSY/RA1/80X/MC/20170129_Summer16_newJECs/AtLogic_MCSummer16_SM/ZJetsToNuNu_HT100to200_madgraph/treeProducerSusyAlphaT/tree.root
OutLocalDataFile=$(cut -f7,9-11 -d/ <<<"$LocalDataFile" |sed -e 's%/%--%g')
( 
mkdir -p "$DataDir"
cd "$DataDir"
if [ ! -r "${OutLocalDataFile}" ];then
    echo "Fetching a local data file for you"
    (
    set -x
    cp "$LocalDataFile" "$OutLocalDataFile"
    )
fi
)
