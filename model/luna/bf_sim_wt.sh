#! /bin/bash

SPORE="pscale_a=0.7"
SIGB="pscale_b=0.25" # WT 
QP=""

MOD="bA=0.0;uA=0.0" # A cannot repress B. 
PSTR="sim_duration=6.5;initial_skip=1800.0;ascale_a=0.0;ascale_b=0.0"
SEED=$RANDOM


set -x #echo on
mono ../lbstools/build/custom_sweeper.exe \
	biofilm.crn \
	--simulations 10000 \
    --seed $SEED \
	--sweep-file bfsim_stress.crn \
	--output-name bfsim_b_qp${QP} \
    --parameters-file carsten_map_params.crn \
    --analysis-method bfsim_thresh \
	--parameter-overrides "${SPORE};${SIGB};${MOD};${PSTR}"
set +x #echo off

echo "seed was ${SEED}"
  