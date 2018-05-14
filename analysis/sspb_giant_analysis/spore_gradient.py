import os.path
import sys
from glob import glob

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io

import figure_util
import filedb



#############################
## Main figure
############################
def get_cache_path(base, file_df, number):
    df = file_df[file_df.index == number]
    try:
        os.makedirs(os.path.join(base, df.dirname.values[0]))
    except:
        pass
    return os.path.join(base, df.dirname.values[0], df.name.values[0] + "_save_autocor.mat")

def get_cell_rate(spdf, cldf, dists, fid):
    fid_spores = spdf[spdf["global_file_id"]==fid]
    fid_cell = cldf[cldf["global_file_id"]==fid]
    spore_count = fid_spores.groupby(pd.cut(fid_spores.distance, dists)).count()
    cell_count = fid_cell.groupby(pd.cut(fid_cell.distance, dists)).count()
    scaled_count = spore_count.image_col / (cell_count.image_col + spore_count.image_col)
    #scaled_count = spore_count.image_col 
    #scaled_count =  cell_count.image_col

    return scaled_count

def plot_cell_density(ax, basedir, file_df, strain, name, color): 
    stfile_df = file_df[file_df.strain == strain]
    num_files = len(stfile_df)
    normed = np.zeros((num_files, 150))
    unnormed = np.zeros((num_files, 150))
    for i, (num, row) in enumerate(stfile_df.iterrows()):
        savename = get_cache_path(basedir, file_df, num)
        try:
            otl = scipy.io.loadmat(savename)
        except:
            print("missing", savename)
        distances = otl["centers"][0]
        man_daccum = otl["kd_dense_g50_scaled_mean"][0]
        #man_daccum = otl["my_method_50"][0]
        unnormed[i, :] = man_daccum
        normed[i, :] = man_daccum/man_daccum.max()
        # except FileNotFoundError:
        #     unnormed[i, :] = np.nan
        #     normed[i, :] = np.nan
    #norm_mean = np.nanmean(normed, axis=0)
    unnorm_mean = np.nanmean(unnormed, axis=0)
    ax.plot(distances, unnorm_mean,label=name, color=color)
    unnormed_sem = np.std(unnormed, axis=0)/np.sqrt(num_files)
    #normed_sem = np.std(normed, axis=0)/np.sqrt(num_files)
    #normed_max = np.max(normed, axis=0)
    #normed_min = np.min(normed, axis=0)
    ax.fill_between(distances, unnorm_mean - unnormed_sem, unnorm_mean + unnormed_sem,  color=color, alpha=0.5)
    ax.ticklabel_format(style='sci',scilimits=(-4,-4),axis='y')
    ax.yaxis.major.formatter._useMathText = True
    return ax

def plot_cell_spore_grad(ax, file_df, dists, spore_df, cell_df, st, lab, color): 
    cdists = dists[0:-1] + (dists[1] - dists[0])
    st_files = file_df.index[(file_df.strain == st)]
    sp_counts = [ get_cell_rate(spore_df, cell_df, dists, fid) for fid in st_files]
    join_array = np.vstack(sp_counts)
    mean_sp_count = np.nanmean(join_array, axis=0)
    #print(join_array.shape[1])
    #std_sp_count = np.nanstd(join_array, axis=0) #/ np.sqrt(join_array.shape[1])
    std_sp_count = np.nanstd(join_array, axis=0) #/ np.sqrt(join_array.shape[1])
    #sem_sp_count = std_sp_count / np.sqrt(np.count_nonzero(join_array, axis=0))
    #std_sp_count = sem_sp_count 
    ax.plot(cdists, mean_sp_count, color=color, label=lab) 
    ax.fill_between(cdists,mean_sp_count- std_sp_count, mean_sp_count+ std_sp_count, color=color, alpha=0.3)
    ax.set_xlim(left=0)
    
    stfile_df = file_df[file_df.strain == st]
    num_files = len(stfile_df)
    print("strain {0} has {1} images".format(st, num_files))
    # normed = np.zeros((num_files, 151)) # TODO this shouldnt be hard coded
    # for i, (num, row) in enumerate(stfile_df.iterrows()):
    #     savename = get_cache_path(file_df, num)
    #     otl = scipy.io.loadmat(savename)
    #     distances = otl["distances"][0]
    #     man_daccum = otl["my_method_50"][0]
    #     normed[i, :] = man_daccum/man_daccum.max()
    #norm_mean = np.mean(normed, axis=0)
    #unnormed_sem = np.std(unnormed, axis=0)/np.sqrt(num_files)
    #normed_sem = np.std(normed, axis=0)/np.sqrt(num_files)
    # normed_max = np.max(normed, axis=0)
    # normed_min = np.min(normed, axis=0)
    # ax.plot(distances, norm_mean, label=name, color=color)
    # ax.fill_between(distances, normed_min, normed_max, color=color, alpha=0.4)
    ax.set_xlim(0, cdists.max())
    #ax.set_ylim(bottom=0)
    return ax



def main():
    base = "../../datasets/biofilm_cryoslice/LSM700_63x_sspb_giant/"
    file_df = filedb.get_filedb(base + "file_list.tsv")

    file_df = file_df[~((file_df["name"] == "JLB077_48hrs_center_1_1") & 
                        (file_df["dirname"] == "Batch1"))]


    dists = np.linspace(0,150,1201)

    spore_df = pd.read_hdf(base + "autocor_sporerem_data.h5", "spores")
    cell_df = pd.read_hdf(base + "autocor_sporerem_data.h5", "cells")
    cell_df = cell_df[~cell_df["spore_overlap"]].copy() # remove cells that overlap spores
    cell_df = cell_df[cell_df["distance"]>2]
    spore_df = spore_df[spore_df["distance"]>2]
    fig_main, ax = plt.subplots(2,1, sharex=True)

    for strain, name, color in figure_util.sspb_strains:
        #ax[0] =  plot_cell_density(ax[0], base, file_df, strain, name, color)
        ax[1] =  plot_cell_spore_grad(ax[1], file_df, dists, spore_df, cell_df, strain, name, color)

    #ax[0].set_ylabel("spores/area (spores/μm$^2$)" )
    ax[0].set_ylabel("spores/area", labelpad=(4.5/figure_util.pts2mm))#  (spores/μm$^2$)" )
    ax[0].set_ylim(bottom=0)
    #ax[1].set_ylim(bottom=0, top=0.25)
    ax[0].legend()
    ax[1].set_xlabel("Distance from air interface (μm)")
    ax[1].set_ylabel("spore/(cell + spore)")
    plt.show()


if __name__ == "__main__":
    main()
