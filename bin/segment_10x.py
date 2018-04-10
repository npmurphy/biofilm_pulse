
import argparse
import os.path

import numpy as np
import scipy.io
import scipy.ndimage
import skimage.io
import skimage.morphology
import shutil

from lib.processing import slice10x



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--make_backup', action="store_true")
    parser.add_argument('--tiff_file', "-f", type=str)
    parser.add_argument('--make_new_bfmask', action="store_true")
    parser.add_argument('--mask_name', default="biofilmmask")
    #parser.add_argument("--use_old_edgemask",action="store_true")
    #parser.add_argument('--segmentation_dir', type=str, default="segmented_laphat1")
    inputargs = parser.parse_args()

    image_name = os.path.splitext(os.path.basename(inputargs.tiff_file))[0]
    base_dir = os.path.dirname(inputargs.tiff_file)

    maskname = "_" + inputargs.mask_name

    if inputargs.make_backup:
        renames = [#("_edgemask.mat", "_expandededgemask.mat"),
                   #("_edgemask.tiff", "_expandededgemask.tiff"),
                   ("_cr_distmap.mat", "_cr_olddistmap.mat"),
                   ("_cr_biofilmmask.mat", "_cr_bfmaskcorrected.mat"),
                   # ("_biofilmmask.tiff", "_expandedbfmask.tiff")
                   ]
        for orig, newn in renames: 
            shutil.move(os.path.join(base_dir, image_name, image_name + orig),
                        os.path.join(base_dir, image_name, image_name + newn))

    if inputargs.make_new_bfmask:
        image_path = os.path.join(base_dir, image_name, image_name + "_cr.tiff")
        outname = os.path.join(base_dir, image_name, image_name + maskname)
        im = skimage.io.imread(image_path)
        mask = slice10x.basic_segment(im)
        scipy.io.savemat(outname + ".mat", {"image": mask})
        skimage.io.imsave(outname + ".tiff", mask.astype(np.uint8)*255)

    # if inputargs.edgemask:
    #     maskpath = os.path.join(base_dir, image_name, image_name + "_biofilmmask.mat")
    #     olddistpath = os.path.join(base_dir, image_name, image_name + "_expandededgemask.mat")
    #     bfmask = scipy.io.loadmat(maskpath)["image"]
    #     oldedgemask = scipy.io.loadmat(olddistpath)["image"]
    #     mask = slice10x.distance_top_mask_flat.get_top_mask(bfmask)
    #     need_filling = ~np.any(mask, axis=0)
    #     mask[:, need_filling] = oldedgemask[:, need_filling]
    #     outname = os.path.join(base_dir, image_name, image_name + "_edgemask")

    #     scipy.io.savemat(outname + ".mat", {"image": mask})
    #     skimage.io.imsave(outname + ".tiff", mask.astype(np.uint8)*255)


if __name__ == "__main__":
    main()
