
import skimage.io
import skimage.exposure
import skimage.morphology
import scipy.io
import numpy as np

from lib.resolutions import PX_TO_UM_LSM700_63x as PX_TO_UM
from lib.figure_util import draw_scale_bar

def process_fp(im, ROI, min_fp, max_fp):
    lim = im.copy()
    lim[im<min_fp] = 0
    print(min_fp, max_fp)
    rescale = skimage.exposure.rescale_intensity(lim, in_range=(min_fp, max_fp), out_range=(0, 255)).astype(np.uint8)
    cuted = rescale[ROI]
    return cuted


def out_line_inclusion_zone_and_edge(img_path, slice_start, slice_stop, roi):
    distmap = scipy.io.loadmat(img_path.replace(".tiff", "_distmap.mat"))["distmap_masked"].astype(np.float32)
    msk = (distmap > slice_start) & (distmap < slice_stop)
    erode = skimage.morphology.binary_erosion(msk, selem=skimage.morphology.disk(3))
    mask = msk & (~erode)
    bfmask = distmap > 0
    bf_erode = skimage.morphology.binary_erosion(bfmask, selem=skimage.morphology.disk(3))
    bf_edge = bfmask & (~bf_erode)
    return (mask[roi[0][0]: roi[0][1], roi[1][0]: roi[1][1]], 
           bf_edge[roi[0][0]: roi[0][1], roi[1][0]: roi[1][1]])

def get_figure(ax, name, impath, roi, chans, FP_max_min, slicel, add_scale_bar=False):
    slice_srt, slice_end = slicel
    im = skimage.io.imread(impath)
    images = [0, 0, 0]
    outline, edge = out_line_inclusion_zone_and_edge(impath, slice_srt, slice_end, roi)
    for c in range(3):
        if c in chans:
            rois = (slice(roi[0][0], roi[0][1]), slice(roi[1][0], roi[1][1]))
            images[c] = process_fp(im[:, :, c], rois, FP_max_min[c][0], FP_max_min[c][1])
            print("S", images[c].shape)
        else:
            rois = (roi[0][1] - roi[0][0], roi[1][1] - roi[1][0])
            images[c] = np.zeros(rois, dtype=np.uint8)
    
    img = np.dstack(images)
    # img[outline == True, :] = [ 255, 255, 255]
    # img[edge == True, :] = [ 255, 255, 0]
    img[outline, :] = [ 255, 255, 255]
    img[edge, :] = [ 255, 255, 0]
    img = np.rot90(img, 3)
    if add_scale_bar:
        img = draw_scale_bar(img, 400, 350, (5/PX_TO_UM), 20, "5μm")
    ax.imshow(img, interpolation="none", aspect=1)
    ax.set_title(name)
    ax.grid(False)
    ax.axis('off')

    return ax
