import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io
import scipy.stats

import lib.figure_util as figure_util
import lib.filedb

#plt.style.use('../figstyle.mpl')

def get_cache_path(base, file_df, number):
    df = file_df[file_df.index == number]
    try:
        os.makedirs(os.path.join(base, df.dirname.values[0]))
    except:
        pass
    cache_file = os.path.join(base, df.dirname.values[0], df.name.values[0] + "_spore_cell_dense.mat")
    return cache_file

def get_plot_lines(file_df, cache_path, strain, dset ):
    strain_files = file_df[file_df.strain == strain]
    
    indiv_files = []
    for num, row in strain_files.iterrows():
        savename = get_cache_path(cache_path, file_df, num)
        try:
            otl = scipy.io.loadmat(savename)
        except FileNotFoundError as e:
            print("missing ", num)
            pass

        distances = otl["centers"][0]
        grad_line = otl[dset + "_kd_dense_g50"][0]

        indiv_files += [grad_line]
    print("strain", strain)
    print("individual files N=", len(indiv_files) )
    indiv_files_a = np.vstack(indiv_files).T
    indiv_files_a[indiv_files_a == 0] = np.nan
    mean_v = np.nanmean(indiv_files_a, axis=1)
    std_v = np.nanstd(indiv_files_a, axis=1)
    sem_v = scipy.stats.sem(indiv_files_a, axis=1, nan_policy="omit")
    return distances, mean_v, std_v, sem_v



def get_figure(ax, cache_path, file_df, sspb_strains, dset):

    for strain, name in sspb_strains:

        dists, mean_line, std_line, sem_line = get_plot_lines(file_df, cache_path, strain, dset)
        color = figure_util.strain_color[strain]

        ax.plot(dists, mean_line, color=color, label=name) 
        ax.fill_between(dists,
                        mean_line - sem_line, 
                        mean_line + sem_line,  
                        color=color, alpha=0.3)

    #ax.set_xlim(0, g("dists").max())
    ax.set_ylim(bottom=0)
    return ax


def main():
    base = "../../datasets/biofilm_cryoslice/LSM700_63x_sspb_giant/"
    datadir = os.path.join(base, "kd_spore_cell")
    file_df = filedb.get_filedb(base + "file_list.tsv")
    
    sspb_strains = [('JLB077', "WT",   ),
                    ('JLB118', "ΔσB",),
                    ('JLB117', "2×rsbQP",)]
    fig_main, ax = plt.subplots(2,1)
    ax[0] = get_figure(ax[0], datadir, file_df, sspb_strains, "spore")
    ax[1] = get_figure(ax[1], datadir, file_df, sspb_strains, "cell")
    ax[0].set_xlabel("Distance from air interface (μm)")
    #ax[0].set_ylabel("Proportion of cells that are spores")
    plt.show()


if __name__ == "__main__":
    main()
