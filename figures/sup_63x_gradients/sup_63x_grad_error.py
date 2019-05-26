
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
    fig, shape_axes = plt.subplots(2, 2)
    #all_axes = np.atleast_2d(all_axes)
    all_axes = np.atleast_2d(shape_axes.flatten())
    # normalisation
    #  = [("unnormed", (0, 11e3), "Unormalised YFP (AU)"), 
    #                  ("maxnorm", (0, 1.5), "RFP max gradient normalized"),
    #                  ("meannorm", (0, 3), "Mean normalized") ]

    normalisation = [#("unnormed", (0, 8e3), "P$_{sigB}$-YFP (AU)"), 
                     ("ratio", (0, 1), "YFP/RFP Ratio")]
    species = ["jlb021",  "jlb088","jlb039"] #, "jlb095"]
    times = [24, 48, 72, 96]
    #basedir = "figures/figure_sigb_10x_grad/"
    this_dir = os.path.join(os.path.dirname(__file__))
    base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/gradients")
    # alldf = pd.read_hdf(os.path.join(base, "single_cell_data.h5"))
    #files = filedb.get_filedb(os.path.join(base, "file_list.tsv"))

    ypos = 0.9
    ypos_l=0.5
    xpos_ll = -0.27
    xpos_t = 0.5

    plotset = {"linewidth":1, } #"alpha":0.3}
    for n, (norm, ylim, ylabel) in enumerate(normalisation):
        for s, spec in enumerate(species):
            args = (all_axes[n,s], base, norm, ylim, error, spec, times, plotset)
            all_axes[n, s] = subfig_plot_grad_errors.get_figure(*args)
            all_axes[n, s].set_xlim(0, 150) 
            all_axes[n, s].set_ylim(*ylim)

            all_axes[n, s].set_ylabel(ylabel, ha="center", va="center")
            all_axes[n,s].get_yaxis().set_label_coords(xpos_ll, ypos_l)

            all_axes[n, s].set_xlabel("Distance from top of biofilm (μm)")
            text = all_axes[n, s].set_title(figure_util.strain_label[spec.upper()],
                                            fontdict={"va":"baseline", "ha":"center"},
                                            transform=all_axes[n,s].transAxes,
                                            position=(xpos_t, ypos))
            #text.position = (xpos_t, ypos)
            # tit = all_axes[n, s].text(figure_util.strain_label[spec.upper()],
            #                           xpos_t, ypos,
            #                           va="top", ha="center", 
            #                           transform=all_axes[n,s].transAxes)
                
            print(n, s)
            print(text.get_fontproperties())
            #print(all_axes[n,s].get_yaxis().get_label_coords())


    #Create legend from custom artist/label lists
    artist = [ plt.Line2D((0,1),(0,0), color=timecolor[t]) for t in times]
    labels = [ "{0} hours".format(t) for t in times]
    shape_axes[1, 1].legend(artist, labels, loc="center")
    #shape_axes[1,1], leg = figure_util.shift_legend(shape_axes[1,1], leg,  0, -2.0) 


    for a, l in zip(all_axes.flatten()[:3], figure_util.letters):
        a.annotate(l, xy=(0,0),
                    xytext=(xpos_ll, ypos),  
                    textcoords='axes fraction',
                    #arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='baseline',
                    fontsize=figure_util.letter_font_size, color="black"
                    )

    all_axes[-1,-1].set_axis_off()

    filename = "sup_63x_grad_error_{0}".format(error)
    width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.8 )
    fig.set_size_inches(width, height)
    fig.subplots_adjust(left=0.12, bottom=0.1, top=0.97, right=0.97,
                        wspace=0.4, hspace=0.4)
    #fig.tight_layout()
    figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)



if __name__ == "__main__":
    #make_figure("sem")
    #make_figure("std")
    make_figure("quantile75")
    
    #make_figure("none")
