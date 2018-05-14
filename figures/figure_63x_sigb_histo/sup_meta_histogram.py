import os.path
import matplotlib as mpl
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
#import subfig_dist_joy
import joy_plots_of_gradients
from lib import filedb
#import os.path
import scipy.stats
import numpy as np
import pandas as pd
from lib import strainmap

from lib import figure_util
figure_util.apply_style()

def main():
    curve_score_methods = {
        "std": ("Standard deviation",
               1.5,  
               lambda d, h, b: np.std(d)), 
        "mean": ("Mean", 
               4.0,
               lambda d, h, b: np.mean(d)),
        "cv": ("Coefficient of variation", 
               1.2,
               lambda d, h, b: scipy.stats.variation(d)),
        "skew": ("modern skew", 
               3.0,
               lambda d, h, b: scipy.stats.skew(d)),
        "skew_normed": ("Skew", 
               2.9,
               lambda d, h, b: scipy.stats.skew(d, bias=False)),
        "mode": ("Mode", 
               3.5,
               lambda d, h, b: b[h.argmax()]),
        "num": ("# cells", 
               2000,
               lambda d, h, b: len(d)),
        "pearson_mode_mean": ("pearson Mode mean", 
                1.2, 
                joy_plots_of_gradients.pearson_mode_mean_skew),
        "non_parameteric_skew": ("Non parameteric", 
                0.4, 
                joy_plots_of_gradients.non_parametric_skew),
        "kurtosis": ("Kurtosis", 
                8.0, 
               lambda d, h, b: scipy.stats.kurtosis(d))
    }

    plot_colors = [ #"mean",
                    "std",
                    #"cv",
                    #"skew",
                    #"num",
                    #"skew_normed",
                    "skew_normed", # same as pandas 
                    #"pearson_mode_mean",
                    #"non_parameteric_skew",
                    #"kurtosis",
                    ]
    
    #basedir = "../../data/bio_film_data/63xdatasets"
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb")
    #cell_df = pd.read_hdf(os.path.join(basedir, "edge_redo_lh1segment_data_bg_back_bleed.h5"), "cells")
    #cell_df = pd.read_hdf(os.path.join(basedir, "new_edge_bgsubv2_maxnorm_lh1segment.h5"), "cells")
    cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
    #cell_df = pd.read_hdf(os.path.join(basedir, "edge_redo_lh1segment_data.h5"), "cells")
    #cell_df = pd.read_hdf(os.path.join(basedir, "lh1segment_bgsub_data.h5"), "cells")
    #cell_df = cell_df[cell_df["area"] > 140]
    cell_df = cell_df[cell_df["distance"] > 2]
    time = 48 #.0
    location = "center"
    file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
    strain_map, des_strain_map = strainmap.load()

    percentile = 0#99#    
    # green_chan = "meannorm_green"
    # red_chan = "meannorm_red"
    green_chan = "green_raw_bg_meannorm"
    red_chan = "red_raw_bg_meannorm"
    rmax = 6.5
    gmax = 6.5 #0.4
    strains = [ ("wt_sigar_sigby", red_chan, rmax, "WT\n P$_{sigA}$-RFP"), 
                ("wt_sigar_sigby", green_chan,    gmax,  "WT\n P$_{sigB}$-YFP"),
                ("delqp_sigar_sigby", green_chan, gmax,  "ΔrsbQP\n P$_{sigB}$-YFP"),
                ("delru_sigar_sigby", green_chan, gmax,  "ΔrsbRU\n P$_{sigB}$-YFP"),
                ("2xqp_sigar_sigby", green_chan,  gmax,  "2$\\times$rsbQP\n P$_{sigB}$-YFP")]
    
    fig, ax = plt.subplots(len(plot_colors), len(strains),  sharey=True) 
    for c, (strain, chan, max_val, name) in enumerate(strains):
        strain_num = des_strain_map[strain]
        distances, sbins, histograms, stats = joy_plots_of_gradients.get_strain_result(file_df, cell_df, time, location,
                                                                 strain_num, chan, max_val, percentile, curve_score_methods)
        for r, k in enumerate(plot_colors):
            color = figure_util.strain_color[strain_num.upper()]
            ax[r, c], mv, leglist = joy_plots_of_gradients.plot_curves(ax[r,c], color, distances, sbins, histograms, stats, k)

            if c == len(strains)-1:
                posn = ax[r,c].get_position()
                cbax = fig.add_axes([posn.x0 + posn.width + 0.0005, posn.y0, 0.015, posn.height])
                max_zval = curve_score_methods[k][1]
                label = curve_score_methods[k][0]
                sm = plt.cm.ScalarMappable(cmap=plt.get_cmap("viridis"), norm=plt.Normalize(vmin=0, vmax=max_zval))
                sm._A = []
                _ = plt.colorbar(sm, cax=cbax)#, fig=fig)
                cbax.set_ylabel(label, rotation=-90, labelpad=8)
                cbax.tick_params(direction='out')


            if r == 0:
                ax[r,c].set_title(name, fontsize=6)
                ax[r,c].get_xaxis().set_ticklabels([])
        
            ax[r,c].set_xlim(0, max_val)

    #this didnt return the right mode for some reason    
    #leg = ax[0, -1].legend(leglist)

    leg = ax[0, -1].legend(leglist, ["Mode", "Mean"], loc='lower left', bbox_to_anchor=(0.84, 0.97))
    leg.set_zorder(400)
    for a in ax.flatten():
        a.tick_params(direction='out')
    ax[0,0].annotate("Distance from air interface (μm)",
                    xy=(0,0),
                    xytext=(0.02, 0.5),  
                    textcoords='figure fraction',
                    #arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='center',
                    fontsize="medium", color=mpl.rcParams['axes.labelcolor'],
                    rotation=90
                    )
    ax[1,2].annotate('Normalized fluoresence', 
                    xy=(0,0),
                    xytext=(0.5, 0.04),  
                    textcoords='figure fraction',
                    #arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='center',
                    fontsize="medium", color=mpl.rcParams['axes.labelcolor']
                    )
    # for a in ax[:, 0].flatten():
    #     ticklabs = a.yaxis.get_ticklabels()
    #     ticklabs = a.get_yticks()#.tolist()
    #     ticklabs[-1] = ''

    letters = [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"] 
    #letter_lab = (-0.13, 0.98)
    for a, l in zip(ax.flatten(), letters):
        a.annotate(l, xy=(0,0),
                    xytext=(-0.13, 0.95),  
                    textcoords='axes fraction',
                    #arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=figure_util.letter_font_size, color="black"
                    )
    #    a.text(letter_lab[0], letter_lab[1], l, transform=a.transAxes, fontsize=8)

    filename = "sup_meta_histo"
    width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=0.6 )
    fig.subplots_adjust(left=0.085, right=0.89, top=0.89, bottom=0.13, hspace=0.20, wspace=0.25)
    fig.set_size_inches(width, height)# common.cm2inch(width, height))
    figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)



if __name__ == "__main__":
    main()



