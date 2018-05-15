
# for 10x gradient figure
python analysis/summarise_10x_gradients.py

# for comparing spores 
python analysis/summarise_63x_gradients.py 


### Spore density gradients
python analysis/kd_density_cacher.py \
--spore_db datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
--cell_db  datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
--file_db  datasets/LSM700_63x_sspb_giant/file_list.tsv \
--out_dir  datasets/LSM700_63x_sspb_giant/kd_spore_cell_2 \
--mask_base data/bio_film_data/data_local_cache/spores_63xbig 

    #--quarter 0 # 1, 2, 3,

# Make the cell and spore count db
#/Users/npm33/bf_pulse/analysis/.py

### First run with flag
#    --data_files_to_recompute_area_cache  proc_data/spores_63xbig
#  to cache the numbers of pixels in each bin. 
#  then run again with just the 
#    --area_cache  datasets/LSM700_63x_sspb_giant/distance_bin_areas.mat \
#  flag to compute the scaled spore and cell counts. 
python analysis/summarize_cell_spore_counts.py \
    --file_db  datasets/LSM700_63x_sspb_giant/file_list.tsv \
    --spore_db datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
    --cell_db  datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
    --out_file  datasets/LSM700_63x_sspb_giant/spore_cell_counts.mat \
    --area_cache  datasets/LSM700_63x_sspb_giant/distance_bin_areas.mat \
    --data_files_to_recompute_area_cache  proc_data/spores_63xbig

python analysis/summarize_cell_spore_counts.py \
    --file_db  datasets/LSM700_63x_sspb_giant/file_list.tsv \
    --spore_db datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
    --cell_db  datasets/LSM700_63x_sspb_giant/autocor_sporerem_data.h5 \
    --out_file  datasets/LSM700_63x_sspb_giant/spore_cell_counts.mat \
    --area_cache  datasets/LSM700_63x_sspb_giant/distance_bin_areas.mat 

