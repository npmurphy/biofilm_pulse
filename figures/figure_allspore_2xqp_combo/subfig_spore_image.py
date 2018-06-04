import os.path
# import sys

import matplotlib.pyplot as plt
import numpy as np
import skimage.io
import skimage.exposure
import skimage.transform
from lib.resolutions import PX_TO_UM_LSM700_GIANT as PX_TO_UM
import lib.figure_util as figure_util


def plot_big_image(ax, path, cache_path, slice_it, fl_range, vertical=True, scalebar=True):
    imname = os.path.splitext(os.path.basename(path))[0]
    imdir = os.path.dirname(path)
    impattern = os.path.join(imdir, imname, imname + "_{0}.tiff")
    slice_r, slice_c = slice_it
    cordstr = "_".join([ str(x) for x in [slice_r[0],slice_r[1], slice_c[0],slice_c[1]]]) + ".tiff"

    scale_down = 0.25

    imchans = []
    for ch in ["cr", "cg"]:
        cachename = os.path.join(cache_path, imname + "_{0}_".format(ch) + cordstr )
        if os.path.exists(cachename):
            print("using cached image ", cachename )
            im = skimage.io.imread(cachename)
        else:
            im = skimage.io.imread(impattern.format(ch))[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1]].copy()
            skimage.io.imsave(cachename, im)
        new_size = tuple(int(np.floor(i*scale_down)) for i in im.shape)
        im = skimage.exposure.rescale_intensity(im, in_range=(fl_range[ch + "_min"], fl_range[ch + "_max"]), out_range=(0,255)).astype(np.uint8)
        im = skimage.transform.resize(im, new_size, order=1)*255
        imchans += [im.astype(np.uint8)]
    
    #(target_height, target_width) = target_height_width
    imchans += [imchans[1]]
    bim = np.dstack(imchans)

    if vertical:
        bim = np.rot90(bim)
    if scalebar:
        SCALE_PX_TO_UM = PX_TO_UM/scale_down 
        bim = figure_util.draw_scale_bar(bim, 40, 40, 25/SCALE_PX_TO_UM, 20, "25μm", fontsize=80)

    ax.imshow(bim, interpolation="none")
    ax.grid(False)
    ax.axis('off')
    return ax


def big_images_main():
    #basedir = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/spores_63xbig/"
    this_dir = os.path.dirname(__file__)
    sp_image_basedir = os.path.join(this_dir, "../../proc_data/spores_63xbig/")
    files = [ {"Path": "Batch3/JLB077_48hrs_center_3_1.lsm", "x": 780 * 20, "y": 250 *20, 
            "cr_min":0, 
            "cr_max":10000, 
            "cg_min":2000,
            "cg_max":(2**14),
            },
            {"Path": "Batch1/JLB117_48hrs_center_4_1.lsm", "x" : 800*20, "y": 70*20,
            "cr_min":0, 
            "cr_max":30000, 
            "cg_min":2000,
            "cg_max":(2**15), }]
    height = 260 * 20 
    width = 500 * 20
    #   {"Path": "Batch3/JLB118_48hrs_center_7_1.lsm",
    #      "small_x" : 1832, "small_y": 227,
    #      "x" : 1832*20, "y": 227*20, 
    #     "cr_min":0, 
    #     #"cr_max":50000, 
    #     "cr_max":30000, 
    #     "cg_min":2000,
    #     "cg_max":(2**15)-1, 
    #      }]

    fig, ax = plt.subplots(1, len(files))
    # fl_range = {
    #             #"cr_min":2000, 
    #             "cr_min":0, 
    #             #"cr_max":50000, 
    #             "cr_max":50000, 
    #             "cg_min":2000,
    #             "cg_max":(2**16)-1, 
    #             }
    for r, i in enumerate(files):
        ax[r] = plot_big_image(ax[r],
                                    sp_image_basedir + i["Path"],
                                    this_dir,
                                    ((i["y"], i["y"] + height),
                                    (i["x"], i["x"] + width)), 
                                    #(height, width),
                                    i,vertical=False)
        # ax[r] = plot_big_image(ax[r], basedir + i["Path"], ((i["y"], i["y"] + height),
        #                                                     (i["x"], i["x"] + width)), 
        #                                                     (height, width),
        #                                                     i)
    plt.show()



if __name__ == "__main__":
    big_images_main()
    #small_images_main()