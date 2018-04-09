# assumes prompt is in the root dir, that is "bf_pulse"

#############################
# Background subtraction 
#############################
bgdir="proc_data/slice10x_analysis/calibration"
img_dir="proc_data/slice10x_analysis/images/"
# output files
outputdir="datasets/LSM780_10x_sigb/" 
bgvalues="${outputdir}/bg_values_redux"


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
# Due to inconsitantancies edge and center numbering system, the code in filename_parser.py 
# does not assign the correct location to many images.
# Instead I manually looked at the images and assined "edge", "edgecenter" or "center" to them
python bin/manual_bf_location.py -o ${outputdir}/image_locations.json -d ${img_dir}/SigB/96hrs 
# this generated a file call manloc.json
# that maps the files to my manual location assignment. Some might be wrong its hard to tell at times. 
# Once that is done I make a filedb tsv file using this script. currently you need to manually set the directory and it myust be run 
# in the directroy with the images due to a glob being used to find the number location setting.
python ~/stochastic/data/bio_film_data/tenx_init_filedb.py -db ~/stochastic/data/bio_film_data/sigb_tenx_slice_analysis/tenx_filedb.tsv  -f *.tiff

###
## Segment the 10X image. 

# Generate the 

