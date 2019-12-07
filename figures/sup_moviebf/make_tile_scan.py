import skimage.io
import os.path
import numpy as np
from lib.resolutions import PX_TO_UM_IPHOX_20x_1p5zoom as PX_TO_UM
import lib.figure_util

this_dir = os.path.dirname(__file__)
tilescan = os.path.join(
    this_dir,
    "../../proc_data/bf_live_tilescan/BF_movie15/end_20x_tilescan{0}/TileScan_001_Merging_ch0{1}.tif",
)
# "bf_pulse/proc_data/bf_live_tilescan/BF_movie15/end_20x_tilescan3
channels = ["0", "1"]
# 0 is red , 1 is green
# images = ["1", "2", "3"]
imname = "3"
# for imname in images:
scales = {"1": (0, 42000), "0": (2498, 55849)}


images = [skimage.io.imread(tilescan.format(imname, channel)) for channel in channels]
images = [
    skimage.exposure.rescale_intensity(im, in_range=scales[i], out_range=(0, 255))
    for im, i in zip(images, channels)
]
images = [im.astype(np.uint8) for im in images]
images += [np.zeros_like(images[-1])]
outim = np.dstack(images)
outim = np.rot90(outim, 3)
length = 100
outim = outim[400 : (400 + 1215), 5008:].copy()
r, c, _ = outim.shape
outim = lib.figure_util.draw_scale_bar(
    outim,
    r - 200,
    c - 400,
    scale_length=length / PX_TO_UM,
    thickness=50,
    legend="{0}μm".format(length),
    fontsize=0,
)

skimage.io.imsave(os.path.join(this_dir, "tilescan_{0}_small.jpg".format(imname)), outim)
