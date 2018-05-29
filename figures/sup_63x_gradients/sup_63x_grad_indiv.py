
import pandas as pd
import numpy as np
import os.path
import filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from glob import glob
import subfig_plot_indiv 


import lib.figure_util as figure_util
from figure_util import dpi
figure_util.apply_style()

def main():
    fig, all_axes = plt.subplots(2, 4)
    all_axes = np.atleast_2d(all_axes)

    normalisation = [("unnormed", (0, 13e3), "Unormalised YFP (AU)"), 
                     ("gradnorm", (0, 1), "RFP max gradient normalized") ]
    species = ["jlb021", "jlb039", "jlb088", "jlb095"]
    times = [24, 48, 72, 96]
    #basedir = "figures/figure_sigb_10x_grad/"
    basedir = "./"

    plotset = {"linewidth":0.5, "alpha":0.3}
    for n, (norm, ylim, ylabel) in enumerate(normalisation):
        for s, spec in enumerate(species):
            args = (all_axes[n,s], basedir, norm, ylim, spec, times, plotset)
            all_axes[n, s] = subfig_plot_indiv.get_figure(*args)
            all_axes[n, s].set_xlim(0, 150) 
            all_axes[n, s].set_ylim(*ylim)
            all_axes[n, s].set_ylabel(ylabel)
            all_axes[n, s].set_title(figure_util.strain_label[spec.upper()])
            all_axes[n, s].set_xlabel("Distance from air interface (μm)")


    filename = "sup_63x_grad_indiv"
    width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.4 )
    #fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.06, hspace=0.25, wspace=0.25)
    fig.set_size_inches(width, height)# common.cm2inch(width, height))
    fig.tight_layout()
    print("request size : ", figure_util.inch2cm((width, height)))
    fig.savefig(filename + ".pdf", dpi=dpi) #, bbox_inches="tight"  )
    fig.savefig(filename + ".png", dpi=dpi) #, bbox_inches="tight"  )
    figure_util.print_pdf_size(filename + ".pdf")


if __name__ == "__main__":
    main()
