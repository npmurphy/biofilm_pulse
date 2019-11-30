#! /bin/bash

SPORE="pscale_a=0.7"
SIGB="pscale_b=0.25" # WT 
QP=""

MOD="bA=0.0;uA=0.0" # A cannot repress B. 
PSTR="sim_duration=6.5;initial_skip=1800.0;ascale_a=0.0;ascale_b=0.0"
SEED=$RANDOM


Parameters to run with [|("a0", 0.05); ("ascale_a", 0.0); ("ascale_b", 0.0); ("b0", 0.05); ("bA", 0.0);
  ("bB", 1.0); ("dm", 0.005); ("dp", 0.005); ("initial_skip", 1800.0);
  ("pscale_a", 0.7); ("pscale_b", 0.25); ("sim_duration", 6.5);
  ("sim_hour", 3600.0); ("sim_minute", 60.0); ("stress", 0.0); ("trA", 0.05);
  ("trB", 0.05); ("uA", 0.0); ("uB", 0.1)|]

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
# example of what final output should look like
#custom_sweeper.exe biofilm.crn 
#	--simulations 10000
#	--seed 5110
#	--sweep-file bfsim_stress.crn 
#   --output-name bfsim_b_qp 
#   --parameters-file carsten_map_params.crn
#   --analysis-method bfsim_thresh 
#   --parameter-overrides 'pscale_a=0.7;pscale_b=0.25;bA=0.0;uA=0.0;sim_duration=6.5;initial_skip=1800.0;ascale_a=0.0;ascale_b=0.0'

echo "seed was ${SEED}"
  