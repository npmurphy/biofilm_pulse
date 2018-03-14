
# new data. 
data_dir="/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks"

dset="BF_12hoursnaps1"

pttwo="Final_transmited_light
beads_end_g100_r100
beads_end_g40_r50
84hr_timepoint
96hr_timepoint
"
# Turn from leica format to something easier to deal with
find ${data_dir}/${dset} -name .DS_Store -exec rm {} +
#for d in ${pttwo}; do
#for d in ${data_dir}/${dset}/*/; do
    echo "D" $d;
    d="${data_dir}/${dset}/${d}"
    mkdir "${d}/MetaData/"
    for p in ${d}/*/; do
        echo "P" ${p}
        mv ${p}/*.tif ${p}/../
        mv -f ${p}/MetaData/* ${d}/MetaData/
        rmdir ${p}/MetaData
        rmdir ${p}
    done
done

dset="BF_12hoursnaps1"
## There are a few substitutions.
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
01"
timepoint="12hr_timepoint" 
timepoint="24hr_timepoint" 
timepoint="36hr_timepoint" 

declare -a columns=("1" "2" "3" "4" "5" "6" "7" "8" "9" "10")

# outf="1"
# declare -a col=("41" "04" "03" "02" "01")

# outf="2"
# declare -a col=("08" "07" "06" "05")

# outf="3"
# declare -a col=("12" "11" "10" "09")

# outf="4"
# declare -a col=("16" "15" "14" "13")

# outf="5"
# declare -a col=("20" "19" "18" "17")

# outf="6"
# declare -a col=("24" "23" "22" "21")

# outf="7"
# declare -a col=("42" "28" "27" "26" "25")


# outf="8"
# declare -a col=("32" "31" "30" "29")

# outf="9"
# declare -a col=("43" "36" "35" "34" "33")
# #24h 43

# outf="10"
# declare -a col=("45" "40" "39" "38" "37")
#36h 45
# for pi in "${col[@]}"; do 
#     flist="${flist} ${data_dir}/${dset}/${timepoint}/Position0${pi}_ch${ch}.tif";
# done

for col in "${columns[@]}"; do   
    for ch in $chans; do
        # echo $col
        # echo $ch
        flist=`python ${data_dir}/${dset}/generate_columns.py --prematter ${data_dir}/${dset}/${timepoint}/ --channel ${ch} --column ${col}`
        #python ${data_dir}/${dset}/generate_columns.py --prematter ${data_dir}/${dset}/${timepoint}/ --channel ${ch} --column ${col}
        #echo python ${data_dir}/${dset}/generate_columns.py --channel ${ch} --column ${col}
        #echo $flist
        python bin/stitcher_simple.py --files ${flist} \
             --output ${data_dir}/${dset}/${timepoint}/Column_${col}_ch${ch}.tif;
    done
done

mkdir ${data_dir}/${dset}/${timepoint}/unstitched
mv ${data_dir}/${dset}/${timepoint}/Position*.tif ${data_dir}/${dset}/${timepoint}/unstitched/

for i in 
