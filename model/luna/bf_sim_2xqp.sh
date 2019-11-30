#! /bin/bash

SPORE="pscale_a=0.7"
SIGB="pscale_b=0.5" # 2xQP (double wild type)
QP="x2"

MOD="bA=0.0;uA=0.0" # A cannot repress B. 
# Run simulation for 6.5 simulated hours
# drop the first 1800 seconds to get over the transient phase. 
# the ascale constant expression rates are off
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
	--parameter-overrides "${1};${MOD};${PSTR}"
set +x #echo off

echo "seed was ${SEED}"
  