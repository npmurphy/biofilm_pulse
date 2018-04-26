basedir="proc_data/iphox_movies/"
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

python bin/generate_tiling_json.py --output ${basedir}/${dataset}/all_columns.json --base_dir "Mark_and_Find" --start_frame 0 --end_frame 559 --description "${BF10_ALL_COLS}" 
python bin/generate_tiling_json.py --output ${basedir}/${dataset}short_columns.json --base_dir "Mark_and_Find" --start_frame 0 --end_frame 559 --description "${BF10_SHORT_COLS}" 

python bin/manual_movie_tiler.py --instructions ${basedir}/${dataset}/short_columns.json #--movie_name "Column_1"

lookat="Column_2"
# 00 is red, 01 is green
pattern=${lookat}"_t{0:03d}_ch00.tif" 
cpattern=${lookat}"_t{0:03d}_ch{1}.tif" 
#dpattern=${lookat}"_t*_ch01.tif" 
## New ellipse tracing on red mean
python bin/manual_tracker.py \
     --images    ${basedir}/${dataset}/${lookat}/${pattern} \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --compileddata ${basedir}/${dataset}/${lookat}/compiled.tsv \
     --view 3color \
     -c 12 \
     -s 190
     #--view gauss \


## Find common problems 
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --check_consistency 
     #--auto_correct_if_possible

## see cell properties at a frame
python bin/track_data_interact.py \
     --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
     --view_cell 2 \
     --at_frame 55

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
     --out_file ${basedir}/${dataset}/${lookat}/compiled.tsv \
     --start_frame 38 \
     --end_frame 280 \
     --channels 00 01



python bin/make_cell_track_movie.py \

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dataset", type=str)
    parser.add_argument('-t', "--trackdata", type=str)
    parser.add_argument('-i', "--image_pattern", type=str)
    parser.add_argument('-o', "--output_pattern", type=str)
    parser.add_argument('-c', "--cell", type=int)
    parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])