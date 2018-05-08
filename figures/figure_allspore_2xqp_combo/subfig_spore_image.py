import os.path
import sys

import matplotlib.pyplot as plt
#import matplotlib.ticker as mticker
import numpy as np
import skimage.io
import skimage.exposure

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

#from data.bio_film_data.sixtythree_analysis import PX_TO_UM_LSM700_GIANT as PX_TO_UM
from lib.resolutions import PX_TO_UM_LSM700_GIANT as PX_TO_UM
import lib.figure_util as figure_util
#plt.style.use('../figstyle.mpl')


def plot_small_image(ax, path, slice_it, target_height_width):
    (target_height, target_width) = target_height_width
    im = skimage.io.imread(path)
    im = skimage.exposure.rescale_intensity(im, in_range=(0, (2**16)-1), out_range=(0,255)).astype(np.uint8)
    # skimage.exposure.rescale_intensity(im[:,:,0], in_range=(1500, 18000), out_range=(0,255))
    # skimage.exposure.rescale_intensity(im[:,:,0], in_range=(1500, 18000), out_range=(0,255)).astype(np.uint8)
    # img = skimage.exposure.rescale_intensity(im[:,:,1], in_range=(0, 6000), out_range=(0,255)).astype(np.uint8)
    #im = np.dstack([imr, img, np.zeros_like(imr)])
    slice_r, slice_c = slice_it
    im = im[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1], :]
    bim = np.zeros((target_height, target_width, 3), np.uint8)
    ac_h, ac_w, _ = im.shape
    rp = (target_height - ac_h)//2
    cp = (target_width - ac_w)//2
    print(im.shape[1], im.shape[0])
    print(rp, cp)
    bim[rp:rp + ac_h, cp:cp+ac_w, :] = im
    ax.imshow(bim, interpolation="bicubic")
    ax.grid(False)
    ax.axis('off')
    return ax


def plot_big_image(ax, path, slice_it, target_height_width, fl_range, vertical=True, scalebar=True):
    imname = os.path.splitext(os.path.basename(path))[0]
    imdir = os.path.dirname(path)
    impattern = os.path.join(imdir, imname, imname + "_{0}.tiff")
    slice_r, slice_c = slice_it
    cordstr = "_".join([ str(x) for x in [slice_r[0],slice_r[1], slice_c[0],slice_c[1]]]) + ".tiff"

    imchans = []
    for ch in ["cr", "cg"]:
        cachename = imname + "_{0}_".format(ch) + cordstr 
        if os.path.exists(cachename):
            print("using cached image ", cachename )
            im = skimage.io.imread(cachename)
        else:
            im = skimage.io.imread(impattern.format(ch))[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1]].copy()
            skimage.io.imsave(cachename, im)
        im = skimage.exposure.rescale_intensity(im, in_range=(fl_range[ch + "_min"], fl_range[ch + "_max"]), out_range=(0,255)).astype(np.uint8)
        imchans += [im]
    
    (target_height, target_width) = target_height_width
    imchans += [imchans[1]]
    bim = np.dstack(imchans)

    if vertical:
        bim = np.rot90(bim)
    if scalebar:
        bim = figure_util.draw_scale_bar(bim, 400, 400, 25/PX_TO_UM, 150, "25μm", fontsize=300)

    ax.imshow(bim, interpolation="none")
    ax.grid(False)
    ax.axis('off')
    return ax


def big_images_main():
    basedir = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/spores_63xbig/"
    files = [
      {"Path": "Batch3/JLB077_48hrs_center_3_1.lsm",
        "small_x": 780, "small_y": 250,
        "x": 780 * 20, "y": 250 *20,
        "cr_min":0, 
        #"cr_max":50000, 
        "cr_max":10000, 
        "cg_min":2000,
        "cg_max":(2**14)-1,
      },
      {"Path": "Batch1/JLB117_48hrs_center_4_1.lsm",
         "small_x" : 800, "small_y": 70,
         "x" : 800*20, "y": 70*20, 
        "cr_min":0, 
        #"cr_max":50000, 
        "cr_max":30000, 
        "cg_min":2000,
        "cg_max":(2**15)-1, 
         },
      {"Path": "Batch3/JLB118_48hrs_center_7_1.lsm",
         "small_x" : 1832, "small_y": 227,
         "x" : 1832*20, "y": 227*20, 
        "cr_min":0, 
        #"cr_max":50000, 
        "cr_max":30000, 
        "cg_min":2000,
        "cg_max":(2**15)-1, 
         }]

    fig, ax = plt.subplots(1, len(files))
    height = 260 * 20 
    width = 500 * 20
    # fl_range = {
    #             #"cr_min":2000, 
    #             "cr_min":0, 
    #             #"cr_max":50000, 
    #             "cr_max":50000, 
    #             "cg_min":2000,
    #             "cg_max":(2**16)-1, 
    #             }
    for r, i in enumerate(files):
        ax[r] = plot_big_image(ax[r], basedir + i["Path"], ((i["y"], i["y"] + height),
                                                            (i["x"], i["x"] + width)), 
                                                            (height, width),
                                                            i)
    plt.show()

def small_images_main():
    basedir = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/spores_63xbig/"
    files = [
    #   {"Path": "Batch4/JLB077_48hrs_center_2_2_reduced20.tiff",
    #     #"x": (656, 1086), "y" : (180, 371)
    #     "x": (660, 660+500), "y" : (150, 150 + 350)
    #   },
    #   { "Path": "Batch2/JLB077_48hrs_center_2_1_reduced20.tiff", 
    #     #"x": (539, 1171), "y": (60, 300)},
    #     "x": (580, 1170), "y": (50, 300)},
      {"Path": "Batch3/JLB077_48hrs_center_3_1_reduced20.tiff",
        #"x": (800 , 1300), "y": (232, 487)},
        "x": (780 , 0), "y": (250, 0)},
    #   {"Path": "Batch3/JLB117_48hrs_center_4_1_reduced20.tiff",
    #     "x": (355, 1252), "y": (100, 450)},
    #   {"Path": "Batch1/JLB117_48hrs_center_5_1_reduced20.tiff",
    #     "x" : (600, 1160), "y":(30, 390)},
      {"Path": "Batch1/JLB117_48hrs_center_4_1_reduced20.tiff",
         "x" : (800, 0), "y":( 70, 0)},
      {"Path": "Batch3/JLB118_48hrs_center_7_1_reduced20.tiff",
         "x" : (1832, 0), "y":( 227, 0)}]
    
    fig, ax = plt.subplots(len(files),1)
    height = 260
    width = 500
    for r, i in enumerate(files):
        ax[r] = plot_small_image(ax[r], basedir + i["Path"], ((i["y"][0], i["y"][0] + height),
                                                        (i["x"][0], i["x"][0] + width)), 
                                                        (height, width))
        #print(i["Path"], i["x"][1] - i["x"][0], i["y"][1] - i["y"][0] )
    plt.show()
    # ax = get_figure(ax)


if __name__ == "__main__":
    big_images_main()
    #small_images_main()