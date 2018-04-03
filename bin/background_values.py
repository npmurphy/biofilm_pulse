#import filename_parser
#from data.bio_film_data import filedb
import argparse
import json
import os.path
from glob import glob
import re
import numpy as np
import pandas as pd
import scipy.io
import skimage.io

import util


image_section_funcs = {
    "all": lambda x: x > 0,
    "bottom": lambda x: x > 30, # after most of slope
    "top": lambda x: (x > 0) & (x <= 20) # before most of slope
}
    
channels = {"red": ["bg", "autofluor"], 
            "green":["bg", "autofluor", "bleedthrough", "actual"],
            "green_raw": ["actual"]} # get the raw YFP signal with no subtractions
file_keys = {"bg": "WT|RFP", 
             "autofluor": "WT",
             "bleedthrough": "RFP",
             "actual": "SigB"}
mask_keys = {"bg":"background", 
             "autofluor": "segmented", 
             "bleedthrough": "segmented", 
             "actual": "distmap"}


def get_file_dirname(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    dirname = os.path.dirname(path)
    return dirname, filename

def get_paths(path):
    dirname, basename = get_file_dirname(path)
    return basename, os.path.join(dirname, basename, basename)
    

def compute_subtraction(row, maskname, color, subtraction_value, section=""):
    basename = row["file_name"]
    dirname = row["dir_name"]
    basepath = os.path.join(dirname, basename, basename)
    datapath = basepath + "_" + maskname + ".mat"
    imgpath = basepath + "_c{0}.tiff".format(color[0])
    try:
        if maskname == "distmap":
            df = scipy.io.loadmat(datapath)["distmap_masked"]
            data = (image_section_funcs[section])(df) # get top, bottom, or all
        else:
            data = scipy.io.loadmat(datapath)["image"]
    except TypeError as e:
        print("file {0} not found".format(datapath))
        raise e
    img = skimage.io.imread(imgpath)
    img = util.array_sub(img, subtraction_value)
    return np.mean(img[data==1])

def get_new_bg_flour_func(pa):
    fileData = pd.DataFrame()
    dirnames, filenames = zip(*[ get_file_dirname(f) for f in pa.files])
    strains = [fn.split("_")[0] for fn in filenames]  
    fileData["file_name"] = filenames
    fileData["dir_name"] = dirnames
    fileData["strain"] = strains
    
    for color in channels.keys(): # yes I know, we read each mask twice but we just run once. 
        print("Color ", color)
        fileData[color + "_none"] = 0
        acumulated_subtraction_list = ["none"]
        for subtraction in channels[color]:
            means = fileData.mean() # a series with the mean of each column
            print(acumulated_subtraction_list)
            print([ means[color + "_" + s] for s in acumulated_subtraction_list])
            subtraction_value = sum([ means[color + "_" + s] for s in acumulated_subtraction_list])

            def file_process(row, section=""):
                if re.match(file_keys[subtraction], row["strain"]):
                    return compute_subtraction(row, mask_keys[subtraction], color, subtraction_value, section=section)
                else:
                    return np.nan

            if subtraction == "actual":
                # look at the "top", "not top", and "all" of gradient.
                for section in image_section_funcs.keys():
                    sec_col = color + "_" + subtraction + "_" + section 
                    fp = lambda x: file_process(x, section=section)
                    fileData[sec_col] = fileData.apply(fp, axis=1)
            else: 
                #normally just do a straight pass. 
                fileData[color + "_" + subtraction] = fileData.apply(file_process, axis=1)
            acumulated_subtraction_list += [subtraction]

    fileData = fileData.drop(columns=[c + "_none" for c in channels])
    fileData.to_csv(pa.output + ".tsv", sep="\t", index_label="index")
    means = fileData.mean() # a series with the mean of each column
    with open(pa.output + ".json", "w") as jo:
        json.dump(means.to_dict(), jo)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') #, help="this expects LSM files")
    parser.add_argument('-o', '--output', default="bg_values")
    pa = parser.parse_args()
    
    if len(pa.files) == 1 and "*" in pa.files[0]:
        pa.files = glob(pa.files[0], recursive=True)
    
    get_new_bg_flour_func(pa)


if __name__ == "__main__":
    main()    
