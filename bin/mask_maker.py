import os.path
import matplotlib
matplotlib.use('TKAgg')

import numpy as np
import skimage.draw
import skimage.transform
import skimage.measure
import skimage.morphology
import argparse
import scipy.io
import scipy.ndimage.morphology
import scipy.ndimage.measurements
import re
from lib import file_finder
from lib import tiff
import skimage.io
import glob
#import .giant63_kmeans_segmentation
# import json
# import data.bio_film_data.slice10x.distance_top_mask_flat
#from data.bio_film_data.sixtythree_stitched_masking import get_biofilm_mask
import lib.processing.slice63x as slice63x
from lib.processing.segment.segedit import Editor
import matplotlib.pyplot as plt
from lib.processing import slice10x


def downscale(imgpath, reductions=None):
    print("Downscaling {0}".format(imgpath))
    im = skimage.io.imread(imgpath)
    typ = np.iinfo(im.dtype)
    orig_size = im.shape
    print("Original size", orig_size)
    if reductions is None:
        target_size = 2048
        reductions = int(np.ceil(max(orig_size) / target_size ))
    print("Reducing by {0}".format(reductions))
    imf = im.astype(np.float) / typ.max
    small = skimage.transform.pyramid_reduce(imf, downscale=reductions)
    print("New size {0}", small.shape)
    #print("expected size {0}, {1}", orig_size[0]/reductions, orig_size[1]/reductions)
    small = (small * typ.max).astype(im.dtype)*2
    skimage.io.imsave(file_finder.get_labeled_path(imgpath, "reduced{0}".format(reductions)), small)


def upscale(imgpath):
    ext = os.path.splitext(imgpath)[1]
    if ext == ".tiff":
        im = skimage.io.imread(imgpath)
    elif ext == ".mat":
        im = scipy.io.loadmat(imgpath)["image"].astype(np.bool)

    reduced = int(re.match(r".*_reduced(\d+)[_\.].*", imgpath).group(1))
    reducedstr = re.match(r".*(reduced\d+)[_\.].*", imgpath).group(1)
    origpath = imgpath.replace("_"+reducedstr, "").replace("_edgemask", "").replace("_biofilmmask", "").replace("_bottommask", "")
    origpath = os.path.splitext(origpath)[0] + ".tiff"

    orig_size = tiff.get_shape(origpath)
    bigim = skimage.transform.pyramid_expand(im, upscale=reduced)
    if im.dtype != np.bool:
        bigim = bigim * np.iinfo(im.dtype).max
    bigim = bigim.astype(im.dtype)
    new_size = bigim.shape
    print("old", orig_size)
    print("new", new_size)
    row_shift = int(np.round((orig_size[0] - new_size[0])/2))
    col_shift = int(np.round((orig_size[1] - new_size[1])/2))
    new_img = np.zeros(orig_size, dtype=im.dtype)
    # TODO this might cause problems. when the new image is bigger, it works great.
    # Need to check other cases though
    if row_shift < 0 or col_shift < 0:
        new_img[:, :] = bigim[0:orig_size[0], 0:orig_size[1]]
    else:
        new_img[0:new_size[0], 0:new_size[1]] = bigim[:,:] #[0:new_img.shape[0], 0:new_img.shape[1]]
    new_img = skimage.morphology.binary_opening(new_img, selem=skimage.morphology.disk(reduced//2, dtype=bool))
    # skimage transform pyramid expandskimage transform pyramid expandif row_shift < 0:
    #     new_img[:, :] = bigim[(-row_shift):row_shift+new_size[0], col_shift:col_shift +new_size[1]] = bigim[:,:]

    #     print("cutting down")
    # else:
    #     print("padding out down")
    #     new_img[row_shift:row_shift+new_size[0], col_shift:col_shift +new_size[1]] = bigim[:,:]
    if ext == ".tiff":
        newpath = imgpath.replace(reducedstr, "embigened")
        skimage.io.imsave(newpath, new_img)

    elif ext == ".mat":
        newpath = os.path.splitext(imgpath.replace("_"+reducedstr, ""))[0]
        newpath = newpath.replace("_cr_", "_")
        newpathmat = newpath + ".mat"
        newpathtif = newpath + ".tiff"
        scipy.io.savemat(newpathmat, {"image":new_img})
        skimage.io.imsave(newpathtif, new_img.astype(np.uint8)*255)

def heuristic_biofilm_seg_unscaled_lsm700_63x(imgpath):
    matpath = os.path.splitext(imgpath.replace("_cr", ""))[0] + ".mat"
    segtpath = file_finder.get_labeled_path(matpath, "segmented")
    maskpath = file_finder.get_labeled_path(matpath, "biofilmmask")
    image = skimage.io.imread(imgpath)
    mask = slice63x.get_biofilm_mask(image)
    #scipy.io.savemat(distpath, {"image":distmask})
    scipy.io.savemat(segtpath, {"image":mask})
    scipy.io.savemat(maskpath, {"image":mask})
    botmask = slice63x.fill_biofilm_mask(mask, "bottom")
    edgepath = file_finder.get_labeled_path(matpath, "edgemask")
    scipy.io.savemat(edgepath, {"image":botmask})




def heuristic_biofilmmask(imgpath):
    matpath = os.path.splitext(imgpath)[0] + ".mat"
    segtpath = file_finder.get_labeled_path(matpath, "segmented")
    maskpath = file_finder.get_labeled_path(matpath, "biofilmmask")
    try:
        mask = scipy.io.loadmat(segtpath)["image"].astype(np.bool)
    except OSError as e:
        print("you probably need to generate a segmentation file first")
        raise e
    skimage.morphology.remove_small_objects(mask, min_size=64, connectivity=1, in_place=True)
    scipy.io.savemat(maskpath, {"image":mask})

def heuristic_distmask(imgpath):
    imgpath = imgpath.replace("_cr.tiff", ".tiff")
    matpath = os.path.splitext(imgpath)[0] + ".mat"
    maskpath = file_finder.get_labeled_path(matpath, "biofilmmask")
    distpath = file_finder.get_labeled_path(matpath, "edgemask")
    try:
        mask = scipy.io.loadmat(maskpath)["image"]
    except OSError as e:
        print("you probably need to generate a mask file first")
        raise e
    distmask = slice10x.distance_top_mask_flat.get_top_mask(mask)
    scipy.io.savemat(distpath, {"image":distmask})
    skimage.io.imsave(distpath.replace(".mat", ".tiff"),  distmask.astype(np.uint8)*255)

def heuristic_bottommask(imgpath):
    matpath = os.path.splitext(imgpath)[0] + ".mat"
    maskpath = file_finder.get_labeled_path(matpath, "biofilmmask")
    distpath = file_finder.get_labeled_path(matpath, "bottommask")
    try:
        mask = scipy.io.loadmat(maskpath)["image"]
    except OSError as e:
        print("you probably need to generate a mask file first")
        raise e
    flipped = np.flipud(mask)
    distmask = slice10x.distance_top_mask_flat.get_top_mask(flipped)
    unfliped = np.flipud(distmask)
    scipy.io.savemat(distpath, {"image":unfliped})

def guess_cr_path(initial):
    basename = os.path.splitext(os.path.basename(initial))[0]
    dirname = os.path.dirname(initial)
    guess = os.path.join(dirname, basename, basename +"_cr.tiff")
    return guess

def guess_reduced_path(initial):
    basename = os.path.splitext(os.path.basename(initial))[0]
    dirname = os.path.dirname(initial)
    cr_file = os.path.join(dirname, basename, basename +"_cr.tiff")
    guess = glob.glob(cr_file.replace("_cr.tiff", "_cr_reduced20.tiff"))
    return guess


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--downscale', action="store_true")

    # parser.add_argument('--segment', action="store_true")
    # parser.add_argument('--kmeans_model', type=str)
    parser.add_argument('--mask_estimate', action="store_true")
    parser.add_argument('--edge_estimate', action="store_true")
    parser.add_argument('--bottom_estimate', action="store_true")
    parser.add_argument('--classic63x', action="store_true")

    parser.add_argument('--minidraw', action="store_true")
    parser.add_argument('--maxbright', type=float, default="0.25")

    parser.add_argument('--upscale', action="store_true")
    #parser.add_argument('--bigdraw', action="store_true")
    parser.add_argument('--mask_name', type=str, default="biofilmmask")

    parser.add_argument('--lsm_guess', '-l', type=str)
    parser.add_argument('--use_expanded_mask', action="store_true", default=False)
    parser.add_argument('--file', '-f', type=str)
    parser.add_argument('--remove_cr_from_mat_path', action="store_true", default=False)
    parser.add_argument('--channel', '-c', type=int, default=-1)

    pa = parser.parse_args()

    if pa.lsm_guess and not pa.file:
        cr_path = guess_cr_path(pa.lsm_guess)
        #print(cr_path)
        if pa.use_expanded_mask: 
            cr_red_path = cr_path
        else:
            cr_red_path = guess_reduced_path(pa.lsm_guess)

        if not cr_red_path:
            print("no reduced path, using the large image")
            cr_red_path = cr_path
        #print(cr_red_path)
    elif not pa.lsm_guess and pa.file:
        cr_path = pa.file
        cr_red_path = pa.file

    state = None
    if pa.downscale:
        downscale(cr_path, reductions=20)

    elif pa.upscale:
        if pa.lsm_guess:
            print("Probably you want to specify the file")
        upscale(cr_path)

    # elif pa.segment:
    #     if not pa.kmeans_model:
    #         segment_heuristic(cr_red_path) #, "segmented")
    #     elif pa.kmeans_model:
    #         segment_kmeans(pa.kmeans_model, cr_red_path)

    elif pa.mask_estimate:
        heuristic_biofilmmask(cr_red_path)

    elif pa.edge_estimate:
        heuristic_distmask(cr_red_path)
    elif pa.bottom_estimate:
        heuristic_bottommask(cr_red_path)
    elif pa.classic63x:
        #print(cr_red_path)
        heuristic_biofilm_seg_unscaled_lsm700_63x(cr_red_path)
    elif pa.minidraw:
        state = Editor(cr_red_path, "mini", pa.mask_name, channel=pa.channel, remove_chan_in_path=pa.remove_cr_from_mat_path, vmax=pa.maxbright)
    # elif pa.big_draw:
    #     state = Editor(pa.upscale, "big")
    else:
        print("No options specified")
        parser.print_usage()

    print("about to set key press listener")
    if state is not None:
        print("really about to")
        state.fig.canvas.mpl_connect('key_press_event', state.on_key_press)
        #state.fig.canvas.mpl_connect('key_release_event', state.on_key_release)
        #state.click_catcher = state.fig.canvas.mpl_connect('button_press_event', state.on_click)
        plt.show()#block=False)
        