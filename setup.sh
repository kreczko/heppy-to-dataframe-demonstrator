#!/bin/bash

EXAMPLES_ROOT="$(dirname "$(readlink -f "$BASH_SOURCE[0]")")"
EXTERNALS=${EXAMPLES_ROOT}/external

ALPHATWIRL=${EXTERNALS}/alphatwirl
ALPHATWIRL_INTERFACE=${EXTERNALS}/interfaces

export PYTHONPATH="${ALPHATWIRL}:${ALPHATWIRL_INTERFACE}:${PYTHONPATH}"

pip install --user -r ${EXAMPLES_ROOT}/requirements.txt

PS1_PREFIX=RA1-ATwirl
