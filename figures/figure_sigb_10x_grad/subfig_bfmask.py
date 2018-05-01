import os.path

import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import skimage.io
import skimage.morphology
#from lib.resolutions import PX_TO_UM_LSM780_10x as PX_TO_UM
this_dir = os.path.dirname(__file__)
plt.style.use(os.path.join(this_dir, '../../figures/figstyle.mpl'))

def get_figure(ax, img_path, original_path): 
    imgpath, slice_it = ("SigB_48hrs_center_1_1_100615_sect.tiff", ((800, 1300), (300, 1600)))
    bname = os.path.splitext(imgpath)[0]
    data_path = os.path.join(original_path, "slice10x_analysis", "images",  "SigB", "48hrs", bname, imgpath.replace(".tiff", "_biofilmmask.mat"))
    mask = scipy.io.loadmat(data_path)["image"]
    smask = skimage.morphology.binary_erosion(mask, selem=skimage.morphology.disk(2))
    outline = mask & ~(smask)

    im = skimage.io.imread(os.path.join(img_path, imgpath))
    imr = skimage.exposure.rescale_intensity(im[:,:,0], in_range=(1500, 18000), out_range=(0,255)).astype(np.uint8)
    img = skimage.exposure.rescale_intensity(im[:,:,1], in_range=(0, 6000), out_range=(0,255)).astype(np.uint8)
    im = np.dstack([imr, img, np.zeros_like(imr)])
    im[np.where(outline)] = [255, 255, 255]
    slice_r, slice_c = slice_it
    im = im[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1], :]
    #im = np.rot90(im)
    #im = figure_util.draw_scale_bar(im, 50, 50, 25/PX_TO_UM, 20, "25μm", fontsize = 40)

    ax.imshow(im, interpolation="none")
    ax.grid(False)
    ax.axis('off')
    # ax.set_xlim(left=0, right=) 
    # ax.set_ylim(bottom=0)
    return ax


def main():
    fig_main, ax = plt.subplots(1,1, sharex=True)
    ax = get_figure(ax, os.path.join(this_dir, "images"), os.path.join(this_dir, "../../proc_data/"))
    plt.show()


if __name__ == "__main__":
    main()
