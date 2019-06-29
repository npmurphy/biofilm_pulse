

img_dir="/media/nmurphy/BF_Data_Orange/proc_data/lsm700_live20x_newstrain1/images/"
outputdir="/media/nmurphy/BF_Data_Orange/datasets/lsm700_live20x_newstrain1/" 
#subset="Set_2/48hrs"
#subset="Set_2/72hrs"
subset="Test_snaps/48hrs"
bgdir="${img_dir}/${subset}"

## First split out the channels and rotate to top up 
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/split_channels.py -f $f --rotate -2;
done

# Pick a good sample image to train random forrest
train_img="Set_1/48hrs/JLB106_48hrs_20x_2.lsm"
train_img="Set_1/48hrs/NEB008_48hrs_20x_3.lsm"

python bin/segment_10x.py --make_new_bfmask -f "${img_dir}/${train_img}"
# copy to to make an manualy corrected image for training
lsmfile=$(basename "$train_img");
filedirname="${lsmfile%.*}";
dirnameb=$(dirname "$train_img");
cp ${img_dir}/${dirnameb}/${filedirname}/${filedirname}_biofilmmask.mat \
   ${img_dir}/${dirnameb}/${filedirname}/${filedirname}_train.mat 

### Correct 
bright=0.7 # not wt
## Check each file was segmented ok. 
python bin/mask_maker.py \
    --remove_cr_from_mat_path \
    --mask_name train \
    --minidraw \
    -l ${img_dir}/${train_img} \
    --maxbright ${bright}

## Train random forrest on the training image
train_list=""
for f in "Set_1/48hrs/JLB106_48hrs_20x_2.lsm" "Set_1/48hrs/NEB008_48hrs_20x_3.lsm";
do 
    lsmfile=$(basename "$train_img");
    filedirname="${lsmfile%.*}";
    dirnameb=$(dirname "$train_img");
    train_list="${train_list} ${img_dir}/${dirnameb}/${filedirname}/${filedirname}_cr.tiff"
done
echo $train_list
#train_list=${img_dir}/${dirnameb}/${filedirname}/${filedirname}_cr.tiff
python bin/train_segmenter.py \
    --files ${train_list} \
    --remove_cr_from_mat_path \
    --model ${img_dir}/../rf_segmenter.pkl \
    --mask_name "train"

#Segment with random forest 
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    lsmfile=$(basename "$f");
    filedirname="${lsmfile%.*}";
    dirnameb=$(dirname "$train_img");
    seg_list=${bgdir}/${dirnameb}/${filedirname}/${filedirname}_cr.tiff
    python bin/segment_with.py \
        --model ${img_dir}/../rf_segmenter.pkl \
        --remove_cr_from_mat_path \
        --f ${seg_list} \
        --mask_name segmented 
    python bin/segment_10x.py \
        -f ${f} \
        --smooth_a_mask segmented \
        --mask_name biofilmmask
done



##############
# Check the segmentation
##############

# Set 1 48
#subset="Set_1/48hrs"
# filename="JLB106_48hrs_20x_1" 
# filename="JLB106_48hrs_20x_2"
# filename="JLB106_48hrs_20x_3"
# filename="NEB008_48hrs_20x_1"
# filename="NEB008_48hrs_20x_2"
# filename="NEB008_48hrs_20x_3" 
# filename="NEB009_48hrs_20x_1" # holes so cut off where the holes started
# filename="NEB009_48hrs_20x_2" # edge is a bit out of focus
# filename="NEB009_48hrs_20x_3" # very bright 
# filename="NEB011_48hrs_20x_1"
# filename="NEB011_48hrs_20x_2"
# filename="NEB011_48hrs_20x_3"
# filename="NEB012_48hrs_20x_1"
# filename="NEB012_48hrs_20x_2"
# filename="NEB012_48hrs_20x_3"
# filename="NEB024_48hrs_20x_1"
# filename="NEB024_48hrs_20x_2"
## filename="NEB025_48hrs_20x_1" ## strange, remove? 
# filename="NEB025_48hrs_20x_2"
# filename="NEB026_48hrs_20x_1"
# filename="NEB026_48hrs_20x_2"

# Set 2 48.
# filename="JLB088_48hrs_20x_1"
# filename="JLB088_48hrs_20x_2"
# filename="JLB088_48hrs_20x_3"
# filename="NEB_009_48hrs_20x_1"
# filename="NEB_009_48hrs_20x_2"
# filename="NEB_009_48hrs_20x_3"
# filename="NEB_009_48hrs_20x_4"
# filename="NEB_011_48hrs_20x_1"
# filename="NEB_011_48hrs_20x_2"
# filename="NEB_011_48hrs_20x_3"
# filename="NEB_018_48hrs_20x_1"
# filename="NEB_018_48hrs_20x_2"
# filename="NEB_018_48hrs_20x_3"
# filename="NEB_024_48hrs_20x_1"
# filename="NEB_024_48hrs_20x_2"
# filename="NEB_024_48hrs_20x_3"
# filename="NEB_026_48hrs_20x_1"
# filename="NEB_026_48hrs_20x_2"
# filename="NEB_026_48hrs_20x_3"
# filename="NEB_034_48hrs_20x_1"
# filename="NEB_034_48hrs_20x_2"
# filename="NEB_034_48hrs_20x_3"

# Set 1 72 hours 
# filename="JLB106_72hrs_20x_1" # has a big hole
# filename="NEB009_72hrs_20x_1"
# filename="NEB009_72hrs_20x_2"
# filename="NEB011_72hrs_20x_2"
# filename="NEB011_72hrs_20x_3"
# filename="NEB012_72hrs_20x_1"
# filename="NEB012_72hrs_20x_2"
# filename="NEB024_72hrs_20x_1"
# filename="NEB024_72hrs_20x_2"
# filename="NEB024_72hrs_20x_3"
# filename="NEB027_72hrs_20x_1" # funky 
# filename="NEB027_72hrs_20x_2"
# filename="NEB027_72hrs_20x_3"

# Set 2 72 hours 
# filename="JLB088_72hrs_20x_1"
# filename="JLB088_72hrs_20x_2"
# filename="JLB088_72hrs_20x_3"
# filename="NEB009_72hrs_20x_1"
# filename="NEB009_72hrs_20x_2" # has a hole
# filename="NEB009_72hrs_20x_3"
# filename="NEB011_72hrs_20x_1"
# filename="NEB011_72hrs_20x_2"
# filename="NEB011_72hrs_20x_3"
# filename="NEB018_72hrs_20x_1"
# filename="NEB018_72hrs_20x_2"
# filename="NEB018_72hrs_20x_3" # edge is out of focus, remove if strange
# filename="NEB024_72hrs_20x_1"
# filename="NEB024_72hrs_20x_2"
# filename="NEB024_72hrs_20x_3" # Also strane edge, candidate to remove
# filename="NEB024_72hrs_20x_4"
# filename="NEB026_72hrs_20x_1"
# filename="NEB026_72hrs_20x_2"
# filename="NEB026_72hrs_20x_3"
# filename="NEB034_72hrs_20x_1" # REMOVED edge is pretty bad, also strange shadows in the body 
# filename="NEB034_72hrs_20x_2"
# filename="NEB034_72hrs_20x_3"

# Testsnaps 48hrs
# filename="JLB088_48hrs_20x_1"
# filename="JLB088_48hrs_20x_2"
# filename="JLB088_48hrs_20x_3"
# filename="NEB008_48hrs_20x_1"
# filename="NEB008_48hrs_20x_2"
# filename="NEB008_48hrs_20x_3"
# filename="NEB011_48hrs_20x_1"
# filename="NEB011_48hrs_20x_2"
# filename="NEB011_48hrs_20x_3"
# filename="NEB011_48hrs_20x_4"
# filename="NEB011_48hrs_20x_5"
# filename="NEB018_48hrs_20x_1"
# filename="NEB018_48hrs_20x_2"
# filename="NEB018_48hrs_20x_3"
#filename="NEB028_48hrs_20x_1" ## not an approved strain
# filename="NEB034_48hrs_20x_1" # not great
# filename="NEB034_48hrs_20x_2"
# filename="NEB034_48hrs_20x_3"
# filename="NEB034_48hrs_20x_4"


filename="NEB_018_48hrs_20x_2"
subset="Set_2/48hrs"

bright=0.7 # not w
## Check each file was segmented ok. 
python bin/mask_maker.py \
    --remove_cr_from_mat_path \
    --mask_name biofilmmask \
    --minidraw \
    -l ${img_dir}/${subset}/${filename} \
    --maxbright ${bright}

 
#rerun="Set_1/48hrs/NEB009_48hrs_20x_1.lsm"; 
# Make the distance maps
for f in `ls ${bgdir}/*.lsm`; 
#for f in `ls ${img_dir}/${rerun}`; 
do
    echo ${f};
    lsmfile=$(basename "$f");
    filedirname="${lsmfile%.*}";
    dirnameb=$(dirname "$f");
    seg_list=${dirnameb}/${filedirname}/${filedirname}_cr.tiff
    #echo ${seg_list};
    python bin/mask_maker.py --edge_estimate --use_expanded_mask -f ${seg_list}
    # marks the pixels with distance from the top
    python bin/distmap_maker.py --filled edgemask  --magnification 20 -f  ${f}
done



widths='--sample_freq 0.25 --slice_width 0.5'
#python bin/gradient_10x_maker.py -f ${bgdir}/*.lsm ${widths} --subtractions none
# run with set_*/72hours
#python bin/gradient_10x_maker.py -f ${img_dir}/Set_*/72hrs/*.lsm ${widths} --subtractions none
python bin/gradient_10x_maker.py -f ${img_dir}/Test_snaps/48hrs/*.lsm ${widths} --subtractions none

python bin/gradient_10x_maker.py -f ${img_dir}/${rerun} ${widths} --subtractions none

#--bg_subtract  ${bgvalues}.json

cp ${img_dir}/../file_list.tsv ${outputdir}/file_list.tsv

python bin/data_aggregator_10x.py \
    -db ${outputdir}/file_list.tsv \
    --basepathtoignore ${img_dir}/ \
    --data distmap \
    --outfile ${outputdir}/gradient_data \
    -f  ${img_dir}/*/48hrs/*.lsm
    

python /home/nmurphy/work/projects/bf_pulse/analysis/summarise_live_20x_gradients.py