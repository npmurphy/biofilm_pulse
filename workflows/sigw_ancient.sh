
#############################
# Background subtraction 
#############################
#bgdir="proc_data/slice63x_bg_subtract_eugene2/December_2014/"
basedir="/media/nmurphy/BF_Data_Orange/proc_data/frozen_sigW/"
bgdir="${basedir}"
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/split_channels.py -f $f --rotate -1;
    python bin/mask_maker.py --classic63x -l ${f};
done

ls -1 $bgdir/*.lsm > ${basedir}/set.txt
ls -1 $bgdir/*.lsm

filename="RFP_only_48hrs_center_1"
filename="RFP_only_48hrs_center_2"
filename="RFP_only_48hrs_center_3"
filename="SigW_48hrs_center_1"
filename="SigW_48hrs_center_2"
filename="SigW_48hrs_center_3"
filename="WT_48hrs_center_1"
filename="WT_48hrs_center_2"

bright=0.7 # not wt
## Check each file was segmented ok. 
python bin/mask_maker.py \
    --remove_cr_from_mat_path \
    --mask_name segmented\
    --minidraw \
    -l ${bgdir}/${filename} \
    --maxbright ${bright}
    #k--mask_name biofilmmask \

for f in `ls ${bgdir}/*.lsm`; 
#for f in `ls ${bgdir}/SigW_48hrs_center_1.lsm`; 
do
    echo ${f};
    python bin/mask_maker.py --edge_estimate -l ${f};
done



#check these
python bin/mask_maker.py --remove_cr_from_mat_path --mask_name edgemask --minidraw -l ${bgdir}/${filename}

for f in `ls ${bgdir}/*/*biofilmmask.mat`; 
do
    echo ${f};
    cp ${f} "${f/biofilmmask/segmented}" 
done

filesBG=`ls -1 ${bgdir}/*.lsm`
python bin/background_mask_10x.py -f ${filesBG}

# Actually generate the background values. 
bgvalues="bg_vals.json"
python bin/background_values.py --output ${bgdir}/${bgvalues} --files ${filesBG}

## make the distance from top file
#for f in `ls ${bgdir}/SigW_48hrs_center_1.lsm`; 
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/distmap_maker.py --filled edgemask --magnification 10  -f  ${f};
done


for i in `ls ${bgdir}/SigW*.lsm`;
do
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    echo ${dirnameb} $filename
    # segments, 
    python bin/segment_10x.py --make_new_bfmask -f ${bgdir}/${dirname}/${filename}.tiff
    # # marks the tops
    python bin/mask_maker.py --edge_estimate --use_expanded_mask -f ${bgdir}/${dirname}/${filename}/${filename}_cr.tiff
    # # marks the pixels with distance from the top
    python bin/distmap_maker.py --filled edgemask  --magnification 10 -f  ${bgdir}/${dirname}/${filename}.tiff 
done

widths='--sample_freq 0.25 --slice_width 0.5'
python bin/gradient_10x_maker.py -f ${bgdir}/SigW*.lsm ${widths} --bg_subtract  ${bgdir}/${bgvalues}.json

outputdir="/media/nmurphy/BF_Data_Orange/datasets/ancient_sigw"
#cp ${bgdir}/file_list.tsv ${outputdir}/file_list.tsv
python bin/data_aggregator_10x.py \
    -db ${outputdir}/file_list.tsv \
    --basepathtoignore /media/nmurphy/BF_Data_Orange/proc_data/ \
    --data distmap \
    --outfile ${outputdir}/gradient_data \
    -f ${bgdir}/SigW_48hrs_center_1.lsm   ${bgdir}/SigW_48hrs_center_3.lsm  


python analysis/summarise_10x_sigw.py
    

