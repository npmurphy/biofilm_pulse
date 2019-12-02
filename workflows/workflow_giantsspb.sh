
# downscale 
#for i in `ls data/jul63xbig/*/*/*_cr_reduced20_edgemask.mat`;
#for i in `ls data/jul63xbig/Batch3/*/*_cr_reduced20_biofilmmask.mat`;
#for i in `ls data/jul63xbig/Batch*/*/*_cr_reduced20.tiff`;

# images were converted from lsm to single channel tiff files _cr (red) and _cg (green) using ImageJ. 

for i in `ls data/jul63xbig/Batch*/*.lsm`;
do  
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirname=$(dirname "$i");

    # Split the giant images into manageable strips 
    python giant63_split.py -f ${dirname}/${filename}/${filename}_cr.tiff;
    python giant63_split.py -f ${dirname}/${filename}/${filename}_cg.tiff''
    # make map to know how the bits go together. 
    python giant63_file_info_json_dump.py -f $i 
    
    python giant63_mask_maker.py --downscale --file ${dirname}/${filename}/${filename}_cg.tiff 
    python giant63_mask_maker.py --downscale --file ${dirname}/${filename}/${filename}_cr.tiff 
    #python giant63_mask_maker.py --downscale --lsm_guess $i;

    #python giant63_svm_segmentation.py --model_file ${basedir}/svm_linear_jetseg.pkl --segment ${dirname}/${lsmfile} --extension check --patch_radius 10
    # This SVM used eigen vectors computed for each patch in the image. 
    # In the end the training set needed to be almost half the dataset and there was still lots of manual correction needed. 
    # The results were compared against the standard 10x segmentation and did not really add any benifit.
    python mask_maker.py --maskestimate -l ${dirname}/${filename}/${filename}_cr_reduced20.tiff
    #do python giant63_mask_maker.py --kmeans_model ${basedir}/kmeans_reduced_segmenter.pkl --segment -f $i;
    # manually correct the mask
    python mask_maker.py  --remove_cr_from_mat_path --mask_name biofilmmask --minidraw -f ${dirname}/${filename}/${filename}_cr_reduced20.tiffI

    # blow it back up to full size 
    python giant63_mask_maker.py --upscale -f ${dirname}/${filename}/${filename}_cr_reduced20_biofilmmask.mat 

    # Get the distance for each sli
    python distmap_maker.py -f $i 
    
    python giant63_split_spore.py -f $i
    python giant63_split_cellquant.py -f $i
done

python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data spores -f ${basedir}/${batch}/${filename}.lsm 
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data cells -f ${basedir}/${batch}/${filename}.lsm 
python giant63_total_agregate.py -o ${basedir}/autocor_data.h5 --data spores -f ${basedir}/Batch*/*.h5 
python giant63_total_agregate.py -o ${basedir}/autocor_data.h5 --data cells -f ${basedir}/Batch*/*.h5





batch="Batch1"
filename="JLB077_48hrs_center_2_1" 
#python giant63_split_spore.py -f ${basedir}/${batch}/${filename}.lsm 
python giant63_split_cellquant.py -f ${basedir}/${batch}/${filename}.lsm 

cd data/bio_film_data
basedir="data/jul63xbig/"
batch="Batch3"
filename="JLB077_48hrs_center_1_2"
filename="JLB077_48hrs_center_2_1"
filename="JLB118_48hrs_center_8_1"
python giant63_tighten_bfmask.py --lsm_file ${basedir}/${batch}/${filename}.lsm --use_old_edgemask
batch="Batch4"
i="data/jul63xbig//Batch4/JLB077_48hrs_center_1_2.lsm"
i="data/jul63xbig//Batch4/JLB118_48hrs_center_7_1.lsm"

python giant63_distmap.py -f ${i}
--make_new_bfmask
for i in `ls ${basedir}/Batch*/*.lsm`;
do  
    python giant63_split_cellquant.py -f ${i}
    #python giant63_split_spore.py -f ${i} # basedir}/${batch}/${filename}.lsm 
    #echo ${i};
    #python giant63_distmap.py -f $i 
    #python giant63_tighten_bfmask.py --lsm_file ${i} --use_old_edgemask
    #python giant63_tighten_bfmask.py --make_backup --lsm_file ${i};
done

python giant63_split_cellquant.py -f ${i}
python giant63_split_cellquant.py -f ${basedir}/${batch}/${filename}.lsm 
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data spores -f ${basedir}/Batch*/*.lsm
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data cells -f ${basedir}/Batch*/*.lsm

for i in `ls ${basedir}/Batch*/*.h5`;
do  
    mv $i $i.maxsporeseg
done


# For one image 
# Image J to split image. 
# split images into sub images 
#basedir="data/jul63xbig/"
basedir="data/jul63xbig/"
batch="Batch4"
#filename="JLB077_48hrs_center_1_1" #
#filename="JLB077_48hrs_center_1_2" #
#filename="JLB077_48hrs_center_2_1" #
filename="JLB077_48hrs_center_2_2" #
#filename="JLB117_48hrs_center_3_1" # done
#filename="JLB117_48hrs_center_4_1" #
#filename="JLB117_48hrs_center_5_2" #
#filename="JLB117_48hrs_center_5_3" #
#filename="JLB117_48hrs_center_5_4" #
#filename="JLB118_48hrs_center_6_1" #
#filename="JLB118_48hrs_center_7_1" #
#filename="JLB118_48hrs_center_7_2" #

python giant63_split.py -f ${basedir}/${batch}/${filename}/${filename}_cr.tiff
python giant63_split.py -f ${basedir}/${batch}/${filename}/${filename}_cg.tiff
python giant63_file_info_json_dump.py -f ${basedir}/${batch}/${filename}.lsm 
python giant63_mask_maker.py --downscale --lsm_guess ${basedir}/${batch}/${filename}.lsm 
#python giant63_mask_maker.py --kmeans_model ${basedir}/kmeans_reduced_segmenter.pkl --segment -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
#python giant63_mask_maker.py --kmeans_model ${basedir}/kmeans_jetseg.pkl --segment -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
#python giant63_svm_segmentation.py --model_file ${basedir}/svm_linear_jetseg.pkl --evaluate $i; 

python giant63_svm_segmentation.py --model_file ${basedir}/svm_linear_jetseg.pkl --segment ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff --extension segmented
#python giant63_mask_maker.py --lsm_guess --kmeans_model ${basedir}/kmeans_reduced_segmenter.pkl --mask_estimate ${basedir}/${batch}/{$filename}.lsm
python giant63_mask_maker.py  --mask_name segmented --minidraw -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --mask_estimate -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py  --mask_name biofilmmask --minidraw -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --edge_estimate -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py  --mask_name edgemask --minidraw -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20.tiff
python giant63_mask_maker.py --upscale -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20_edgemask.mat 
python giant63_mask_maker.py --upscale -f ${basedir}/${batch}/${filename}/${filename}_cr_reduced20_biofilmmask.mat 
python giant63_distmap.py -f ${basedir}/${batch}/${filename}.lsm 
#python giant63_count_distances.py -f ${basedir}/${batch}/${filename}.lsm 
python giant63_split_spore.py -f ${basedir}/${batch}/${filename}.lsm 
#python giant63_split_cell.py -f ${basedir}/${batch}/${filename}.lsm 
python giant63_split_cellquant.py -f ${basedir}/${batch}/${filename}.lsm 

# Aggregate the data.

#python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data spores -f ${basedir}/Batch*/*.lsm
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data spores -f ${basedir}/${batch}/${filename}.lsm 
python giant63_data_agregate.py -db ${basedir}/file_list.tsv --data cells -f ${basedir}/${batch}/${filename}.lsm 
python giant63_total_agregate.py -o ${basedir}/autocor_data.h5 --data spores -f ${basedir}/Batch*/*.h5 
python giant63_total_agregate.py -o ${basedir}/autocor_data.h5 --data cells -f ${basedir}/Batch*/*.h5


#batch="Batch1"
#filename="JLB077_48hrs_center_1_1"
#filename="JLB077_48hrs_center_2_1"
#filename="JLB117_48hrs_center_3_1"
#filename="JLB117_48hrs_center_4_1"
#filename="JLB117_48hrs_center_5_1"
#filename="JLB118_48hrs_center_6_1"
#filename="JLB118_48hrs_center_7_1"

#batch="Batch3"
#filename="JLB118_48hrs_center_8_1"
#filename="JLB118_48hrs_center_7_1"
#filename="JLB118_48hrs_center_6_1"
#filename="JLB117_48hrs_center_5_2"
#filename="JLB117_48hrs_center_4_1"
#filename="JLB077_48hrs_center_3_1"
#filename="JLB077_48hrs_center_2_1"
#filename="JLB077_48hrs_center_1_2"

#batch="Batch2"
#filename="JLB077_48hrs_center_1_1" # 
#filename="JLB077_48hrs_center_2_1" #
#filename="JLB077_48hrs_center_3_1" #
#filename="JLB117_48hrs_center_4_1" # 
#filename="JLB117_48hrs_center_5_1" #
#filename="JLB118_48hrs_center_6_1" #
#filename="JLB118_48hrs_center_7_1"  
#filename="JLB118_48hrs_center_8_2"
