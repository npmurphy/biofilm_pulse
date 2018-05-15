# 00 is red, 01 is green
basedir="proc_data/iphox_movies/"
dataset="BF10_timelapse"
lookat="Column_2"

pattern=${lookat}"_t{0:03d}_ch00.tif" 
cpattern=${lookat}"_t{0:03d}_ch{1}.tif" 
    
python bin/make_cell_track_movie.py \
    --dataset ${basedir}/${dataset}/${lookat}/compiled.tsv \
    --trackdata ${basedir}/${dataset}/${lookat}/cell_track.json \
    --image_pattern ${basedir}/${dataset}/${lookat}/${cpattern} \
    --output_pattern "datasets/movie_1/frame_{0:03d}.png" \
    --cell 11 \
    --channels 00 01
    #11 28 10
     #--cokmpileddata ${basedir}/${dataset}/${lookat}/compiled.tsv \

ffmpeg -start_number 38 -i datasets/movie_1/frame_%03d.png datasets/movie1.mpg

ffmpeg -start_number 38 -i datasets/movie_1/frame_%03d.png -c:v libx264 -pix_fmt yuv420p datasets/movie1.mp4


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

ffmpeg -start_number 38 -i datasets/movie_20x/frame_%03d.png -c:v libx264 -pix_fmt yuv420p datasets/movie_20x.mp4
