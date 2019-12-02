# Giant process.
import argparse
import glob
import json
import os
import re
import sys
import time

import numpy as np
import scipy.io
import scipy.ndimage
import skimage.measure
import skimage.morphology
import tifffile

import lib.cell_segmenter as spore_segmentation
from lib import file_finder

CSV_HEADINGS = [
    "image_row",
    "image_col",
    "distance",
    "slice_row",
    "slice_col",
    "eccentricity",
    "mean",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", nargs="+")
    pa = parser.parse_args()

    if pa.files is None:
        print(parser.usage())
        print("no file or directory specified")
        sys.exit(2)

    # for red_f in pa.files:
    for lsm_file in pa.files:
        base_dir = os.path.dirname(lsm_file)
        base_file = os.path.basename(lsm_file)
        base_no_ext = os.path.splitext(base_file)[0]
        red_files = glob.glob(
            os.path.join(base_dir, base_no_ext, base_no_ext + "_cr_i*.tif")
        )
        files_nums = [
            (int(re.match(r".*cr_i1j(\d+).tif", f).groups(0)[0]), f) for f in red_files
        ]
        files_nums = sorted(files_nums)

        base_fn = os.path.join(base_dir, base_no_ext, base_no_ext + ".mat")
        distmap_path = file_finder.get_labeled_path(base_fn, "distmap")
        distmap = scipy.io.loadmat(distmap_path)["distmap_masked"]

        bigmask = scipy.io.loadmat(
            file_finder.get_labeled_path(base_fn, "biofilmmask")
        )["image"].astype(np.bool)

        with open(os.path.join(base_dir, base_no_ext, base_no_ext + ".json")) as jsfp:
            file_info = json.load(jsfp)

        big_image_col_shift = 0

        for filenum, red_f in files_nums:
            start = time.time()
            print("Processing {0}".format(red_f))
            green_f = red_f.replace("_cr_", "_cg_")
            csv_f = green_f.replace("_cg_", "_spores_").replace(".tif", ".tsv")

            file_key = re.match(r".*cr_(i\d+j\d+).tif", red_f).groups()[0]
            img_width = file_info[file_key]["cols"]

            sporeim = tifffile.imread(green_f)
            bf_mask = bigmask[:, big_image_col_shift : big_image_col_shift + img_width]
            assert sporeim.shape == bf_mask.shape
            # get over exposed.
            spore_lab = spore_segmentation.laphat_segment_v0(
                sporeim, cell_width_pixels=10
            )
            # print(spore_mask.dtype)
            # print(bf_mask.dtype)
            spore_lab *= bf_mask.astype(spore_lab.dtype)
            n_spore = len(np.unique(spore_lab)) - 1
            # if "j01" not in red_f:
            # ignores = np.unique(np.ravel(spore_lab[:100, :]))
            # avoid overlap from previous iamge
            # else:
            #    ignores = []
            print("found {0} spores".format(n_spore))
            spores = skimage.measure.regionprops(spore_lab, sporeim)
            if not (("j01" in red_f) or ("j1" in red_f)):
                spores = [spore for spore in spores if spore.centroid[1] > 200]
            with open(csv_f, "w") as tsvf:
                tsvf.write("\t".join(CSV_HEADINGS) + "\n")
                for spore in spores:
                    # if spore.label in ignores:
                    #     continue
                    row, col = tuple((int(round(x)) for x in spore.centroid))
                    bcol = col + big_image_col_shift
                    dist = "{0:.6f}".format(distmap[row, bcol])
                    vals = [
                        row,
                        bcol,
                        dist,
                        row,
                        col,
                        spore.eccentricity,
                        spore.mean_intensity,
                    ]
                    wstring = "\t".join([str(x) for x in vals])
                    tsvf.write(wstring + "\n")
            big_image_col_shift += img_width - 200

            done = time.time()
            print("Done: {0} seconds".format(done - start))
