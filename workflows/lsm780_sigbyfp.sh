# assumes prompt is in the root dir, that is "bf_pulse"

#############################
# Background subtraction 
#############################
bgdir="proc_data/slice10x_analysis/calibration"
img_dir="proc_data/slice10x_analysis/images/"
# output files
outputdir="datasets/LSM780_10x_sigb/" 
bgvalues="${outputdir}/bg_values"


# make and check the biofilm mask  
dirname="RXY"
filename="WT_48hrs_1_4_251114_sect"
python bin/mask_maker.py --maskestimate -l ${f};
python bin/mask_maker.py  --remove_cr_from_mat_path --mask_name biofilmmask --minidraw -f ${bgdir}/${dirname}/${filename}/${filename}_cr.tiff --maxbright=0.01

# make a quick background mask estimate (just use the top third and avoid regions labeled as bf)
filesBG=`ls -1 ${bgdir}/*XY/*48*.tiff`
python bin/background_mask_10x.py -f ${filesBG}

# comparable SigB, just use centers 
filesSB=`ls -1 proc_data/slice10x_analysis/images/SigB/48hrs/*center*.tiff`

# Actually generate the background values. 
python bin/background_values.py --output ${bgvalues} --files ${filesBG} ${filesSB}


##########################
## catagorise and images. 
##########################
dirname="2xQP"
dirname="delRU"
dirname="SigB/*"
dirname="delSigB"
dirname="delQP"
#dirname="SigB/96hrs"
################
## make sure all the images are all oriented correctly
###############
python bin/manual_correct_orientation.py -d ${img_dir}/${dirname}

# Due to inconsitantancies edge and center numbering system, the code in filename_parser.py 
# does not assign the correct location to many images.
# Instead I manually looked at the images and assined "edge", "edgecenter" or "center" to them
python bin/manual_bf_location.py -o ${outputdir}/image_locations.json -d ${img_dir}/${dirname}
 
# this generated a file that maps the files to my manual location assignment.
# Some might be wrong its hard to tell at times. 
# Once that is done I make a filedb tsv file using this script.
python one_offs/tenx_init_filedb.py -db ${outputdir}/tenx_filedb_redux.tsv \
--image_locations ${outputdir}/image_locations.json \
--basedir ${img_dir} \
--files ${img_dir}/*/*.tiff ${img_dir}/SigB/*/*.tiff


##################
## Segment the images
##################
dirname="2xQP"
dirname="delRU"
dirname="delQP"
#dirname="sigB/36hrs"
#dirname="*"
#dirname="sigB/*"
dirname="delSigB"
#dirname="sigB/24hrs"
#dirname="sigB/36hrs"
#dirname="sigB/48hrs"
#dirname="sigB/72hrs"
#dirname="sigB/96hrs"
#i="SigB_36hrs_1_1_230615_sect"
#filename="delRU_72hrs_center_2"
for i in `ls ${img_dir}/${dirname}/*.tiff`;
do
    lsmfile=$(basename "$i");
    filename="${lsmfile%.*}";
    dirnameb=$(dirname "$i");
    echo ${dirnameb} $filename
    # segments, 
    python bin/segment_10x.py --make_new_bfmask -f ${img_dir}/${dirname}/${filename}.tiff
    # marks the tops
    python bin/mask_maker.py --edge_estimate --use_expanded_mask -f ${img_dir}/${dirname}/${filename}/${filename}_cr.tiff
    # marks the pixels with distance from the top
    python bin/distmap_maker.py --filled edgemask  --magnification 10 -f  ${img_dir}/${dirname}/${filename}.tiff 
    # Compute the mean signal accross the biofilm for each image.
    # width and frequency are in micrometers
    #python bin/gradient_10x_maker.py -f ${img_dir}/${dirname}/${filename}.tiff ${widths} --bg_subtract  ${bgvalues}.json
done

#dirname="delRU"
#dirname="2xQP"
dirname="delQP"
#dirname="SigB/24hrs"
#dirname="SigB/36hrs"
#dirname="SigB/48hrs"
dirname="SigB/72hrs"
#dirname="SigB/96hrs"
#dirname="delSigB"
widths='--sample_freq 0.25 --slice_width 0.5'
python bin/gradient_10x_maker.py -f ${img_dir}/${dirname}/*.tiff ${widths} --bg_subtract  ${bgvalues}.json

python bin/data_aggregator_10x.py \
    -db ${outputdir}/filedb.tsv \
    --basepathtoignore ${img_dir} \
    --data distmap \
    --outfile ${outputdir}/gradient_data \
    -f ${img_dir}/SigB/*/*.tiff \
       ${img_dir}/delRU/*.tiff \
       ${img_dir}/delQP/*.tiff \
       ${img_dir}/2xQP/*.tiff \
       ${img_dir}/delSigB/*.tiff
    

