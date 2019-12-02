import argparse
import re
from glob import glob

import sys

import numpy as np
import skimage.draw
import skimage.exposure
import skimage.io
import skimage.morphology
import skimage.segmentation
import scipy.io
from lib.cell_tracking import cell_dimensions
#import tifffile

from lib.cell_tracking.track_data import TrackData
import pandas as pd
#jfrom lib.cell_tracking import auto_match

#import scipy.ndimage

def get_image_range(file_pattern, image_range):
    parse_re = re.compile(re.sub(r"{\d?:\d+d}", r"(\d+)", file_pattern))
    if image_range == (None, None):
        tmppattern_st = file_pattern.split("{")[0]
        tmppattern_ed = file_pattern.split("}")[1]

        def parse_number(filepath):
            parsed = parse_re.match(filepath).groups()
            return int(parsed[0])
        
        return sorted([parse_number(f) for f in glob(tmppattern_st + "*" + tmppattern_ed)])
    else:
        return list(image_range[0], image_range[1])

def count_number_of_images(file_pattern, trackdata_path):
    image_range = get_image_range(file_pattern, (None, None))
    trackdata = TrackData(trackdata_path, max(image_range))
    counter = 0
    for cell in trackdata.get_cells_list():
        frames_alive, = np.where(np.array(trackdata.cells[cell]["state"]) > 0)
        counter += len(frames_alive)
    print("there were {0} images available".format(counter))
    return counter


def export_data_ellipse(filename, filepattern, trackdata_path, window_size, process_data, dims, dtype):
    image_range = get_image_range(filepattern, (None, None))
    print(image_range)
    # if window_size % 2 == 0:
    #     window_size += 1

    red_chan = "ch00"
    green_chan = "ch01"
    blue_chan = "ch02"
    num_images = count_number_of_images(filepattern, trackdata_path)

    trackdata = TrackData(trackdata_path, max(image_range))
    image_bank = np.zeros((num_images, window_size, window_size, num_images, dims), dtype=dtype) #, np.float32)
    mask_bank = np.zeros((num_images, window_size, window_size, num_images, 1), dtype=dtype) #, np.float32)
    output_bank = [{}] * num_images
    w = (window_size)//2
    i = 0
    for f in range(trackdata.metadata["max_frames"]):
        print("frame ", f )
        cells_alive = trackdata.get_cells_in_frame(f, state=[1])
        if len(cells_alive) == 0:
            continue
        image = skimage.io.imread(filepattern.format(f))
        processed = process_data(image)
        for cell in cells_alive:
            cell_props = trackdata.get_cell_properties(f, cell)
            cell = trackdata.get_cell_params(f, cell)
            mask = np.zeros(image.shape, dtype=dtype) #, np.float32)
            mask[cell_dimensions.get_cell_pixels(*cell, image.shape)] = 1.0
            output_bank[i] = cell_props
            r = int(cell_props["row"])
            c = int(cell_props["col"])
            # print(image_bank.shape)
            # print(processed.shape)
            # print(r-w, r+w, c-w, c+w) 
            #NHWC
            image_bank[i, :, :, :] = np.transpose(processed[:, r-w:r+w, c-w:c+w], (1,2,0))
            mask_bank[i, :, :, 0] = mask[r-w:r+w, c-w:c+w]
            i+= 1

    df = pd.DataFrame.from_dict(output_bank)
    df_array = df.values
    cols = list(df.columns)
    tosave = {"images": image_bank, 
              "mask": mask_bank,
              "outputs": df_array,
              "columns": cols}
    #print(tosave.keys)
    scipy.io.savemat(filename, tosave)
    return None


def whitehat_gauss_lap(img):
    return img

def just_gauss(img):
    gimg = skimage.filters.gaussian(img, sigma=2).astype(np.float16)
    ri_img = skimage.exposure.rescale_intensity(gimg, in_range="image", out_range=(0, 1))
    return np.array([ri_img.astype(np.float16)])

#get_func = { "whitehat_gauss_lap": (whitehat_gauss_lap, 3, np.uint8)}
get_func = { "gauss": (just_gauss, 1, np.float16)}
             
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', type=str, required=True)
    parser.add_argument('--trackdata', type=str, required=True)
    parser.add_argument('--outputfile', type=str, required=True)
    pa = parser.parse_args()
    window_size = 64
    proc_func, dims, dtype = get_func["gauss"]
    export_data_ellipse(pa.outputfile, pa.images, pa.trackdata, window_size, proc_func, dims, dtype)


if __name__ == '__main__':
    main()