
import matplotlib.pyplot as plt
from lib.figure_util import timecolor
import pandas as pd
import os.path

#%%
def get_figure(ax, basedir, dataset, xlim, error, species, times, kwargs):
    if error == "sem":
        ds_tag = "indiv"
        main_line = "mean"
    elif "quartile" in error:
        ds_tag = "error"
        main_line = "median"
    else:
        ds_tag = "error"
        main_line = "mean"

    fb_kw = {k:v for k, v in kwargs.items() if k not in ["label"]}
    pl_kw = {k:v for k, v in kwargs.items() if k not in ["alpha"]}
            
    for time in times:
        df = pd.read_csv(os.path.join(basedir,"{3}_{0}_{1}_{2}.tsv".format(dataset, species, time, ds_tag)), sep="\t")
        df = df[df["distance"] > 2]
        if "color" not in kwargs:
            fb_kw["color"]=timecolor[time]
            pl_kw["color"]=timecolor[time]
        if error == "sem":
            df["up_" + error] = df[main_line] + df[error]
            df["dn_" + error] = df[main_line] - df[error]
            ax.fill_between(df["distance"], df["up_" + error], df["dn_" + error], **fb_kw)
        ax.plot(df["distance"], df[main_line], **pl_kw) # **kwargs)
    return ax

#%%
    
#test_fig()

#%%
def test_fig():
    fig, ax = plt.subplots(1, 1)
    #basedir = "figures/figure_sigb_10x_grad/"
    basedir = "./"
    normalisation = [("unnormed", (0, 13e3)), ("gradnorm", (0, 1)) ]
    species = ["jlb021", "jlb039", "jlb088", "jlb095"]
    times = [24, 48, 72, 96]

    #xlabel="YFP (AU)" ylabel="RFP max gradient normalized"
    norm, xlim = normalisation[0]
    spec = species[0]
    plotset = {"linewidth":0.6, "alpha":0.5}
    error = "sem"
    ax = get_figure(ax, basedir, norm, xlim, error, spec, times, plotset)
    ax.set_xlim(0, 150) 
    ax.set_xlabel("Distance from air interface (μm)")
    plt.show()
#%%



if __name__ == "__main__":
    test_fig()