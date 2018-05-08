import argparse
import gc
import os
import time

import numpy as np
import numpy.random as npr
import pandas as pd
import scipy.io
from sklearn.neighbors import KDTree 

import filedb
import resolutions


def get_mask_path(base, file_df, name, number):
    df = file_df[file_df.index == number]
    return os.path.join(base, df.dirname.values[0], df.name.values[0], df.name.values[0]) + "_{0}.mat".format(name)


def get_cache_path(base, file_df, number):
    df = file_df[file_df.index == number]
    try:
        os.makedirs(os.path.join(base, df.dirname.values[0]))
    except:
        pass
    return os.path.join(base, df.dirname.values[0], df.name.values[0] + "_spore_cell_dense.mat")


def ignore_edges(distmap, width):
    distmap[:width, :] = np.nan
    distmap[-width:, :] = np.nan
    distmap[:, -width:] = np.nan
    distmap[:, :width] = np.nan
    return distmap


def get_spore_density(file_df, spore_df, cell_df, mask_base, outdir, look_at_file):
    savename = get_cache_path(outdir, file_df, look_at_file)
    if os.path.exists(savename):
        print("skipping ", savename)
        return None

    lspore_df = spore_df[spore_df["global_file_id"] == look_at_file]
    lcell_df = cell_df[cell_df["global_file_id"] == look_at_file]

    spore_rc = lspore_df[["image_row", "image_col"]].values
    cells_rc = lcell_df[["image_row", "image_col"]].values
    spore_kdtree = KDTree(spore_rc)
    cells_kdtree = KDTree(cells_rc)
    
    #area_in_um2 = 150
    #area_in_um2 = 100
    #area_in_um2 = 50
    rad_um = 4 #np.sqrt(area_in_um2/np.pi)
    print("rad um", rad_um)
    pixrad = rad_um / resolutions.PX_TO_UM_LSM700_GIANT
    print("rad pix", pixrad)

    mask_path = get_mask_path(mask_base, file_df, "distmap", look_at_file)
    print("Reading Distance Map ", mask_path)
    tic = time.time()

    distmap = scipy.io.loadmat(mask_path)["distmap_masked"].astype(np.float32)
    
    ## We do not correct for the lack of density at the edges so 
    ## ignore 5 times the std of the gaussian so it will not affect much.
    five_sigma = int(pixrad * 5) 
    distmap = ignore_edges(distmap, five_sigma)
    
    distmap_shape = distmap.shape

    print("flattening, sorting")
    distmap = distmap.flatten()
    # Why do I sort it twice? Why did I not do 
    # sorted_distmap = distmap[sortind_distmap]
    sorted_distmap = np.sort(distmap)
    sortind_distmap = np.argsort(distmap)
    del(distmap)
    toc = time.time()
    print(toc-tic, "seconds to get the distmap, and sort it")

    distances = np.arange(2.0, 150, 0.5)
    window_half_width = 0.25
    centers = distances + window_half_width

    kd_daccum_mean = np.zeros_like(distances)
    kd_daccum_std = np.zeros_like(distances)
    kd_cells_mean = np.zeros_like(distances)
    kd_cells_std = np.zeros_like(distances)
    n_samples = 10000

    for d, dist in enumerate(centers):
        print("doing ", d, dist)
        # find the indices of the distance pixels in the current distance +- window
        dislice_start = np.searchsorted(sorted_distmap, dist - window_half_width, side="right")
        dislice_end = np.searchsorted(sorted_distmap, dist + window_half_width, side="left")
        indices_of_slice = sortind_distmap[dislice_start:dislice_end]
        print("found ", len(indices_of_slice), "points")
        if n_samples < len(indices_of_slice):
            sample_indices = npr.choice(indices_of_slice, size=n_samples, replace=False)
        else:
            sample_indices = indices_of_slice

        # convert these samples back into 2d rows and cols.  
        rr, cc = np.unravel_index(sample_indices, distmap_shape)
        sp = np.vstack([rr, cc]).T

        if sp.shape[0] > 0:
            spore_kd_densities = spore_kdtree.kernel_density(sp, h=pixrad, kernel='gaussian')
            kd_daccum_mean[d]  = np.mean(spore_kd_densities) 
            kd_daccum_std[d]   = np.std(spore_kd_densities) 
            kd_cell_densities  = cells_kdtree.kernel_density(sp, h=pixrad, kernel='gaussian')
            kd_cells_mean[d]   = np.mean(kd_cell_densities) 
            kd_cells_std[d]    = np.std(kd_cell_densities) 

    scipy.io.savemat(savename, {"centers":centers,
                                 "spore_kd_dense_g50": kd_daccum_mean, 
                                 "spore_kd_dense_g50_std": kd_daccum_std, 
                                 "cell_kd_dense_g50": kd_cells_mean, 
                                 "cell_kd_dense_g50_std": kd_cells_std, 
                                 })
    gc.collect()


def main():
    parser = argparse.ArgumentParser(description='args')
    parser.add_argument('--file_numbers', type=int, nargs='+',
                        help='integer file numbers')
    parser.add_argument('--quarter', type=int,
                        help='run part 0, to 3 of the list of files')
    parser.add_argument('--spore_db', type=str,
                        help='path to the spore hdf5 db')
    parser.add_argument('--cell_db', type=str,
                        help='path to the cell hdf5 db')
    parser.add_argument('--file_db', type=str,
                        help='path to the file list')
    parser.add_argument('--out_dir', type=str,
                        help='path to put the output density files')
    parser.add_argument('--mask_base', type=str,
                        help='path where the masks are stored')

    args = parser.parse_args()
    # base = "../../datasets/biofilm_cryoslice/LSM700_63x_sspb_giant/"
    # outputdir = "../../datasets/biofilm_cryoslice/LSM700_63x_sspb_giant/kd_spore_cell_2"
    # maskbase = "../../data/bio_film_data/data_local_cache/spores_63xbig"
    maskbase = args.mask_base
    #file_df = filedb.get_filedb(base + "file_list.tsv")
    file_df = filedb.get_filedb(args.file_db) 
    #spore_df = pd.read_hdf(base + "autocor_sporerem_data.h5", "spores")
    spore_df = pd.read_hdf(args.spore_db, "spores")
    cell_df = pd.read_hdf(args.cell_db, "cells")
    cell_df = cell_df[~cell_df["spore_overlap"]].copy() # remove cells that overlap spores

    numbers = [ num for (num, row) in file_df.iterrows() ]  
    
    if args.file_numbers is not None:
        numbers = args.files

    n = len(numbers)
    if args.quarter is not None:
        p = args.quarter
        numbers = numbers[(n//4)*p:(n//4)*(p+1)]

    for num in numbers:
        get_spore_density(file_df, spore_df, cell_df, maskbase, args.out_dir, look_at_file=num)


if __name__ == "__main__":
    main()
