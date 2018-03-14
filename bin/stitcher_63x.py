#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from common import read_lsm, save_tiff
import numpy as np
from glob import glob
import os.path
import os
import sys
#import skimage.io
import argparse
from lib.processing.stitch_images import top_is_on_left, find_minimal_overlap
from lib.processing.stitch_images import join_images_with_offset, get_files_in_order

def make_stiched_same_name(top_name):
    savename = top_name.replace("_top_", "_")
    savename = savename.replace("_top", "_")
    savename = savename.replace(".lsm", "")
    savename = savename + "_stitched"
    savename = savename.replace("__","_")
    return savename + ".tiff"
    

def join_list_of_images(lof, filenames):
    lofi = iter(lof)
    imr = next(lofi)
    #trouble = []
    for i, imn in enumerate(lofi, start=1):
        print("joining {0} of {1}:, {2}".format(i+1, len(lof), filenames[i]))
        #try:
        #    imr = join_images(imr, imn)
        #except Exception as e:
        offset = find_minimal_overlap(imr, imn)
        #print("\t\t Trying backup method offset:", offset)
        imr = join_images_with_offset(imr, imn, offset)
        #trouble += [filenames[i]]
    return imr#, trouble


def load_and_rotate_images(lof, check_top=True):
    need_rotate = not top_is_on_left(lof[0], check_top)
    images = []
    for fn in lof:
        im = read_lsm(fn)
        if need_rotate:
            im = np.rot90(im, 2)
        images += [im]
    return images



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') 
    parser.add_argument('-m', '--manual', nargs='+' )
    #parser.add_argument('-d', '--delete', action='store_true', default=False)
    parser.add_argument('--single_image', action='store_true', default=False)
    parser.add_argument('--check', action='store_true', default=False)
    parser.add_argument('--dont_try_overlap', action='store_true', default=False)
    parser.add_argument('--dont_check_top', action='store_true', default=False)
    parser.add_argument('--output_name', type=str, default=True)
    pa = parser.parse_args()

    if pa.files and pa.manual:
        print("cannot use --manual and --files")
        sys.exit(2)

    get_files_in_order_func = get_files_in_order

    if pa.files:
        sfl = []
        for f in pa.files: 
            if os.path.isdir(f):
                sfl += glob(os.path.join(f, "*.lsm"))
            else:
                sfl += [f]
        #lsmfiles = [x for x in lsmfiles if "Z" not in x]
        topfiles = [x for x in sfl if "top" in x]

    elif pa.manual:
        print("I assume you have listed the files in order of joining")
        topfiles = [pa.manual[0]]
        get_files_in_order_func = lambda x: (pa.manual[:], [])


    if pa.check:
        for top_name in topfiles:
            tiffname = make_stiched_same_name(top_name)
            if not os.path.exists(tiffname):
                print ("FAILED: {0}".format(top_name))
    elif pa.single_image:
        print("Single image")

        def matches(x):
            y = os.path.basename(x)
            #m = re.search(r"([^_\W]+|del_SigB|RFP_only)_\d\d[hH]rs_[a-zA-Z]+_\d+_\d+_sect.lsm",y)
            #m2 = re.search(r"([^_\W]+|del_SigB|RFP_only)_\d\d[hH]rs_[a-zA-Z]+_[a-zA-Z]+_\d+.lsm",y)
            #m3 = re.search(r"([^_\W]+|del_SigB|RFP_only)_\d\d[hH]rs_[a-zA-Z](_)?\d+.lsm",y)
            #if m or m2 or m3:
            if "bead" not in y.lower():
                return True 
            else:
                return False
        singles = [ f for f in sfl if matches(f)] 
        for s_file in singles:
            print("fake stiching single image file: {0}".format(s_file)) 
            imord = load_and_rotate_images([s_file], check_top=not(pa.dont_check_top))
            tiffname = s_file.replace(".lsm", "_stitched.tiff")
            mktime = os.stat(s_file).st_mtime
            save_tiff(tiffname, imord[0], compress=6)
            #mktime = os.path.getmtime(s_file)
            os.utime(tiffname, (mktime, mktime))

    else :
        for top_name in topfiles:
            print("TOP: ", top_name)

            files_in_order, files_left_out = get_files_in_order_func(top_name)
            if files_left_out != []:
                print("\tNot all files accounted for:")
                print(files_left_out)
                continue

            #print("\t", "\n\t".join(files_in_order))
            imord = load_and_rotate_images(files_in_order,  check_top=not(pa.dont_check_top))
            joined_image = join_list_of_images(imord, files_in_order, pa.dont_try_overlap)
            
            tiffname = make_stiched_same_name(top_name)
            print("Writing image : gimp ", tiffname)
            save_tiff(tiffname, joined_image, compress=6)
            #mktime = os.path.getmtime(top_name)
            mktime = os.stat(top_name).st_mtime
            os.utime(tiffname, (mktime, mktime))

            print("-------------")


if __name__ == "__main__":
    main()
