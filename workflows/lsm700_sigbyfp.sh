

## Joining the tiles 
python stitcher_63x.py

## Segmenting the biofilm part. 

## getting background and autflouresence data.
bgvalues="/Users/npm33/bf_pulse/datasets/LSM700_63x_sigb/bg_values_redux2"
# background and RFP only 
filesBG=`find "proc_data/slice63x_bg_subtract/November_2014/63x_optimization" -name "*.lsm" -not -path "*/10x/*"`
# comparable SigB 
filesSB=`find "proc_data/slice63x_sigb_yfp/images/" -name "SigB_72*cent*stitched.tiff" -not -path "*/segmented/*"`
python bin/background_values.py --output ${bgvalues} --files ${filesBG} ${filesSB}

## get the mean signal 

## segment the cells 

## generate the dataset 