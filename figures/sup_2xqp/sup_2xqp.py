import os.path
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs

# import subfig_dist_joy
from lib import filedb

# import os.path
import scipy.stats
import numpy as np
import pandas as pd
from lib import strainmap

import os.path
from lib import figure_util

figure_util.apply_style()


# import matplotlib.gridspec as gridspec
from figures.sup_63x_gradients import subfig_plot_grad_errors
from figures.figure_63x_sigb_histo import joy_plots_of_gradients

figure_util.apply_style()
from lib.figure_util import timecolor


def main():
    # fig = plt.figure()
    # grid = gs.GridSpec(1, 3, width_ratios=[1,1,1])#, height_ratios=[1.0, 0.8])
    # joy_gs  = gs.GridSpecFromSubplotSpec(1, 2,
    #                                 width_ratios=[1,1],
    #                                 subplot_spec = grid[0,1:],
    #                                 wspace=0.3)
    fig, ax = plt.subplots(1, 3)

    # all_axes = plt.subplot(grid[0])
    all_axes = ax[0]
    ax1 = ax[1]
    ax2 = ax[2]
    ax1.get_shared_x_axes().join(ax1, ax2)

    # ax1 = fig.add_subplot(joy_gs[0])
    # ax2 = fig.add_subplot(joy_gs[1], sharey=ax1)
    ax = np.array([[ax1], [ax2]])

    error = "quantile75"
    normalisation = [  # ("unnormed", (0, 8e3), "P$_{sigB}$-YFP (AU)"),
        ("ratio", (0, 1), "YFP/RFP Ratio")
    ]
    species = ["jlb095"]
    times = [24, 48, 72, 96]
    # basedir = "figures/figure_sigb_10x_grad/"
    this_dir = os.path.join(os.path.dirname(__file__))
    base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/gradients")
    # alldf = pd.read_hdf(os.path.join(base, "single_cell_data.h5"))
    # files = filedb.get_filedb(os.path.join(base, "file_list.tsv"))

    plotset = {"linewidth": 1}  # "alpha":0.3}
    (norm, ylim, ylabel) = normalisation[0]
    for s, spec in enumerate(species):
        args = (all_axes, base, norm, ylim, error, spec, times, plotset)
        all_axes = subfig_plot_grad_errors.get_figure(*args)
        all_axes.set_xlim(0, 150)
        all_axes.set_ylim(*ylim)
        all_axes.set_ylabel(ylabel)
        # all_axes.set_title(figure_util.strain_label[spec.upper()])
        all_axes.set_xlabel("Distance from top of biofilm (μm)")

    # Create legend from custom artist/label lists
    artist = [plt.Line2D((0, 1), (0, 0), color=timecolor[t]) for t in times]
    labels = ["{0} hours".format(t) for t in times]
    all_axes.legend(artist, labels)

    ################
    ## Joy plot

    curve_score_methods = {
        "mean": ("Mean", (0.0, 4.0), lambda d, h, b: np.mean(d)),
        "cv": (
            "Coefficient of variation",
            (0.3, 0.8),
            lambda d, h, b: scipy.stats.variation(d),
        ),
        "skew_normed": (
            "Skew",
            (0.0, 2.9),
            lambda d, h, b: scipy.stats.skew(d, bias=False),
        ),
    }

    plot_colors = [  # "mean",
        # "std",
        "cv",
        "skew_normed",  # same as pandas
    ]

    #this_dir = "/media/nmurphy/BF_Data_Orange/"
    #basedir = os.path.join(this_dir, "datasets/LSM700_63x_sigb")
    basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb")
    cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
    cell_df = cell_df[cell_df["distance"] > 2]
    time = 48  # .0
    location = "center"
    file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
    strain_map, des_strain_map = strainmap.load()

    percentile = 0
    # green_chan = "meannorm_green"
    # red_chan = "meannorm_red"
    rmax = 6.5
    gmax = 6.5  # 0.4
    green_chan = "green_raw_bg_mean"
    red_chan = "red_raw_bg_mean"
    rmax = 50000
    gmax = 10000
    strains = [  # ("wt_sigar_sigby", red_chan, rmax, "WT\n P$_{sigA}$-RFP"),
        # ("wt_sigar_sigby", green_chan,    gmax,  "WT\n P$_{sigB}$-YFP"),
        # ("delqp_sigar_sigby", green_chan, gmax,  "ΔrsbQP\n P$_{sigB}$-YFP"),
        # ("delru_sigar_sigby", green_chan, gmax,  "ΔrsbRU\n P$_{sigB}$-YFP")]
        ("2xqp_sigar_sigby", green_chan, gmax, "2$\\times$rsbQP\n P$_{sigB}$-YFP")
    ]

    # fig, ax = plt.subplots(len(plot_colors), len(strains),  sharey=True)
    for c, (strain, chan, max_val, name) in enumerate(strains):
        strain_num = des_strain_map[strain]
        distances, sbins, histograms, stats = joy_plots_of_gradients.get_strain_result(
            file_df,
            cell_df,
            time,
            location,
            strain_num,
            chan,
            max_val,
            percentile,
            curve_score_methods,
        )
        for r, k in enumerate(plot_colors):
            color = figure_util.strain_color[strain_num.upper()]
            ax[r, c], mv, leglist = joy_plots_of_gradients.plot_curves(
                ax[r, c], color, distances, sbins, histograms, stats, k
            )

            if c == len(strains) - 1:
                posn = ax[r, c].get_position()
                cbax = fig.add_axes(
                    [posn.x0 + posn.width + 0.0005, posn.y0, 0.015, posn.height]
                )
                label = curve_score_methods[k][0]
                min_zval = curve_score_methods[k][1][0]
                max_zval = curve_score_methods[k][1][1]
                sm = plt.cm.ScalarMappable(
                    cmap=plt.get_cmap("viridis"),
                    norm=plt.Normalize(vmin=min_zval, vmax=max_zval),
                )
                sm._A = []
                _ = plt.colorbar(sm, cax=cbax)  # , fig=fig)
                cbax.set_ylabel(label, rotation=-90, labelpad=8)
                cbax.tick_params(direction="out")

            # if r == 0:
            # ax[r,c].set_title(name, fontsize=6)

            ax[r, c].set_xlim(0, max_val)
    ax2.get_yaxis().set_ticklabels([])
    leg = ax[0, -1].legend(
        leglist, ["Mode", "Mean"], loc="lower left", bbox_to_anchor=(0.84, 0.97)
    )
    leg.set_zorder(400)

    for a in ax.flatten():
        a.tick_params(direction="out")
    ax1.set_ylabel("Distance from biofilm top (μm)")
    ax1.set_xlabel("Normalized fluorescence")
    ax2.set_xlabel("Normalized fluorescence")
    # xy=(0,0),
    # xytext=(0.5, 0.04),
    # textcoords='figure fraction',
    # #arrowprops=dict(facecolor='black', shrink=0.05),
    # horizontalalignment='center', verticalalignment='center',
    # fontsize="medium", color=mpl.rcParams['axes.labelcolor']
    # )

    for a, l in zip([all_axes, ax1, ax2], figure_util.letters):
        a.annotate(
            l,
            xy=(0, 0),
            xytext=(-0.27, 1.05),
            textcoords="axes fraction",
            # arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment="center",
            verticalalignment="top",
            fontsize=figure_util.letter_font_size,
            color="black",
        )

    filename = "sup_2xQP_prog"
    width, height = figure_util.get_figsize(
        figure_util.fig_width_big_pt, wf=1.0, hf=0.4
    )
    fig.set_size_inches(width, height)
    # fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.17, wspace=0.4)
    fig.tight_layout()
    figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)


if __name__ == "__main__":
    main()

