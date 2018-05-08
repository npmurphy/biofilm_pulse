import skimage.io
import os.path
import numpy as np
from lib.resolutions import PX_TO_UM_LSM780_10x as PX_TO_UM
import lib.figure_util

this_dir = os.path.dirname(__file__)
tilescan = os.path.join(this_dir, "../../proc_data/frozen_sigW/SigW_72hrs_center_3.tif")
#"bf_pulse/proc_data/bf_live_tilescan/BF_movie15/end_20x_tilescan3
#channels = ["0", "1"]
# 0 is red , 1 is green
#images = ["1", "2", "3"]
#imname = "3"
#for imname in images:
scales = { 1 : (0, 20), # green
           0: (0, 100), # red
           2: (0, 0) }

image = skimage.io.imread(tilescan)

print(image.shape)
images = [ image[1,:,:], image[0,:,:], np.zeros_like(image[0, :,:])]
images = [ skimage.exposure.rescale_intensity(im, in_range=scales[i], out_range=(0,255))
                 for i, im in enumerate(images) ]
#images = [ im.astype(np.uint8) for im in images] 
#images += [ np.zeros_like(imges[-1])]
outim = np.dstack(images)
outim = np.rot90(outim,3)
length = 100 
outim = lib.figure_util.draw_scale_bar(outim, 20, 20 ,
                               scale_length=length/PX_TO_UM,
                               thickness=50,
                               legend = "{0}μm".format(length), fontsize=80)

skimage.io.imsave(os.path.join(this_dir, "sigW.png"), outim)
