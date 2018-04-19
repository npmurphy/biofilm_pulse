
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
    #d="${data_dir}/${dset}/${d}"
    mkdir "${d}/MetaData/"
    for p in ${d}/*/; do
        echo "P" ${p}
        #mv ${p}/*.tif ${p}/../
        mv -f "${p}/MetaData/"* ${d}/MetaData/
        rmdir ${p}/MetaData
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



### 
#Process images.
#python bin/mask_maker.py --mask_name biofilmmask --remove_cr_from_mat_pat --minidraw -l ${bgdir}/${fpath} --maxbright ${bright}
python bin/mask_maker.py --mask_name biofilmmask --remove_cr_from_mat_pat -l ${bgdir}/${fpath} 
