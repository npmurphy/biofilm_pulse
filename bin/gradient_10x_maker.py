import argparse
import csv
import gc
import json
import os.path
from collections import OrderedDict

import numpy as np
import scipy.io
import skimage.filters
import skimage.io
import skimage.morphology

import util.file_finder as file_finder
from util import array_sub

chans = { "red": 0,
          "green": 1,
          "blue": 2}

stats = [("mean", np.mean), ("std", np.std)]
subtractions = {"raw": {"red": ["red_raw"],
                        "green": ["green_raw"]}, 
                "bg": {"red": ["red_bg"],
                       "green": ["red_bg"]}, 
                "bg_af": { "red": [ "red_bg", "red_autofluor"],
                           "green": ["green_bg", "green_autofluor"]},
                "bg_af_bt": {"green": ["green_bg", "green_autofluor", "green_bleedthrough"]} 
                }

fixed_heads = [ "cdist", "pixels"] 
color_chans = [ch + "_" + des for des, dt in subtractions.items() for ch in dt.keys()]
color_chans_stats = [ cc + "_" + s for cc in color_chans for s, _ in stats ] 
names = fixed_heads + color_chans_stats


def init_dict():
    return OrderedDict(zip(names, [np.nan]*len(names)))


def do_subtractions(img, subtractions, bgbleed_vals):
    result = {}
    for description, instructions in subtractions.items():
        for color, bg_val_list in instructions.items():
            subval = sum([bgbleed_vals[i] for i in bg_val_list])
            result[color + "_" + description] = array_sub(img[:,:,chans[color]], subval)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument('--sample_freq', type=float, default=0.25)
    parser.add_argument('--slice_width', type=float, default=0.5)
    parser.add_argument('--bg_subtract')
    pa = parser.parse_args()

    with open(pa.bg_subtract) as bgjs:
        bg_subvals = json.load(bgjs)
        bg_subvals["red_raw"] = 0 
        bg_subvals["green_raw"] = 0 

    datarow = init_dict()

    for num, f in enumerate(pa.files):
        print("{0} of {1}: {2}".format(num, len(pa.files), f))
        sptsv = f.replace(".tiff", ".tsv")
        with open(sptsv, "w") as csvf:
            writer = csv.DictWriter(csvf, fieldnames=names, delimiter="\t")
            writer.writeheader()
            #mask = images_to_data.get_20_mask(f)
            #th_files = insert_dir_in_path(f, spore_segdir).replace(".tiff", "_T{*).tiff")
            #sptsv = f.replace(".tiff", "_T{0}.tsv").format(pa.threshold)
            img = skimage.io.imread(f)
            channel_imgs = do_subtractions(img, subtractions, bg_subvals)

            base_dir = os.path.dirname(f)
            base_file = os.path.basename(f)
            base_no_ext = os.path.splitext(base_file)[0]

            base_fn = os.path.join(base_dir, base_no_ext, base_no_ext + ".mat")
            distmap_path = file_finder.get_labeled_path(base_fn, "distmap")
            distmap = scipy.io.loadmat(distmap_path)["distmap_masked"]
            mask = scipy.io.loadmat(file_finder.get_labeled_path(base_fn, "biofilmmask"))["image"].astype(np.bool)

            dmax = distmap.max()
            hw = pa.slice_width/2
            centers = np.arange(hw, dmax - hw, pa.sample_freq)

            for cdist in centers:
                dsr, dsc = np.where((distmap > (cdist-hw)) & (distmap <= (cdist+hw)) & mask)
                datarow["cdist"] = cdist
                datarow["pixels"] = len(dsr)
                for chan in channel_imgs.keys():
                    for stat, stat_func in stats: 
                        datarow[chan + "_" + stat] = stat_func(np.ravel(channel_imgs[chan][dsr,dsc]))

                writer.writerow(datarow)

        gc.collect()


if __name__ == "__main__":
    main()