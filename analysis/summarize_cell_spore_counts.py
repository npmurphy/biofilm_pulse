import os.path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io

import lib.filedb as filedb

import argparse

from lib.analysis.sliding_windows import sliding_window_counts

def get_file(df, fid):
    return df[df["global_file_id"]==fid]


def cache_cell_spore_ratio(file_df, spore_df, cell_df, st, min_sample_size): 
    st_files = file_df.index[(file_df.strain == st)]
    data_frames = [ (get_file(spore_df, fid), get_file(cell_df, fid)) for fid in st_files]
    step_freq = 0.25
    window = 2.0
    sp_counts = [ sliding_window_counts(spdf, cldf, (2, 140, step_freq), window) for spdf, cldf in data_frames]
    spore_counts = [ t[0,:] for d, t, n in sp_counts ]
    sp_ratios = [ t[0,:]/(t[0,:] + t[1,:]) for d, t, n in sp_counts ]
    total_counts = [ t[0,:] + t[1,:] for d, t, n in sp_counts ]
    cdists = sp_counts[0][0]
    join_array = np.vstack(sp_ratios)
    sporecount_array = np.vstack(spore_counts)
    cellcount_array = total_counts - sporecount_array
    count_array = np.vstack(total_counts)
    count_array[count_array<min_sample_size] = 0
    result = {"dists": cdists,
              "totalcounts": count_array,
              "eachimgcounts": total_counts # not sure why I have this when I have the counts. 
              }
    for name, data_array in [ ("sporeratio", join_array),
                              ("sporecounts", sporecount_array), 
                              ("cellcounts", cellcount_array),
                              ("totalcounts", count_array)]:
                
        data_array[count_array<min_sample_size] = np.nan
        result[name + "_mean"] = np.nanmean(data_array, axis=0)
        result[name + "_std"] = np.nanstd(data_array, axis=0) 
        good_rows = np.count_nonzero(data_array, axis=0)
        result[name + "_sem"] = np.nanstd(data_array, axis=0) / np.sqrt(good_rows)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_db")
    parser.add_argument("--spore_db")
    parser.add_argument("--cell_db")
    parser.add_argument("--out_file")
    args = parser.parse_args()

    #base = "../../datasets/LSM700_63x_sspb_giant/"
    file_df = filedb.get_filedb(args.file_db)

    # This image is not representative
    file_df = file_df[~((file_df["name"] == "JLB077_48hrs_center_1_1") & 
                        (file_df["dirname"] == "Batch1"))]

    #spore_df = pd.read_hdf(base + "autocor_sporerem_data.h5", "spores")
    print("loading the hd5 files")
    spore_df = pd.read_hdf(args.spore_db, "spores")
    cell_df = pd.read_hdf(args.cell_db, "cells")
    cell_df = cell_df[~cell_df["spore_overlap"]].copy() # remove cells that overlap spores
    print("ready to work")
    # cell_df = cell_df[cell_df["distance"]>2].copy()
    # spore_df = spore_df[spore_df["distance"]>2].copy()

    sspb_strains = [('JLB077', "WT"   ),
                    ('JLB117', "2xQP" ),
                    ('JLB118', "ΔσB"  ) ]
    # Some images had little tiny regions at the end with <10 cell spores in them 
    # that produced huges spikes of 100% spores etc. 
    # to ignore this we are using 100 as a minimum sample size. 
    # 10 does the job, 500, 100 look good at the top but introduce more artifacts later. 
    # 100 is just a big enough number. 
    data = { strain : cache_cell_spore_ratio( file_df, spore_df, cell_df, strain, 100) for strain, _ in sspb_strains}
    datad = { s + "_" + k : v for (s, d) in data.items() for (k, v) in d.items()}
    #datad = { k: v for d in data for k, v in d.items() }
    print("saving to: ",  args.out_file)
    scipy.io.savemat(args.out_file, datad)


if __name__ == '__main__':
    main()