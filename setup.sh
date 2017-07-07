#!/bin/bash

SoftwareSetup=/cvmfs/sft.cern.ch/lcg/views/LCG_latest/x86_64-slc6-gcc62-opt/setup.sh
if [ -r "${SoftwareSetup}" ]; then
    source "${SoftwareSetup}"
fi

EXAMPLES_ROOT="$(dirname "$(readlink -f "$BASH_SOURCE[0]")")"
EXTERNALS=${EXAMPLES_ROOT}/external

ALPHATWIRL=${EXTERNALS}/alphatwirl
ALPHATWIRL_INTERFACE=${EXTERNALS}/alphatwirl-interface

export PYTHONPATH="${EXAMPLES_ROOT}:${ALPHATWIRL}:${ALPHATWIRL_INTERFACE}${PYTHONPATH+:${PYTHONPATH}}"

PS1_PREFIX=demo-ATwirl

DataDir=data
LocalDataFile=/hdfs/SUSY/RA1/80X/MC/20170129_Summer16_newJECs/AtLogic_MCSummer16_SM/ZJetsToNuNu_HT100to200_madgraph/treeProducerSusyAlphaT/tree.root
OutLocalDataFile=$(cut -f7,9-11 -d/ <<<"$LocalDataFile" |sed -e 's%/%--%g')
( 
mkdir -p "$DataDir"
cd "$DataDir"
if [ ! -r "${OutLocalDataFile}" ] ;then
    if [ -r "${LocalDataFile}" ]; then
        echo "Fetching a local data file for you"
        (
        set -x
        cp "$LocalDataFile" "$OutLocalDataFile"
        )
    else
        echo "Tried to fetch a local testing data file for you but couldn't find one"
    fi
fi
)
