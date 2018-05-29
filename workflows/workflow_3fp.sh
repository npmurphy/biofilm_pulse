
# For one image 
# Image J to split image. 
# split images into sub images 
basedir="data_local_cache/fp3_unmixing/" 
# There are more images in fpthree, they are compatible with these 


#basedir="/Users/niall.murphy/Microscope/teamJL_2/Niall/fpthree/"
#basedir="/home/nmurphy/SLCU/microscopy/teamJL_2/Niall/fpthree/"
#filename="JLB124_48hrs_edge_tile_scan_unmixing"
#filename="JLB124_48hrs_center_tile_scan_unmixing"

dirname="rsiga_ysigb_cspoiid"
#filename="JLB124_24hrs_center_63x_tile_unmixing"
filename="JLB124_48hrs_center_63x_tilescan_unmixing"
#filename="JLB124_72hrs_center_63x_tilescan_unmixing"
# filename="JLB124_24hrs_edge_63x_tile_unmixing"
#filename="JLB124_48hrs_edge_63x_tilescan_unmixing"
# filename="JLB124_72hrs_edge_63x_tilescan_unmixing"
dirname="rsiga_ysigb_csspb"
filename="JLB109_24hrs_center_63x_tile_unmixing"
filename="JLB109_48hrs_center_63x_tile_unmixing"
filename="JLB109_72hrs_center_63x_tile_unmixing"
# JLB109_24hrs_edge_63x_tile_unmixing
# JLB109_48hrs_edge_63x_tile_unmixing
# JLB109_72hrs_edge_63x_tile_unmixing

python giant63_init_filedb.py -db ${basedir}/${dirname}/filedb.tsv -f ${basedir}/${dirname}/*.lsm

python giant63_mask_maker.py --downscale --lsm_guess ${basedir}/${filename}.lsm 
for i in `ls ${basedir}/${dirname}/*.lsm`;
do  
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    python giant63_mask_maker.py --downscale --lsm_guess ${dirnameb}/${filename}.lsm 
done

python giant63_jet_findbasis.py --patch_radius 15 --output ${basedir}/jetbasis_r15.mat --file_list ${basedir}/basis_files.json 
python giant63_jet_precompute.py --basis ${basedir}/jetbasis_r15.mat --files ${basedir}/${dirname}/*/*_cr_reduced20.tiff --num_eigenvals 25

python giant63_svm_segmentation.py \
    --model_file ${basedir}/svm_linear_r15jetseg.pkl \
    --file_list ${basedir}/seg_files.json \
    --train \
    --patch_radius 15 \
    --focus_around_mask \
    --discard 0.9


## segment
python giant63_svm_segmentation.py --model_file ${basedir}/svm_linear_r15jetseg.pkl --segment ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff --extension segmented
python giant63_mask_maker.py --mask_name segmented --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff

python giant63_mask_maker.py --mask_estimate -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --mask_name biofilmmask --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff

python giant63_mask_maker.py --edge_estimate -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --mask_name edgemask --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff

python giant63_mask_maker.py --bottom_estimate -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --mask_name bottommask --minidraw -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20.tiff


python giant63_mask_maker.py --upscale -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20_edgemask.mat 
python giant63_mask_maker.py --upscale -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20_bottommask.mat 
python giant63_mask_maker.py --upscale -f ${basedir}/${dirname}/${filename}/${filename}_cr_reduced20_biofilmmask.mat 

python giant63_distmap.py --filled edgemask  --magnification 63-LSM780  -f  ${basedir}/${dirname}/${filename}.lsm 
python giant63_distmap.py --filled bottommask --magnification 63-LSM780  -f  ${basedir}/${dirname}/${filename}.lsm

# spoiid 
for i in `ls ${basedir}/${dirname}/*48hrs_center*.lsm`;
do  
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    python giant63_split_cellquant.py -c 5 -f ${basedir}/${dirname}/${filename}.lsm 
done
python giant63_split_cellquant.py -f ${basedir}/${dirname}/${filename}.lsm 
#python giant63_data_agregate.py -db ${basedir}/${dirname}/filedb.tsv --data cells -f ${basedir}/${dirname}/*_center_*.lsm
python giant63_data_agregate.py -db ${basedir}/${dirname}/filedb.tsv --data cells -f ${basedir}/${dirname}/JLB124_48hrs_center_*.lsm
python giant63_total_agregate.py -o ${basedir}/${dirname}_data.h5 --data cells -f ${basedir}/${dirname}/*.h5

# Aggregate the data.
#python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data spores -f ${basedir}/*.lsm
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data cells -f ${basedir}/${batch}/*.lsm
python giant63_total_agregate.py -o ${basedir}/${dirname}_data.h5 --data cells -f ${basedir}/${batch}/*.h5


##############
## Tightening up the biofilm mask 
basedir="../data/bio_film_data/data_local_cache/fp3_unmixing/" 
dirname="rsiga_ysigb_cspoiid"
#for i in `ls ${basedir}/${dirname}/*.lsm`; # We havnt done the other time steps
for i in `ls ${basedir}/${dirname}/*48hrs_center*.lsm`;
do  
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    echo "DOING" ${dirnameb}/${filename}.lsm 
    python giant63_split_cellquant.py -f ${basedir}/${dirname}/${filename}.lsm 
    #python giant63_data_agregate.py -db ${basedir}/${dirname}/filedb.tsv --data cells -f ${basedir}/${dirname}/*_center_*.lsm
done
    #python giant63_tighten_bfmask.py --make_backup --lsm_file ${dirnameb}/${filename}.lsm 
    #python giant63_tighten_bfmask.py --make_new_bfmask --lsm_file ${dirnameb}/${filename}.lsm 
    #python giant63_tighten_bfmask.py --use_old_edgemask --lsm_file ${dirnameb}/${filename}.lsm 
    #python giant63_distmap.py --filled edgemask  --magnification 63-LSM780  -f  ${basedir}/${dirname}/${filename}.lsm 
rm ${basedir}/${dirname}/*.h5

python giant63_data_agregate.py -db ${basedir}/${dirname}/filedb.tsv --data cells -f ${basedir}/${dirname}/JLB124_48hrs_center_*.lsm
python giant63_total_agregate.py -o ${basedir}/${dirname}_redoedgedata.h5 --data cells -f ${basedir}/${dirname}/*.h5



# manually corrected edgemask with imagej convert back to binary mask 
#name=JLB124_48hrs_center_tile_scan_unmixing
name=JLB124_48hrs_center_63x_tilescan_unmixing
python convert_tiff_to_mask.py --name image --image_file ${basedir}/${dirname}/${name}/${name}_edgemask.tiff
