import argparse
import csv
import glob
import json
import os
import re
import sys
import time
from collections import OrderedDict

import numpy as np
import scipy.io
import scipy.ndimage
import scipy
import skimage.measure
import tifffile

from lib.cell_segmenter import laphat_segment_v1
import lib.file_finder as file_finder
from lib.util import array_sub



def get_cached_segmentation(segmentation_method, filename, dirname="segmented_laphat1"):
    dirn, filen = os.path.dirname(filename), os.path.basename(filename)
    savename = os.path.join(dirn, dirname, filen)
    if os.path.exists(savename):
        tiffimg = tifffile.imread(savename)
        return tiffimg.astype("uint16")
    else:
        tiffimg = tifffile.imread(filename)
        wseg = segmentation_method(tiffimg)
        wseg = wseg.astype(np.dtype("uint16"))
        maxval = wseg.max()
        if maxval >= (2**16)-20:
            print("too many cells in image", maxval)
        if not os.path.exists(os.path.join(dirn, dirname)):
            os.mkdir(os.path.join(dirn, dirname))
        tifffile.imsave(savename, wseg, compress=7)
        return wseg


CSV_HEADINGS = [ "image_row"
                 , "image_col"
                 , "distance"
                 , "slice_row"
                 , "slice_col"
                 , 'segment_label'
                 , 'area'
                 , 'length'
                 , 'perimeter'
                 , 'eccentricity']

DEBUG = False
debugdir = "debug"


def get_cell_stats(im, distmap, cell_seg, cell_labels, max_val, cell_columns, base_key):
    # This will return nans for when the indeces are not in the seg.
    # So region props should have the same label id and the array position 
    cells_std = np.array(scipy.ndimage.standard_deviation(im, labels=cell_seg, index=cell_labels))
    cells_mean = np.array(scipy.ndimage.mean(im, labels=cell_seg, index=cell_labels))
    mean_val = np.nanmean(cells_mean)
    cells_normmean = cells_mean / mean_val

    def get_quick_max_val():
        # This gets the maximum mean value of RFP in the top 20 um of BF
        cells_median_dist = np.array(scipy.ndimage.median(distmap, labels=cell_seg, index=cell_labels))
        dist_lims = list(zip(range(2,20,1), range(3,21,1)))
        top_means = np.zeros(len(dist_lims))
        for i, (st, ed) in enumerate(dist_lims):
            top_means[i] = np.mean(cells_mean[(cells_median_dist > st) & (cells_median_dist <= ed)])
        return top_means

    if base_key not in max_val: # get value if its the first one (assume its red), reuse for other colors 
        max_val[base_key] = np.max(get_quick_max_val())
    cell_columns[base_key + "_std"] = cells_std
    cell_columns[base_key + "_mean"] = cells_mean
    cell_columns[base_key + "_meannorm"] = cells_normmean
    cell_columns[base_key + "_maxnorm"] = cells_mean / max_val[base_key]
    return cell_columns, max_val

        

def process_file(red_f, distmap, bigmask, get_segmentation, filenum, file_info, big_image_col_shift, subtract_values, color_subtract_fields):
    start = time.time()
    print("Processing {0}".format(red_f))
    csv_f = red_f.replace("_cr", "_cells")
    csv_f = os.path.splitext(csv_f)[0] + ".tsv"
    grn_f = red_f.replace("_cr", "_cg")
    blu_f = red_f.replace("_cr", "_cb")

    # for each biofilm mask file.
    filematch = re.match(r".*cr_(i\d+j\d+).tif", red_f)
    if filematch is not None:
        file_key = filematch.groups()[0]
        img_width = file_info[file_key]["cols"]
    else:
        img_width = 0

    if file_info == {}:
        bf_mask = bigmask
    else:
        stcol = big_image_col_shift
        edcol = big_image_col_shift+img_width
        print("considering mask from {0} to {1}".format(stcol, edcol))
        bf_mask = bigmask[:, stcol:edcol]

    imr = tifffile.imread(red_f)
    cell_seg = get_segmentation(red_f)
    if DEBUG:
        ocell_seg = cell_seg.copy()
        ocell_seg[ocell_seg > 0] = 2**14
    cell_seg *= bf_mask
    ## This allows the cell seg and region props to use the cell label directly
    cell_labels = np.arange(0, cell_seg.max()+1, dtype=np.int) #np.unique(cell_seg)[1:]
    ncell = len(cell_labels)
    if DEBUG:
        dbugimg = np.dstack([imr, ocell_seg, bf_mask.astype(np.uint16)*2**14])
        skimage.io.imsave(file_finder.insert_dir_in_path(debugdir, red_f), dbugimg)

    #labels = list(range(1, ndarray.max(cell_seg)+1))
    #assert(all(np.array([0] + labels) == np.unique(cell_seg)))
    cells = skimage.measure.regionprops(cell_seg)
    if not (("j01" in red_f) or ("j1" in red_f) and (file_info is not None)):
        cells = [cell for cell in cells if cell.centroid[1] > 200]

    cell_color_columns = {}
    for impath, chan in [(red_f, "red"), (grn_f, "green"), (blu_f, "blue")]:
        red_gradient_max_vals = {}
        try:
            im = tifffile.imread(impath)
            previous_sub_val = 0
            accumulated_subtract_fields = ""
            for field in color_subtract_fields[chan]:
                try:
                    accumulated_subtract_fields += "_" + field 
                    previous_sub_val += subtract_values[chan + "_" + field]
                    im = array_sub(im, previous_sub_val)
                    #red_gradient_max_val = None #this will be given a value below when we run "get_cell_stats"
                    stats_inputs = (im, 
                                    distmap,
                                    cell_seg,
                                    cell_labels,
                                    red_gradient_max_vals,
                                    cell_color_columns,
                                    chan + accumulated_subtract_fields)
                    cell_color_columns, red_gradient_max_val = get_cell_stats(*stats_inputs)
                except KeyError:
                    print("subtract field {0}, {1} not found".format(field, chan))
        
        except FileNotFoundError as e:
            print("no ", chan, "channel ")

    color_info_cols = cell_color_columns.keys()
    cell = OrderedDict([(k, "") for k in CSV_HEADINGS + list(color_info_cols)])
    print("found {0} cells".format(ncell))
    with open(csv_f, 'w') as tsvf: 
        w = csv.DictWriter(tsvf, cell.keys(), delimiter='\t')
        w.writeheader()

        for cellprop in cells: # range(len(centers)):
            #cell['file_number'] = fid
            row, col = tuple((int(round(x)) for x in cellprop.centroid))
            bcol = col + big_image_col_shift
            cell["image_row"] = row
            cell["image_col"] = bcol
            cell["distance"] = "{0:.6f}".format(distmap[row, bcol])
            cell["slice_row"] = row
            cell["slice_col"] = col
            cell['segment_label'] = cellprop.label
            cell['area'] = cellprop.area
            cell["length"] = cellprop.major_axis_length
            cell['perimeter'] = cellprop.perimeter
            cell['eccentricity'] = cellprop.eccentricity

            for key in color_info_cols:
                cell[key] = cell_color_columns[key][cellprop.label]

            w.writerow(cell)
            #global_col_shift = big_image_col_shift + shift_correction
            #wstring = "\t".join([ str(x) for x in [row, bcol, dist, row, col]])
    big_image_col_shift += img_width - 200
    done = time.time()
    print("Done: {0} seconds".format(done - start))
    return big_image_col_shift


def get_subtraction_numbers(args):
    if args.subtract_values_file is not None:
        with open(args.subtract_values_file) as bglfoj:
            bg_autofluor = json.load(bglfoj)
    else:
        bg_autofluor = {}
    bg_autofluor.update({"red_raw" : 0, "green_raw": 0, "blue_raw": 0})
    return bg_autofluor

def get_color_subtraction_sequences(args):
    inputs = list(zip(["red", "green", "blue"], [args.subtract_red, args.subtract_green, args.subtract_blue]))
    sequences = { k: ["raw"] for k, _ in inputs}
    for color, val in inputs: 
        if val is not None:
            sequences[color] = val
    return sequences

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument('-c', '--cell_width_pixels', type=int, default=10)
    parser.add_argument('--subtract_values_file', type=str)
    parser.add_argument('--subtract_red', nargs='+', type=str )
    parser.add_argument('--subtract_green', nargs='+', type=str )
    parser.add_argument('--subtract_blue', nargs='+', type=str )
    pa = parser.parse_args()


    if pa.files is None:
        print(parser.usage())
        print("no file specified")
        sys.exit(2)

    bg_autofluor = get_subtraction_numbers(pa)
    bg_color_subtract_seqs = get_color_subtraction_sequences(pa)


    for lsm_file in pa.files:
        base_dir = os.path.dirname(lsm_file)
        base_file = os.path.basename(lsm_file)
        base_no_ext = os.path.splitext(base_file)[0]
        red_files = glob.glob(os.path.join(base_dir, base_no_ext, base_no_ext + "_cr_i*.tif"))
        files_nums = [(int(re.match(r".*cr_i1j(\d+).tif", f).groups(0)[0]), f) for f in red_files]
        if len(red_files) == 0:
            files_nums = [(0, os.path.join(base_dir, base_no_ext, base_no_ext + "_cr.tiff"))]
        files_nums = sorted(files_nums)
        #print(red_files)
        if DEBUG:
            try:
                os.mkdir(os.path.join(base_dir, base_no_ext, debugdir))
            except:
                pass

        base_fn = os.path.join(base_dir, base_no_ext, base_no_ext + ".mat")

        distmap_path = file_finder.get_labeled_path(base_fn, "distmap")
        distmap = scipy.io.loadmat(distmap_path)["distmap_masked"]
        bigmask = scipy.io.loadmat(file_finder.get_labeled_path(base_fn, "biofilmmask"))["image"].astype(np.bool)

        def laphat_segmentation(img, cell_width_pixels):
            return laphat_segment_v1(img,
                                        cell_width_pixels=pa.cell_width_pixels,
                                        small_cells=(pa.cell_width_pixels < 6))

        def get_segmentation(x):
            return get_cached_segmentation(laphat_segmentation, x)

        try:
            with open(os.path.join(base_dir, base_no_ext, base_no_ext +".json")) as jsfp:
                file_info = json.load(jsfp)
        except:
            print("didnt find a split json file, pretending its a single image")
            file_info = {}

        big_image_col_shift = 0

        for filenum, red_f in files_nums:
            print("procing {0}", red_f)
            big_image_col_shift = process_file(red_f, distmap, bigmask, get_segmentation, 
                                               filenum, file_info, big_image_col_shift,
                                                bg_autofluor, bg_color_subtract_seqs)


if __name__ == "__main__":
    main()
