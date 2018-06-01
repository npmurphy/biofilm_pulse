import os.path
import numpy as np
import skimage.io
import skimage.exposure

# from PIL import Image
# from PIL import ImageFont
# from PIL import ImageDraw 
import lib.figure_util

from lib.resolutions import PX_TO_UM_LSM780_10x as PX_TO_UM


biofilm_images = [  ("wt_sigar_sigby", "SigB_48hrs_center_1_1_100615_sect.tiff", ((800,1300), (300,1600))),
                    ("delru_sigar_sigby", "delRU_48hrs_3_6_100615sect.tiff", ((1080,1580),(500,1800))),
                    ("delqp_sigar_sigby", "delQP_48hrs_2_5_100615_sect.tiff",((900, 1400),(150,1450)))]

#("delqp_sigar_sigby", "delQP_48hrs_2_4_100615_sect.tiff",((720, 1220),(100,1400)))]
this_dir = os.path.dirname(__file__)

for i, (strain, imgpath, slice_it) in enumerate(biofilm_images): 
    im = skimage.io.imread(os.path.join(this_dir, "images", imgpath))
    imr = skimage.exposure.rescale_intensity(im[:,:,0], in_range=(1500, 18000), out_range=(0,255)).astype(np.uint8)
    img = skimage.exposure.rescale_intensity(im[:,:,1], in_range=(0, 6000), out_range=(0,255)).astype(np.uint8)
    im = np.dstack([imr, img, np.zeros_like(imr)])
    slice_r, slice_c = slice_it
    im = im[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1], :]
    #im = np.rot90(im)

    if strain == "wt_sigar_sigby":
        sbl = 100 # scale bar in um
        height, width, _ = im.shape
        #height - 50 
        im = lib.figure_util.draw_scale_bar(im, height-70, 20, sbl/PX_TO_UM, 14, "{0}μm".format(sbl)) 

    outpath = os.path.join(this_dir, "images", os.path.splitext(imgpath)[0] + ".jpg")
    print(outpath)
    skimage.io.imsave(outpath, im)

