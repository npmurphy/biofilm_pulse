
#############################
# Background subtraction 
#############################
#bgdir="proc_data/slice63x_bg_subtract_eugene2/December_2014/"
basedir="/media/nmurphy/BF_Data_Orange/proc_data/new_strain_snaps1/images/"
bgdir="${basedir}/Set_2/72hrs/63x"
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/split_channels.py -f $f --rotate -1;
    python bin/mask_maker.py --classic63x -l ${f};
done

#ls -1 $bgdir/*.lsm > ${basedir}/set272.txt

#filename="JLB106_72hrs_63x_2_base"
#filename="JLB106_72hrs_63x_3"
#filename="NEB009_72hrs_63x_3"
# filename="NEB011_72hrs_63x_1"
# filename="NEB011_72hrs_63x_2"
# filename="NEB011_72hrs_63x_3"
# filename="NEB011_72hrs_63x_4"
# filename="NEB012_72hrs_63x_3"
# filename="NEB024_72hrs_63x_2"
# filename="NEB024_72hrs_63x_4"
# filename="NEB027_72hrs_63x_2_fast"

# filename="JLB088_72hrs_63x_1"
# filename="JLB088_72hrs_63x_2_base"
# filename="JLB088_72hrs_63x_3"
# filename="JLB088_72hrs_63x_4"
# filename="NEB009_72hrs_63x_2"
# filename="NEB009_72hrs_63x_3"
# filename="NEB009_72hrs_63x_4"
# filename="NEB011_72hrs_63x_1"
# filename="NEB011_72hrs_63x_2"
# filename="NEB011_72hrs_63x_3"
# filename="NEB011_72hrs_63x_4"
# filename="NEB018_72hrs_63x_1"
# filename="NEB018_72hrs_63x_2"
# filename="NEB018_72hrs_63x_3"
# filename="NEB018_72hrs_63x_4_base"
# filename="NEB024_72hrs_63x_1"
# filename="NEB024_72hrs_63x_2"
# filename="NEB024_72hrs_63x_3"
# filename="NEB024_72hrs_63x_4"
# filename="NEB026_72hrs_63x_1"
# filename="NEB026_72hrs_63x_2"
# filename="NEB026_72hrs_63x_3"
# filename="NEB026_72hrs_63x_4"
# filename="NEB034_72hrs_63x_1"
# filename="NEB034_72hrs_63x_2"
filename="NEB034_72hrs_63x_3"


bright=0.7 # not wt
## Check each file was segmented ok. 
python bin/mask_maker.py \
    --remove_cr_from_mat_path \
    --mask_name biofilmmask \
    --minidraw \
    -l ${bgdir}/${filename} \
    --maxbright ${bright}

for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/mask_maker.py --edge_estimate -l ${f};
done

#check these
python bin/mask_maker.py --remove_cr_from_mat_path --mask_name edgemask --minidraw -l ${bgdir}/${filename}

## make the distance from top file
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/distmap_maker.py --filled edgemask --magnification 63  -f  ${f};
done

############
## Segment the images
############
for f in `ls ${bgdir}/*.lsm`; 
do
    echo ${f};
    python bin/giant63_split_cellquant.py -f ${f} --cell_width_pixels 12 
done

## Make a file_db with ls 
ls ${bgdir}/*.lsm > ${bgdir}/allfiles.txt
# rm ${bgdir}/allfiles.txt

### Collect data into one file
outputdir="/media/nmurphy/BF_Data_Orange/datasets/new_strain_snaps1/"
echo ${basedir}/
mkdir $outputdir
python bin/giant63_simple_agregate.py \
    -db ${basedir}/../file_list.tsv \
    -o ${outputdir}/single_cell_data.h5 \
    --data cells \
    --bad_db ${basedir}/../bad_images.tsv \
    --remove_from_path ${basedir} \
    -f ${basedir}/**/*.tsv
cp ${basedir}/../file_list.tsv ${outputdir}/file_list.tsv
 
