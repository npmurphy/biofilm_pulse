import os.path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import scipy.interpolate
import scipy.ndimage.filters
import scipy.stats

from lib import figure_util
from lib import filedb, strainmap
#from lib.analysis.sliding_windows import sliding_window_histos, sliding_window_distribution
from lib.analysis.sliding_windows import sliding_window_histos_with_stats


def get_strain_result(file_df, cell_df, time, location, strain_num, chan, max_val, percentile, stats_to_compute):
    fids = file_df[(file_df["time"] == time) &
                    (file_df["location"] == location) &
                    (file_df["strain"] == strain_num )].index
    df = cell_df[cell_df["global_file_id"].isin(fids)]

    distance_samples = (2.5, 140, 6) # start,stop,spacing
    width = 2.
    distances, bins, distrib, stats = sliding_window_histos_with_stats(df, distance_samples,
                                     width, chan, 100, valbinmax=max_val,
                                     blur=0, percentile=percentile, calc_stats=stats_to_compute)
    distrib = np.fliplr(distrib)
    distances = distances[::-1]
    res_stats = { k: (v[0], v[1], stats[k][::-1]) for k, v in stats_to_compute.items()}
    return distances, bins, distrib, res_stats 

def plot_curves(ax, mean_color, distances, x_range, histograms, stats, color_stat):
    curves_no = histograms.shape[1]
    scale = 250.
    #max_val = stats[color_stat][2].max()
    min_scale_val = stats[color_stat][1][0]
    scale_val = stats[color_stat][1][1]

    max_cval = 0
    for i in range(0, curves_no):
        yshift = distances[i]
        scaled_data = (histograms[:,i]*scale) + yshift

        # get the mean 
        meanval = stats["mean"][2][i]
        #print("problem", meanval)
        interp = scipy.interpolate.interp1d(x_range, scaled_data)
        mean_y = interp(meanval)

        #mode_val = stats["mode"][2][i]
        #mode_nearest_x = np.argwhere(x_range>=mode_val)[0]
       
        stat_val = stats[color_stat][2][i]
        # Check we dont have negative skew
        #cmap = plt.get_cmap("seismic")
        #curve_color = cmap((stat_val + scale_val)/(2*scale_val))
        #cmap = plt.get_cmap("plasma")
        cmap = plt.get_cmap("viridis")
        curve_color = cmap((stat_val-min_scale_val)/(scale_val-min_scale_val))
       
        #if pearson_mm_skew > max_pskew:
        #    max_pskew = pearson_mm_skew
        ax.plot(x_range, scaled_data, color="black", zorder=(i*2), linewidth=0.25)
        ax.fill_between(x_range, scaled_data, interpolate=True, color=curve_color, zorder=(i*2))

        markerset = {"marker" : ".", 
                     "markersize": 1,
                     "linestyle": "none"}        
        # mol = ax.plot(mode_val, scaled_data[mode_nearest_x], label="Mode",
        #         color=figure_util.mode_color, zorder=(i*2)+1, **markerset) 
        mal = ax.plot(meanval, mean_y, label="Mean", 
                        color=figure_util.mean_color, zorder=(i*2)+1, **markerset)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=3, integer=True))
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=3, integer=True))

    #ax.patch.set_facecolor(bg_color)
    ax.set_ylim(0, 160)
    #print(np.nanmax(pdistrib[:,plabels[metric]]))

    mol = [None]
    return ax, max_cval, mol + mal

def pearson_mode_mean_skew(data, histo, bins):
    stdval = np.std(data)
    meanval = np.mean(data)
    modeval = bins[histo.argmax()]
    pearson_mm_skew = (meanval - modeval)/stdval # mode version 
    return pearson_mm_skew

def non_parametric_skew(data, histo, bins):
    stdval = np.std(data)
    meanval = np.mean(data)
    median = np.median(data)
    return (meanval - median)/stdval # mode version 


def main():
    
    curve_score_methods = {
        "std": ("Standard Deviation",
               2.5,  
               lambda d, h, b: np.std(d)), 
        "mean": ("Mean", 
               4.0,
               lambda d, h, b: np.mean(d)),
        "cv": ("Coefficient of variation", 
               1.2,
               lambda d, h, b: scipy.stats.variation(d)),
        "skew": ("modern skew", 
               3.5,
               lambda d, h, b: scipy.stats.skew(d)),
        "skew_normed": ("Skew", 
               4.0,
               lambda d, h, b: scipy.stats.skew(d, bias=False)),
        "mode": ("Mode", 
               3.5,
               lambda d, h, b: b[h.argmax()]),
        "num": ("# cells", 
               2000,
               lambda d, h, b: len(d)),
        "pearson_mode_mean": ("pearson Mode mean", 
                1.2, 
                pearson_mode_mean_skew),
        "non_parameteric_skew": ("Non parameteric", 
                0.4, 
                non_parametric_skew),
        "kurtosis": ("Kurtosis", 
                8.0, 
               lambda d, h, b: scipy.stats.kurtosis(d))
    }

    plot_colors = [ #"mean",
                    "std",
                    #"cv",
                    #"skew",
                    #"num",
                    "skew_normed",
                    #"pearson_mode_mean",
                    #"non_parameteric_skew",
                    #"kurtosis",
                    ]
    
    basedir = "../../datasets/biofilm_cryoslice/LSM700_63x_sigb"
    #cell_df = pd.read_hdf(os.path.join(basedir, "new_edge_bgsubv2_maxnorm_lh1segment.h5"), "cells")
    #cell_df = pd.read_hdf(os.path.join(basedir, "new_edge_bgsubv2_maxnorm_lh1segment.h5"), "cells")
    #cell_df = pd.read_hdf(os.path.join(basedir, "mini_bgsubv2_maxnorm_comp5.h5"), "cells")
    cell_df = pd.read_hdf(os.path.join(basedir, "bgsubv2_maxnorm_comp5.h5"), "cells")
    cell_df = cell_df[cell_df["red_bg_maxnorm"] > 0]
    cell_df = cell_df[cell_df["distance"] > 2]
    time = 48 #.0
    location = "center"
    file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
    strain_map, des_strain_map = strainmap.load()

    percentile = 0#99#    
    gmax = None 
    rmax = None
    gmax = 0.7
    rmax = 3.0
    strains = [ ("wt_sigar_sigby", "red_bg_maxnorm", rmax), 
                ("wt_sigar_sigby", "green_bg_maxnorm",    gmax),
                ("delqp_sigar_sigby", "green_bg_maxnorm", gmax),
                ("delru_sigar_sigby", "green_bg_maxnorm", gmax),
                ("2xqp_sigar_sigby", "green_bg_maxnorm",  gmax)]
    
    fig, ax = plt.subplots(len(plot_colors), len(strains), sharex=True, sharey=True) 
    for c, (strain, chan, maxv) in enumerate(strains):
        strain_num = des_strain_map[strain]
        distances, sbins, histograms, stats = get_strain_result(file_df, cell_df, time, location,
                                                                 strain_num, chan, maxv, percentile, curve_score_methods)
        for r, k in enumerate(plot_colors):
            color = figure_util.strain_color[strain_num.upper()]
            ax[r, c], mx, mv = plot_curves(ax[r,c], color, distances, sbins, histograms, stats, k)

            if c == len(strains)-1:
                posn = ax[r,c].get_position()
                cbax = fig.add_axes([posn.x0 + posn.width + 0.01, posn.y0, 0.02, posn.height])
                max_val = curve_score_methods[k][1]
                label = curve_score_methods[k][0]
                sm = plt.cm.ScalarMappable(cmap=plt.cm.plasma, norm=plt.Normalize(vmin=0, vmax=max_val))
                sm._A = []
                plt.colorbar(sm, cax=cbax)#, fig=fig)
                cbax.set_ylabel(label, rotation=-90, labelpad=8)

    #max_val = m 
    #metric_name = n
    # ax[0].set_title("WT P$_{sigA}$-RFP")
    # ax[1].set_title("WT P$_{sigB}$-YFP")
    # ax[2].set_title("ΔrsbQP P$_{sigB}$-YFP")
    # ax[3].set_title("ΔrsbRU P$_{sigB}$-YFP")

    # for a in ax[1:]:
    #     a.set_ylabel("")
    # ax[0].set_ylabel("Distance from air interface (μm)")

    plt.show()
    #fig.show()
    #fig.canvas.manager.window.raise_()


if __name__ == "__main__":
    main()
