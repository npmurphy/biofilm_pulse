
import matplotlib.pyplot as plt
from figure_util import timecolor
import pandas as pd
import os.path

#%%
def get_figure(ax, basedir, dataset, xlim, species, times, kwargs):
    for time in times:
        df = pd.read_csv(os.path.join(basedir,"data/indiv_{0}_{1}_{2}.tsv".format(dataset, species, time)), sep="\t")
        file_cols = [ x for x in df.columns if "file_" in x  ]
        for fc in file_cols:
            ax.plot(df["distance"], df[fc], color=timecolor[time], **kwargs)
    return ax

#%%
    
#test_fig()

#%%
def test_fig():
    fig, ax = plt.subplots(1, 1)
    basedir = "figures/figure_sigb_10x_grad/"
    normalisation = [("unnormed", (0, 13e3)), ("gradnorm", (0, 1)) ]
    species = ["jlb021", "jlb039", "jlb088", "jlb095"]
    times = [24, 48, 72, 96]

    ylabel="YFP (AU)"
    ylabel="RFP max gradient normalized"
    norm, xlim = normalisation[0]
    spec = species[0]
    plotset = {"linewidth":0.6, "alpha":0.5}
    ax = get_figure(ax, basedir, norm, xlim, spec, times, plotset)
    ax.set_xlim(0, 150) 
    ax.set_xlabel("Distance from air interface (μm)")
    plt.show()
#%%



if __name__ == "__main__":
    test_fig()