
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

bgvalues="datasets/LSM700_63x_sigb/bg_values"
# background and RFP only 
#filesBG=`find "proc_data/slice63x_bg_subtract/November_2014/63x_optimization" -name "*.lsm" -not -path "*/10x/*"`
filesBG=`find "${bgdir}" -name "*.lsm" ! -name "SigB*"`
# comparable SigB 
filesSB=`find "proc_data/slice63x_sigb_yfp/images/" -name "SigB_72*cent*stitched.tiff" -not -path "*/segmented/*"`
python bin/background_values.py --output ${bgvalues} --files ${filesBG} ${filesSB}


#############
# This was done before I started using these workflow files so
# this might not be complete
#################
#Joining the tiles 
python bin/stitcher_63x.py

#redoing edges to use the same technique as the spores
for f in `ls ${basedir}/${ldir}/*/*.tiff`; 
do
    echo ${f};
    python giant63_tighten_bfmask.py --lsm_file ${f} --make_backup --make_new_bfmask --single_slice
done
#split images into color channels

basedir=proc_data/slice63x_sigb_yfp/images/
#for f in `ls ${basedir}/${ldir}/SigB_72Hrs/*center_1*.tiff`; 
ldir=August_2015_data
ldir=July_2015_optimization_experiments
ldir=March_2015
ldir=May_2015_old_new_compar

for f in `ls ${basedir}/${ldir}/*/*.tiff`; 
do
    echo ${f};
    # python split_channels.py -f $f;
    # python giant63_mask_maker.py --classic63x -l ${f};
    #python giant63_distmap.py --filled edgemask  --magnification 63  -f  ${f};
    python bin/giant63_split_cellquant.py -f ${f} \
        --subtract_values_file ${bgvalues}.json \
        --subtract_red raw bg autofluor \
        --subtract_green raw bg autofluor bleedthrough;
done 

f=${basedir}/"August_2015_data/2xQP_48Hrs/2xQP_48hrs_center_5_240615_sect_stitched.tiff"
python bin/giant63_split_cellquant.py -f ${f} \
        --subtract_values_file ${bgvalues}.json \
        --subtract_red raw bg autofluor \
        --subtract_green raw bg autofluor bleedthrough;

#basedir="/Volumes/data/TeamJL/Niall/biofilm_slice/slice63x_analysis/"
python giant63_simple_agregate.py \
    -db ${basedir}/file_list.tsv \
    -o ${outdir}/bgsubv2_maxnorm_fixlab.h5 \
    --data cells \
    --remove_from_path ../data/bio_film_data/data_local_cache/slice63x_sigb_yfp/\
    -f ${basedir}/images/**/*.tsv

    #-o ${outdir}/lh1segment_data.h5 \
    #-o ${outdir}/lh1segment_bgsub_data.h5 \





## Checking segmentation. 
python giant63_mask_maker.py --mask_name segmented --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr.tiff
python giant63_mask_maker.py --mask_name edgemask --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr.tiff
python giant63_mask_maker.py --classic63x -f ${basedir}/${dirname}/${filename}/${filename}_cr.tiff
python giant63_distmap.py --filled edgemask  --magnification 63  -f  ${basedir}/${dirname}/${filename}.tiff


######################
## list of bad images
###############
basedir="data/orig_63xset/"
# Seemed ok
fpath="images/August_2015_data/SigB_24Hrs/SigB_24hrs_center_1_230615_sect_stitched"

fpath="images/August_2015_data/SigB_36Hrs/SigB_36hrs_center_4_230615_sect_stitched"
fpath="images/August_2015_data/SigB_48Hrs/SigB_48hrs_edge_6_240615_sect_stitched"
fpath="images/August_2015_data/SigB_72Hrs/SigB_72hrs_edge_5_240615_sect_stitched"
fpath="images/July_2015_optimization&experiments/SigB_24Hrs/SigB_24hrs_edge_2_080615_sect_stitched"
fpath="images/July_2015_optimization&experiments/SigB_72Hrs/SigB_72hrs_edge_1_120615_sect_stitched"
fpath="images/March_2015/SigB_Eugene2/SigB_96hrs_edge_4_stitched"
fpath="images/May_2015_old_new_compar/SigB_26Hrs_Feb15_set/SigB_26Hrs_center5_Feb15_sect_stitched"
fpath="images/May_2015_old_new_compar/SigB_26Hrs_Feb15_set/SigB_26Hrs_edge2_Feb15_sect_stitched"
fpath="images/May_2015_old_new_compar/SigB_26Hrs_Feb15_set/SigB_26Hrs_edge_Feb15_sect_stitched"
fpath="images/May_2015_old_new_compar/SigB_96hrs_July_14_sect/SigB_96Hrs_center3_Jul_14_sect_stitched"
fpath="images/May_2015_old_new_compar/SigB_96hrs_July_14_sect/SigB_96Hrs_center_Jul_14_sect_stitched"
fpath="images/May_2015_old_new_compar/SigB_96hrs_July_14_sect/SigB_96Hrs_edge4_Jul_14_sect_stitched"
python giant63_mask_maker.py --remove_cr_from_mat_path --mask_name segmented --remove_cr_from_mat_pat --minidraw -l ${basedir}/${fpath}.lsm --maxbright 0.25
python giant63_mask_maker.py --remove_cr_from_mat_path --mask_name edgemask --remove_cr_from_mat_pat --minidraw -l ${basedir}/${fpath}.lsm --maxbright 0.25

