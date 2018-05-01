
# new data. 
data_dir="/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks"

dset="BF_12hoursnaps1"
pttwo="Final_transmited_light
beads_end_g100_r100
beads_end_g40_r50
"
## There are a few substitutions.
#mv ${data_dir}/${dset}/60hr_position11_2/60hr_position11_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position11_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position11_2/60hr_position11_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position11_ch01.tif;
#mv ${data_dir}/${dset}/60hr_position16_2/60hr_position16_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position16_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position16_2/60hr_position16_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position16_ch01.tif;
#mv ${data_dir}/${dset}/60hr_position40_2/60hr_position40_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position40_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position40_2/60hr_position40_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position40_ch01.tif;
#mv ${data_dir}/${dset}/72hr_position39_2/72hr_position39_2_ch00.tif ${data_dir}/${dset}/72hr_timepoint/Position39_ch00.tif;
#mv ${data_dir}/${dset}/72hr_position39_2/72hr_position39_2_ch01.tif ${data_dir}/${dset}/72hr_timepoint/Position39_ch01.tif;

#dset="BF_12hoursnaps2"
dset="BF_12hoursnaps3"

# Turn from leica format to something easier to deal with
find ${data_dir}/${dset} -name .DS_Store -exec rm {} +
#for d in ${pttwo}; do
for d in ${data_dir}/${dset}/*timepoint/; do
    echo "D" $d;
    # #d="${data_dir}/${dset}/${d}"
    #mkdir "${d}/MetaData/"
    for p in ${d}/*0*/; do
        echo "P" ${p}
        #mv ${p}/*.tif ${p}/../
        #mv -f "${p}/MetaData/"* "${d}/MetaData/"
        #rmdir ${p}/MetaData
        rmdir ${p}
    done
done

time=12; pos=18
time=12; pos=21
time=12; pos=29
time=48; pos=13

time=60; pos="02"
time=60; pos="10"
time=60; pos="22"
time=60; pos="34"

time=72; pos="21"
time=72; pos="22"
time=72; pos="25"
time=72; pos="30"
time=72; pos="34"
time=72; pos="38"



chans="00
01
02"
for ch in $chans; do
    mv ${data_dir}/${dset}/${time}hr_timepoint/Position0${pos}_ch${ch}.tif ${data_dir}/${dset}/${time}hr_timepoint/Position0${pos}_ch${ch}_o.tif 
    mv ${data_dir}/${dset}/${time}hr_position${pos}_2/${time}hr_position${pos}_2_ch${ch}.tif ${data_dir}/${dset}/${time}hr_timepoint/Position0${pos}_ch${ch}.tif;
done
mv -f "${data_dir}/${dset}/${time}hr_position${pos}_2/MetaData/"* ${data_dir}/${dset}/${time}hr_timepoint//MetaData/
rmdir "${data_dir}/${dset}/${time}hr_position${pos}_2/MetaData/"
rmdir "${data_dir}/${dset}/${time}hr_position${pos}_2"


#mv ${data_dir}/${dset}/60hr_position11_2/60hr_position11_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position11_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position11_2/60hr_position11_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position11_ch01.tif;
#mv ${data_dir}/${dset}/60hr_position16_2/60hr_position16_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position16_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position16_2/60hr_position16_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position16_ch01.tif;
#mv ${data_dir}/${dset}/60hr_position40_2/60hr_position40_2_ch00.tif ${data_dir}/${dset}/60hr_timepoint/Position40_ch00.tif;
#mv ${data_dir}/${dset}/60hr_position40_2/60hr_position40_2_ch01.tif ${data_dir}/${dset}/60hr_timepoint/Position40_ch01.tif;
#mv ${data_dir}/${dset}/72hr_position39_2/72hr_position39_2_ch00.tif ${data_dir}/${dset}/72hr_timepoint/Position39_ch00.tif;
#mv ${data_dir}/${dset}/72hr_position39_2/72hr_position39_2_ch01.tif ${data_dir}/${dset}/72hr_timepoint/Position39_ch01.tif;


##############
#Stich 
############
chans="00
01
02"
timepoint="7hr_timepoint" 
timepoint="12hr_timepoint" 
timepoint="24hr_timepoint" 
timepoint="36hr_timepoint" 
timepoint="48hr_timepoint" 
timepoint="60hr_timepoint" 
timepoint="72hr_timepoint" 
timepoint="84hr_timepoint" 
timepoint="96hr_timepoint"
timepoint="Test_point_7h48min" 
timepoint="Final_transmited_light"

#declare -a columns=("1" "2" "3" "4" "5" "6" "7" "8" "9" "10")
declare -a columns=("1" "2" "3" "4" "5" "6" "7" "8" "9" "10")

for col in "${columns[@]}"; do   
    for ch in $chans; do
        flist=`python ${data_dir}/${dset}/generate_columns.py --prematter ${data_dir}/${dset}/${timepoint}/ --channel ${ch} --column ${col}`
        python bin/stitcher_simple.py --files ${flist} \
             --output ${data_dir}/${dset}/${timepoint}/Column_${col}_ch${ch}.tif;
    done
done

mkdir ${data_dir}/${dset}/${timepoint}/unstitched
mv ${data_dir}/${dset}/${timepoint}/Position*.tif ${data_dir}/${dset}/${timepoint}/unstitched/

##################
### We could use the 10x tools for this. 
####################

### 
#Process images.
#python bin/mask_maker.py --mask_name biofilmmask --remove_cr_from_mat_pat --minidraw -l ${bgdir}/${fpath} --maxbright ${bright}
data_dir="/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks"
dset="BF_12hoursnaps2"
dset="BF_12hoursnaps3"

## Change the format to be more like the other datasets
echo ${data_dir}/${dset}
python bin/live_tile_renamer.py --directory ${data_dir}/${dset}

mkdir ${data_dir}/${dset}/background 
#for f in ${data_dir}/${dset}/*_timepoint/*rest042/*.tiff; do
#for f in ${data_dir}/${dset}/*_timepoint/*rest042.tiff; do
for f in ${data_dir}/${dset}/*_timepoint/*rest042; do
    echo $f;
    rmdir $f;
    #rm $f;
    #mv $f ${data_dir}/${dset}/background/
done

python bin/background_iphox.py --output datasets/iphox_gradient_snaps/bg_values.json \
    --directories ${data_dir}/BF_12hoursnaps2/background  ${data_dir}/BF_12hoursnaps3/background



### Then make the biofilm masks
for f in ${data_dir}/${dset}/*hr_timepoint/delRU_*hr_Column*.tiff; do 
    echo $f
    python bin/mask_maker.py --classic63x --mask_name biofilmmask --remove_cr_from_mat_pat -l ${f}
done
#checked with this.
python bin/mask_maker.py --minidraw --mask_name biofilmmask --maxbright=0.1 --remove_cr_from_mat_pat -l ${data_dir}/${dset}/36hr_timepoint/delRU_36hr_Column2.tiff 
python bin/mask_maker.py --minidraw --mask_name edgemask --remove_cr_from_mat_pat -l ${data_dir}/${dset}/delRU/12hr_timepoint/delRU_12hr_Column1.tiff

# All were fine except the first 4 12 hour columns. Did those manually using
python bin/mask_maker.py --minidraw --mask_name biofilmmask --remove_cr_from_mat_pat -l ${data_dir}/${dset}/delRU/12hr_timepoint/delRU_12hr_Column10.tiff
# reran the edge estimator 
for f in ${data_dir}/${dset}/*hr_timepoint/delRU_12hr_Column*.tiff; do 
    python bin/mask_maker.py --edge_estimate --remove_cr_from_mat_pat -l ${f};
done


# next we need to make the distance from top map.
for f in ${data_dir}/${dset}/*hr_timepoint/delRU_*hr_Column*.tiff; do 
    echo $f
    python bin/distmap_maker.py --filled edgemask  --magnification "100-IPhox_1.5zoom" -f  ${f} 
done

### Now get the gradients of the images. 
widths='--sample_freq 0.25 --slice_width 0.5'
python bin/gradient_10x_maker.py \
    -f ${data_dir}/BF_12hoursnaps2/*hr_timepoint/delRU_*hr_Column*.tiff \
       ${data_dir}/BF_12hoursnaps3/*hr_timepoint/delRU_*hr_Column*.tiff \
    ${widths} \
    --bg_subtract  ${data_dir}/bg_values.json \
    --subtractions "bg_only"

## Make the file DB
outputdir="/Users/npm33/bf_pulse/datasets/iphox_gradient_snaps"
python one_offs/tenx_init_filedb.py -db ${outputdir}/filedb.tsv \
--basedir ${data_dir}/ \
--files ${data_dir}/${dset}/*hr_timepoint/delRU_*hr_Column*.tiff 

python bin/data_aggregator_10x.py \
    -db ${outputdir}/filedb.tsv \
    --basepathtoignore ${data_dir} \
    --data distmap \
    --outfile ${outputdir}/gradient_data \
    -f ${data_dir}/BF_12hoursnaps2/*hr_timepoint/delRU_*hr_Column*.tiff  
       ${data_dir}/BF_12hoursnaps3/*hr_timepoint/delRU_*hr_Column*.tiff  

