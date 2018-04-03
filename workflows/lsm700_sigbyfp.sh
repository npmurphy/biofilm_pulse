
#############################
# Background subtraction 
#############################
bgdir="proc_data/slice63x_bg_subtract_eugene2/December_2014/"
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/split_channels.py -f $f;
    python bin/mask_maker.py --classic63x -l ${f};
done

for f in `ls ${bgdir}/*.lsm`; 
do
    lsmfile=$(basename "$f");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    # make a background file that we can edit for propper background
    cp ${bgdir}/${filename}/${filename}_segmented.mat ${bgdir}/${filename}/${filename}_background.mat;
    # remove these files we wont use.
    rm ${bgdir}/${filename}/${filename}_biofilmmask.mat;
    rm ${bgdir}/${filename}/${filename}_edgemask.mat;
done 

#find ${bgdir}/ -name "*.lsm"  -exec basename {} \;

#fpath="RFP_only_72hrs_base2_2_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_base_2_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_base_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_middle_2_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_middle_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_top_2_Eugene_2_settings.lsm"
#fpath="RFP_only_72hrs_top_Eugene_1_modified_settings.lsm" # actually is eugene 2
#fpath="SigB_72hrs_center_base2_Eugene2_set.lsm"
#fpath="SigB_72hrs_center_base_Eugene2_set.lsm"
#fpath="SigB_72hrs_center_middle2_Eugene2_set.lsm"
#fpath="SigB_72hrs_center_middle_Eugene2_set.lsm"
#fpath="SigB_72hrs_center_top2_Eugene2_set.lsm"
#fpath="SigB_72hrs_center_top_Eugene2_set.lsm"
#fpath="WT_72hrs_center_base_Eugene_2_settings.lsm"
#fpath="WT_72hrs_center_top_Eugene_2_settings.lsm"
#bright=0.01 # wildtype
bright=0.7 # not wt

python bin/mask_maker.py --remove_cr_from_mat_path --mask_name segmented --remove_cr_from_mat_pat --minidraw -l ${bgdir}/${fpath} --maxbright ${bright}
python bin/mask_maker.py --remove_cr_from_mat_path --mask_name background --remove_cr_from_mat_pat --minidraw -l ${bgdir}/${fpath} --maxbright ${bright}



## Compute the BG values

bgvalues="datasets/LSM700_63x_sigb/bg_values_eugene2"
# background and RFP only 
#filesBG=`find "proc_data/slice63x_bg_subtract/November_2014/63x_optimization" -name "*.lsm" -not -path "*/10x/*"`
filesBG=`find "${bgdir}" -name "*.lsm" ! -name "SigB*"`
# comparable SigB 
filesSB=`find "proc_data/slice63x_sigb_yfp/images/" -name "SigB_72*cent*stitched.tiff" -not -path "*/segmented/*"`
python bin/background_values.py --output ${bgvalues} --files ${filesBG} ${filesSB}




## Joining the tiles 
#python stitcher_63x.py

## Segmenting the biofilm part. 

## get the mean signal 

## segment the cells 

## generate the dataset 