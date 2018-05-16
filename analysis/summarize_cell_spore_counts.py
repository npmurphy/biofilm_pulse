import os.path

import numpy as np
import pandas as pd
import scipy.io

import lib.filedb as filedb

import argparse

from lib.analysis.sliding_windows import sliding_window_counts, sliding_window_pixel_counts

def get_file(df, fid):
    return df[df["global_file_id"]==fid]

def cache_indiv_cell_spore(file_df, spore_df, cell_df, distance_cache):
    step_freq = 0.25
    window = 2.0

    columns = {}
    
    for fid in file_df.index.values:
        sp_df = get_file(spore_df, fid)
        cl_df = get_file(cell_df, fid)
        distance_area = distance_cache["file_{0}".format(fid)][0,:]
        sw_dists, results, names = sliding_window_counts(sp_df, cl_df, (2, 140, step_freq), window)
        
        spore_counts = results[0,:]
        cell_counts = results[1,:]
        total_counts = spore_counts + cell_counts

        if "distance" not in columns:
            columns["distance"] = sw_dists

        columns["file_{0}_area_norm_spore_counts".format(fid)] = spore_counts/distance_area
        columns["file_{0}_area_norm_cell_counts".format(fid)] = cell_counts/distance_area
        columns["file_{0}_area_norm_total_counts".format(fid)] = total_counts/distance_area
        columns["file_{0}_total_counts".format(fid)] = total_counts
        columns["file_{0}_spore_counts".format(fid)] = spore_counts
        columns["file_{0}_cell_counts".format(fid)] = cell_counts
        columns["file_{0}_fraction_spores".format(fid)] = spore_counts/total_counts

    df = pd.DataFrame.from_dict(columns, orient="columns")
    return df 




def get_pixel_counts(file_df, fid, depth_info, window_width, datadir):
    this_file = file_df[file_df.index == fid]
    filename = this_file["name"].values[0]
    batch = this_file["dirname"].values[0]

    print("loading distmap", batch, filename)
    path_to_distmap = os.path.join(datadir, batch, filename, filename + "_distmap.mat")
    distmap = scipy.io.loadmat(path_to_distmap)["distmap_masked"].astype(np.float32)
    print("loaded")
    _, px_counts, _ = sliding_window_pixel_counts(distmap, depth_info, window_width)
    return px_counts


def cache_pixel_area(file_df, output_file, datadir): 
    step_freq = 0.25
    window = 2.0
    pixel_areas = { "file_{0}".format(fid): get_pixel_counts(file_df, fid, (2, 140, step_freq), window, datadir) for fid in file_df.index} 
    scipy.io.savemat(output_file, pixel_areas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_db")
    parser.add_argument("--spore_db")
    parser.add_argument("--cell_db")
    parser.add_argument("--area_cache")
    parser.add_argument("--data_files_to_recompute_area_cache", type=str) 
    parser.add_argument("--individual_files", action="store_true", default=False)
    parser.add_argument("--mean_finals", action="store_true", default=False)
    parser.add_argument("--out_file")
    args = parser.parse_args()

    file_df = filedb.get_filedb(args.file_db)

    # This image is not representative
    file_df = file_df[~((file_df["name"] == "JLB077_48hrs_center_1_1") & 
                        (file_df["dirname"] == "Batch1"))]


    if args.data_files_to_recompute_area_cache: 
        cache_pixel_area(file_df, args.area_cache, args.data_files_to_recompute_area_cache)
        print("done caching pixel witdths, exiting, run again with out the data_files_to_recompute_area_cache flag")
        return 0

    print("loading the hd5 files")
    spore_df = pd.read_hdf(args.spore_db, "spores")
    cell_df = pd.read_hdf(args.cell_db, "cells")
    cell_df = cell_df[~cell_df["spore_overlap"]].copy() # remove cells that overlap spores
    distance_cache = scipy.io.loadmat(args.area_cache)
    
    print("ready to work")

    cached = cache_indiv_cell_spore(file_df, spore_df, cell_df, distance_cache) 
    cached.to_csv(args.out_file, sep="\t", index_label="index")


if __name__ == '__main__':
    main()