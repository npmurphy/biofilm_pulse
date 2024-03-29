# 00 is red, 01 is green
basedir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/"
datadir="/media/nmurphy/BF_Data_Orange/datasets/iphox_singlecell/"
dataset="BF10_timelapse"
lookat="Column_2"

pattern=${lookat}"_t{0:03d}_ch00.tif" 
cpattern=${lookat}"_t{0:03d}_ch{1}.tif" 
    
python bin/make_cell_track_movie.py \
    --dataset ${datadir}/${dataset}/${lookat}/compiled_redo.tsv \
    --trackdata ${datadir}/${dataset}/${lookat}/cell_track.json \
    --image_pattern ${basedir}/${dataset}/${lookat}/${cpattern} \
    --output_pattern "datasets/movie_1/frame_{0:03d}.png" \
    --cell 11 \
    --channels 00 01
    #11 28 10
     #--cokmpileddata ${basedir}/${dataset}/${lookat}/compiled.tsv \


##ffmpeg -start_number 38 -i datasets/movie_1/frame_%03d.png datasets/movie1.mpg

#ffmpeg -start_number 38 -i datasets/movie_1/frame_%03d.png -c:v libx264 -pix_fmt yuv420p datasets/movie1.mp4
ffmpeg -start_number 38 \
       -i /media/nmurphy/BF_Data_Orange/datasets/movie_1/frame_%03d.png \
       -r 25 \
       -f mpeg -vcodec mpeg1video -b:v 5000k -y \
       /media/nmurphy/BF_Data_Orange/datasets/movie1_2.mpg

ffmpeg -start_number 38 \
       -i /media/nmurphy/BF_Data_Orange/datasets/movie_1_simp/frame_%03d.png \
       -r 25 \
       -f mpeg -vcodec mpeg1video -b:v 5000k -y \
       /media/nmurphy/BF_Data_Orange/datasets/movie1_simp.mpg

##############
## 20x Movie
#################
basedir="proc_data/iphox_zoom_out/"
dataset="BF13_20x_zoom_out_timelapse"
lookat="Series003"
pattern=${lookat}"_t{0:03d}_z0_ch{1}.tif" 
    
python bin/make_simple_movie.py \
    --image_pattern ${basedir}/${dataset}/${lookat}/${pattern} \
    --output_pattern "datasets/movie_20x/frame_{0:03d}.png" \
    --start_frame 0 \
    --end_frame 503 \
    --channels 00 01
    #11 28 10
     #--cokmpileddata ${basedir}/${dataset}/${lookat}/compiled.tsv \

ffmpeg -start_number 0 -i datasets/movie_20x/frame_%03d.png datasets/movie_20x.mpg

ffmpeg -start_number 0 -i datasets/movie_20x/frame_%03d.png -c:v libx264 -pix_fmt yuv420p datasets/movie_20x.mp4

# 288 is 6 hours
ffmpeg -start_number 0 \
       -i datasets/movie_20x/frame_%03d.png \
       -vframes 288 \
       -r 25 \
       -f mpeg -vcodec mpeg1video -b:v 5000k -y \
       datasets/movie20x_2.mpg


################
## 2xQP movie
############
#basedir="/media/nmurphy/BF_Data_Orange/raw_data/iphox_movies/Biofilm_movie_2xQP_test"
basedir="/media/nmurphy/BF_Data_Orange/raw_data/iphox_movies/WT_2xQP_movie_III/"
dataset="Mark_and_Find_001"
lookat="Position025"
pattern=${lookat}"_t{0:03d}_z0_ch{1}.tif" 
    
python bin/make_simple_movie.py \
    --image_pattern ${basedir}/${dataset}/${lookat}/${pattern} \
    --output_pattern "/media/nmurphy/BF_Data_Orange/datasets/movie_2xQP/frame_{0:03d}.png" \
    --start_frame 100 \
    --end_frame 257 \
    --channels 00 01

ffmpeg -start_number 100 \
       -i datasets/movie_2xQP/frame_%03d.png \
       -vframes 257 \
       -r 25 \
       -f mpeg -vcodec mpeg1video -b:v 6000k -y \
       datasets/movie_2xQP_new.mpg
    #    -f mpeg 
