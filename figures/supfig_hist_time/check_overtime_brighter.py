import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib import figure_util, filedb
from lib.analysis.sliding_windows import sliding_window_distribution
from lib.figure_util import timecolor

figure_util.apply_style()
# In[16]:

def get_density_mass(files, alldf, time, chan, bins, st_stp, strain="jlb021"):
    looking = files[(files["time"]==time) & (files["location"]=="center") & (files["strain"]==strain)]
    these_cells = alldf[alldf["global_file_id"].isin(looking.index)]
    strt, stop = st_stp
    inzone = these_cells[(these_cells["distance"] > strt) & (these_cells["distance"] <= stop)]
    n = len(inzone)
    vals, bins = np.histogram(inzone[chan], bins=bins)   # not using density, but dividing by n. 
    xbins = bins[:-1] + (bins[1] - bins[0])/2
    return xbins, vals/n



# In[23]:
def make_figure():
    this_dir = os.path.dirname(__file__)
    base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/")
    alldf = pd.read_hdf(os.path.join(base, "single_cell_data.h5"))
    files = filedb.get_filedb(os.path.join(base, "file_list.tsv"))

    alldf["ratio"] = alldf["green_raw_bg_mean"]/alldf["red_raw_bg_mean"]
    strains = ["jlb021",  "jlb039", "jlb088", "jlb095"]

    chans = [#("green_raw_bg_meannorm", "meanorm", np.linspace(0,6.5, 150), (0,5), "Mean Normalised flourecence"), 
             #("green_raw_bg_mean", "unnorm", np.linspace(0,10000, 150), (0,7), "Raw flourecence"), 
             ("ratio", "ratio",  np.linspace(0, 1.3, 150), (0, 15), "YFP/RFP"), 
             ]

    #         ("green_bg_maxnorm", "gradnorm", np.linspace(0,1.50, 50),(0, 0.5),  "RFP max gradient normalised"),
    #chans = [("green_raw_bg_meannorm", "meanorm", np.linspace(0,6.5, 150), (0,5), "Mean Normalised flourecence")]
    #chans = [("green_raw_bg_mean", "unnorm", np.linspace(0,10000, 150), (0,7), "Mean Normalised flourecence")]
    times = [ 24,  48,  72,  96]
    for c, (chan, fname, bins, ylim, title) in enumerate(chans):
        fig, ax = plt.subplots(2,4)
        for s, strain in enumerate(strains):
            name = figure_util.strain_label[strain.upper()]
            for t, time in enumerate(times):
                xbins, vals = get_density_mass(files, alldf, time, chan, bins, (2,20), strain=strain)
                ax[0, s].plot(xbins, vals*100, linewidth=1.0, alpha=1.0, label="{0:d} hours".format(int(time)), color=timecolor[time])
                ax[0, s].set_title(name + "\n Top of biofilm (2-20um)")
                ax[1, s].set_title("Bottom of biofilm (60-100um)")
                ax[0, s].set_ylabel("% of cells")
                ax[0, s].set_ylim(*ylim)
                ax[1, s].set_ylim(*ylim)
                ax[0, s].set_xlabel(title)
                ax[1, s].set_xlabel(title)
                ax[0, s].set_xlim(0, 1.0)

                ax[1, s].set_xlim(0, 1.0)
                xbins, vals = get_density_mass(files, alldf, time, chan, bins, (60,100), strain=strain)
                ax[1, s].plot(xbins, vals*100, linewidth=1.0, alpha=1.0, label="{0:d} hours".format(int(time)), color=timecolor[time])
                ax[1, s].set_ylabel("% of cells")
    
        artist = [ plt.Line2D((0,1),(0,0), color=timecolor[t]) for t in times]
        labels = [ "{0} hours".format(t) for t in times]
        ax[0, 0].legend(artist, labels)

        width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.4 )
        filename = "supfig_histo_time_{0}".format(fname)
        fig.set_size_inches(width, height)
        fig.tight_layout()
        figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
        fig.clear()



if __name__ == '__main__':
    make_figure()
