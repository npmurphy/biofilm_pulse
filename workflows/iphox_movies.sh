basedir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/"
#outdir="/media/nmurphy/BF_Data_Orange/datasets/iphox_singlecell/"
dataset="BF10_timelapse"

## All the columns. 
BF10_ALL_COLS=\
"1: 2 3 4 5
2: 6 7 8 9  
3: 10 11 12 13
4: 14 15 16 17
5: 18 19 20 21
6: 22 23 24 25
7: 26 27 28 29 
8: 30 31 32 33
9: 34 35 36 37"

# Actually the biofilm didnt grow in the top two 
BF10_SHORT_COLS=\
"1: 2 3
2: 6 7 
3: 10 11 
4: 14 15 
5: 18 19 
6: 22 23 
7: 26 27 
8: 30 31 
9: 34 35"


#python bin/generate_tiling_json.py --output ${basedir}/${dataset}/all_columns.json --base_dir "Mark_and_Find" --start_frame 0 --end_frame 559 --description "${BF10_ALL_COLS}" 
#python bin/generate_tiling_json.py --output ${basedir}/${dataset}short_columns.json --base_dir "Mark_and_Find" --start_frame 0 --end_frame 559 --description "${BF10_SHORT_COLS}" 

dataset="Biofilm_movie_04_02_2019"
EU_BF1=\
"1: 2 4 5 6
2: 7 8 9 10  
3: 11 12 13 14
4: 15 16 17 18
5: 19 20 21 22
6: 23 24 25 26"

basedir="/media/nmurphy/BF_Data_Orange/raw_data/iphox_movies/"
dataset="Biofilm_movie_2xQP_test"
EU_BF2xQP=\
"1: 2 3 4
2: 6 7 9
3: 11 12 13
4: 15 16 17
5: 19 20 21
6: 23 24 25 
7: 27 28 29
8: 31 32 33"


basedir="/media/nmurphy/BF_Data_Orange/raw_data/iphox_movies/"
dataset="Biofilm_WT_movie_new_media"
EU_BF_delsigf=\
"1: 2 3 4 5
2: 6 7 8 9  
3: 10 11 12 13
4: 14 15 16 17
5: 18 19 20 21
6: 22 23 24 25
7: 26 27 28 29 
8: 30 31 32 33
9: 34 35 36 37"


python bin/generate_tiling_json.py --output ${basedir}/${dataset}/all_columns.json --base_dir "Mark_and_Find 001" --start_frame 0 --end_frame 499 --description "${EU_BF_delsigf}" 
python bin/manual_movie_tiler.py --instructions ${basedir}/${dataset}/all_columns.json #--movie_name "Column_1"

#basedir="/media/nmurphy/BF_Data_Orange/datasets/iphox_singlecell/"
basedir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/"
dataset="BF10_timelapse"
#dataset="Biofilm_movie_04_02_2019/"
#lookat="Column_5"
lookat="Column_2"
# 00 is red, 01 is green
pattern=${lookat}"_t{0:03d}_ch00.tif" 
cpattern=${lookat}"_t{0:03d}_ch{1}.tif" 
#dpattern=${lookat}"_t*_ch01.tif" 
## New ellipse tracing on red mean
echo  ${basedir}/${dataset}/${lookat}/${pattern} 

python bin/manual_tracker_sql.py \
     --images    ${basedir}/${dataset}/${lookat}/${pattern} \
     --trackdata /home/nmurphy/Dropbox/work/projects/bf_pulse/bf10_track.sqllite \
     --compileddata ${basedir}/${dataset}/${lookat}/compiled.tsv \
     --view 3color \
     -c 54 \
     -s 69

python bin/unet_out_to_ellipse_use_past.py --frame 69
#python bin/unet_cell_track.py --frame 55

python bin/manual_track_verify.py \
     --images    ${basedir}/${dataset}/${lookat}/${pattern} \
     --trackdata /home/nmurphy/Dropbox/work/projects/bf_pulse/bf10_track.sqllite \
     --just_suspicious_cells \
     -s 69

# Current status 
# Ready to do frame 70  -> 71
# need an automatic division detector

python bin/track_data_interact.py --trackdata $(pwd)/bf10_track.sqllite \
     --divide --cell 1873 --at 69 --into 1873 2905
# undivide a cell 
#    remove divided status 
#    remove the parent status 


## Find common problems 
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --check_consistency 
     #--auto_correct_if_possible

## see cell properties at a frame
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --view_cell 20 \
     --at_frame 169

## Set State of a cell
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --set_cell_state "NE" \
     --from_frame 55 \
     --cell 2 

## Split part of cell history into a new cell
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --split_cell_at_frame \
     --cell "39" \
     --new_cell "40" \
     --upto_frame 58 
     #--from_frame 58 

## Figure out parents and children
python bin/lineage_setter.py \
     --image_pattern ${basedir}/${dataset}/${lookat}/${pattern} \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json 


python bin/compile_tracks.py \
     --image_pattern ${basedir}/${dataset}/${lookat}/${cpattern} \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --out_file ${basedir}/${dataset}/${lookat}/compiled_redo.tsv \
     --start_frame 38 \
     --end_frame 280 \
     --channels 00 01

python bin/compile_tracks.py \
     --image_pattern ${basedir}/${dataset}/${lookat}/${cpattern} \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --out_file ${basedir}/${dataset}/${lookat}/compiled.tsv \
     --start_frame 38 \
     --end_frame 280 \
     --channels 00 01

### Export images for neural_net training 
python bin/export_nn_training_set.py \
     --images    ${basedir}/${dataset}/${lookat}/${pattern} \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --outputfile ${basedir}/training_data_v1.mat 



# python bin/make_cell_track_movie.py \

#     parser = argparse.ArgumentParser()
#     parser.add_argument('-d', "--dataset", type=str)
#     parser.add_argument('-t', "--trackdata", type=str)
#     parser.add_argument('-i', "--image_pattern", type=str)
#     parser.add_argument('-o', "--output_pattern", type=str)
#     parser.add_argument('-c', "--cell", type=int)
#     parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])