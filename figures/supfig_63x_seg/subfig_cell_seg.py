import os.path

import matplotlib.pyplot as plt
import numpy as np
#import scipy.io
import skimage.io
import skimage.morphology
#import figure_util
#import filedb
from lib.cmaps import cmrand
#import filedb
from lib.cell_segmenter import laphat_segment_v1

this_dir = os.path.dirname(__file__)
plt.style.use(os.path.join(this_dir, '../../figures/figstyle.mpl'))

# put in figure utils? 
def process_fp(im, ROI, min_fp, max_fp):
    lim = im.copy()
    lim[im<min_fp] = 0
    print(min_fp, max_fp)
    rescale = skimage.exposure.rescale_intensity(lim, in_range=(min_fp, max_fp), out_range=(0, 255)).astype(np.uint8)
    cuted = rescale[ROI]
    return cuted

def get_figure(ax, cache_path):
    image_base_dir = "."
    this_dir = os.path.dirname(__file__)
    path = os.path.join(this_dir, "SigB_48hrs_center_4_100615_sect_stitched.tiff")
    roi = (726, 726 + 500), (142,142+500) # row, cols 
    FP_max_min = (0,    30000)

    impath = os.path.join(image_base_dir, path)
    im = skimage.io.imread(impath)
    #    outline = out_line_inclusion_zone(impath, slice_srt, slice_end, roi)
    rois = (slice(roi[0][0], roi[0][1]), slice(roi[1][0], roi[1][1]))
    sim = process_fp(im[:, :, 0], rois, FP_max_min[0], FP_max_min[1])
    #img = np.dstack([sim, np.zeros_like(sim), np.zeros_like(sim)])
    img = np.dstack([sim, sim, sim])

    cell_width_pixels=10
    seg = laphat_segment_v1(im[:,:,0], cell_width_pixels=cell_width_pixels, small_cells=cell_width_pixels < 6)
    print(seg.shape)
    print(seg.dtype)
    #print()
    
    mask = seg > 0
    print(np.count_nonzero(mask), np.prod(mask.shape))
    smask = skimage.morphology.binary_erosion(mask, selem=skimage.morphology.disk(3))
    print(smask.shape)
    print(smask.dtype)
    outline = mask & ~(smask)
    print(np.count_nonzero(outline), np.prod(outline.shape))
    outint = outline.astype(np.int32) 
    oseg = seg * outint
    print(np.count_nonzero(oseg), np.prod(oseg.shape))
    print(oseg.shape)
    print(oseg.dtype)
    smallseg = oseg[rois]


    ax.imshow(img, interpolation="none", aspect=1)
    #ax.imshow(np.ma.masked_equal(smallseg, 0), interpolation="bicubic", aspect=1, cmap=cmrand)
    ax.imshow(np.ma.masked_equal(smallseg, 0), aspect=1, cmap=cmrand)

    #ax.imshow(im, interpolation="bicubic")
    ax.grid(False)
    ax.axis('off')

    # ax.set_xlim(left=0, right=) 
    # ax.set_ylim(bottom=0)
    return ax


def main():
    fig_main, ax = plt.subplots(1,1, sharex=True)
    ax = get_figure(ax, "../../data/bio_film_data/data_local_cache/")
    # ax.set_xlim(38, 488)
    # ax.set_ylim(277, 439)
    plt.show()


if __name__ == "__main__":
    main()
