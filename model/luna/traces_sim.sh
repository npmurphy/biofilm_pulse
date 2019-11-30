#! /bin/bash


MOD="bA=0.0;uA=0.0"
PSTR="sim_duration=6.5;initial_skip=1800.0;ascale_a=0.0;ascale_b=0.0;stress=0.005;a0=1.0;b0=1.0"
MODE="pscale_a=0.7;pscale_b=0.25"  # WT pulse 
#MODE="pscale_a=0.7;pscale_b=0.5"  # 2x pulse
#MODE="pscale_a=3.6;pscale_b=2.0"  # WT bistable
#MODE="pscale_a=3.6;pscale_b=4.0"  # 2x bistable
#echo "pscale_a=${PSCALE_A};ascale_a=${ASCALE_A};pscale_b=${PSCALE_B};ascale_b=${ASCALE_B};${MOD};${PSTR}"
mono ../lbstools/build/simple_tracer.exe \
    biofilm.crn \
    --seed $RANDOM \
    --output-name bfsim_b_trace_seed${RANDOM} \
    --parameters-file carsten_map_params.crn \
    --parameter-overrides "${MOD};${PSTR};${MODE}"
  
