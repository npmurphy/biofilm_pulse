import os.path

import matplotlib.pyplot as plt
import pandas as pd

import subfig_indivfile_histo

from lib import filedb
from lib import strainmap
 

from lib import figure_util
figure_util.apply_style()
from lib.figure_util import strain_color


def main():
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb")
    #cell_df = pd.read_hdf(os.path.join(basedir, "edge_redo_lh1segment_data_bg_back_bleed.h5"), "cells")
    cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
    print(cell_df.columns)

    file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
    file_df.loc[file_df["time"] == 26.0, ['time']] = 24.0
    file_df.loc[file_df["time"] == 38.0, ['time']] = 36.0
    
    USE_CACHE_PLOTS = False


    time = 48
    location = "center"
    slice_srt, slice_end = 5, 7 

    fig, axhisto = plt.subplots(1, 1)

    strain_map, des_strain_map = strainmap.load()
    gchan = "green_raw_bg_autofluor_bleedthrough_meannorm"

    gmax_val = 20
    nbins=150

    gbins = (0, gmax_val, nbins)

    percentile = 0
    list_of_histos = [ 
            ("wt_sigar_sigby", gchan, "WT P$_{sigB}$-YFP", strain_color["JLB021"]),
            ("delqp_sigar_sigby", gchan, "ΔrsbQP P$_{sigB}$-YFP", strain_color["JLB039"]),
            ("delru_sigar_sigby", gchan, "ΔrsbRU P$_{sigB}$-YFP", strain_color["JLB088"]),
            ("2xqp_sigar_sigby", gchan, "2$\\times$rsbQP P$_{sigB}$-YFP", strain_color["JLB095"]),
    ]
    print("-----------")
    lelines = []
    lelabs = []
    for i, (strain, chan, label, color) in enumerate(list_of_histos):
        print(label)
        fids = file_df[(file_df["time"] == time) &
                    (file_df["location"] == location) &
                    (file_df["strain"] == des_strain_map[strain])].index
        strain_df = cell_df[cell_df["global_file_id"].isin(fids)]
        #strain_df = get_strain(file_df, cell_df, strain) 
        plot_args = {"color":color, "max_min":"none", "mode_mean":False}
        tbins = gbins
        dset = time, location, strain

        args = (axhisto, strain_df, chan, tbins, (slice_srt, slice_end), dset, percentile, USE_CACHE_PLOTS, this_dir, plot_args)
        axhisto, line, _ = subfig_indivfile_histo.get_figure(*args)
        lelines += [line]
        lelabs += [label]
    axhisto.legend(lelines, lelabs)
        
    axhisto.set_xlabel("Normalised cell fluorecence (bleed through subtracted)")

    axhisto.set_ylabel("Percentage of cells") 
    axhisto.set_ylim(0, 7)
    axhisto.set_xlim(0, gmax_val)
        

    filename = "sup_bleed_histo"
    fig.subplots_adjust(left=0.1, right=0.9, top = 0.98, bottom=0.2)#, hspace=0.35, wspace=0.2)
    width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.5)
    fig.set_size_inches(width, height)# common.cm2inch(width, height))

    figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)



if __name__ == "__main__":
    main()

