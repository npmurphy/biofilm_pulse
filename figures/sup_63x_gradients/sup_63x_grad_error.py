
#import pandas as pd
import numpy as np
import os.path
#from lib import filedb
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
#from glob import glob
import subfig_plot_grad_errors 

import lib.figure_util as figure_util
figure_util.apply_style()
#from lib.figure_util import dpi
from lib.figure_util import timecolor
# std, sem, quartile . 

def make_figure(error):
    fig, all_axes = plt.subplots(2, 4)
    all_axes = np.atleast_2d(all_axes)
    # normalisation = [("unnormed", (0, 11e3), "Unormalised YFP (AU)"), 
    #                  ("maxnorm", (0, 1.5), "RFP max gradient normalized"),
    #                  ("meannorm", (0, 3), "Mean normalized") ]

    normalisation = [("unnormed", (0, 8e3), "P$_{sigB}$-YFP (AU)"), 
                     ("ratio", (0, 1), "YFP/RFP Ratio")]
    species = ["jlb021", "jlb039", "jlb088", "jlb095"]
    times = [24, 48, 72, 96]
    #basedir = "figures/figure_sigb_10x_grad/"
    this_dir = os.path.join(os.path.dirname(__file__))
    base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/gradients")
    # alldf = pd.read_hdf(os.path.join(base, "single_cell_data.h5"))
    #files = filedb.get_filedb(os.path.join(base, "file_list.tsv"))

    plotset = {"linewidth":0.5, "alpha":0.3}
    for n, (norm, ylim, ylabel) in enumerate(normalisation):
        for s, spec in enumerate(species):
            args = (all_axes[n,s], base, norm, ylim, error, spec, times, plotset)
            all_axes[n, s] = subfig_plot_grad_errors.get_figure(*args)
            all_axes[n, s].set_xlim(0, 150) 
            all_axes[n, s].set_ylim(*ylim)
            all_axes[n, s].set_ylabel(ylabel)
            all_axes[n, s].set_title(figure_util.strain_label[spec.upper()])
            all_axes[n, s].set_xlabel("Distance from air interface (μm)")

    #Create legend from custom artist/label lists
    artist = [ plt.Line2D((0,1),(0,0), color=timecolor[t]) for t in times]
    labels = [ "{0} hours".format(t) for t in times]
    all_axes[0, 2].legend(artist, labels)


    for a, l in zip(all_axes.flatten(), figure_util.letters):
        a.annotate(l, xy=(0,0),
                    xytext=(-0.31, 1.05),  
                    textcoords='axes fraction',
                    #arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=figure_util.letter_font_size, color="black"
                    )

    filename = "sup_63x_grad_error_{0}".format(error)
    width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.4 )
    fig.set_size_inches(width, height)
    fig.tight_layout()
    figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)



if __name__ == "__main__":
    #make_figure("sem")
    #make_figure("std")
    make_figure("quantile75")
    
    #make_figure("none")
