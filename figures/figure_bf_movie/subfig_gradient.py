
import matplotlib.pyplot as plt
from lib.figure_util import timecolor
import pandas as pd
import os.path
import lib.filedb

#%%
def get_figure_cached(ax, basedir, dataset, xlim, error, species, times, kwargs):
    if error == "sem":
        ds_tag = "indiv"
        main_line = "mean"
    elif "quartile" in error:
        ds_tag = "error"
        main_line = "median"
    else:
        ds_tag = "error"
        main_line = "mean"
    
    for time in times:
        df = pd.read_csv(os.path.join(basedir,"data/{3}_{0}_{1}_{2}.tsv".format(dataset, species, time, ds_tag)), sep="\t")
        if error == "sem":
            df["up_" + error] = df[main_line] + df[error]
            df["dn_" + error] = df[main_line] - df[error]
        ax.fill_between(df["distance"], df["up_" + error], df["dn_" + error], color=timecolor[time], **kwargs)
        ax.plot(df["distance"], df[main_line], color=timecolor[time]) # **kwargs)
    return ax

#%%
def get_figure(ax, df, file_df, chan, xlim, spec, times, plotset):
    t = 96
    for time in times:
        #print(time)
        this_time_files = file_df[file_df["time"] == time].index
        #print(this_time_files)
        this_time = df[df["file_id"].isin(this_time_files)]
        signals = this_time.groupby("cdist").mean()
        errors = this_time.groupby("cdist").sem()
        error = errors[chan]
        signal = signals[chan]
        #print(signal)
        #color = plt.cm.gist_rainbow(time/t)
        color = lib.figure_util.all_times_dict[time]
        l = ax.plot(signals.index, signal, label="{0} hours".format(time), color = color)
        l = ax.fill_between(errors.index, signal - error, signal + error, color =color, **plotset)
    return ax
    

#%%
def test_fig():
    fig, ax = plt.subplots(1, 1)

    dataset_dir = "datasets/iphox_gradient_snaps/"
    file_df = lib.filedb.get_filedb(dataset_dir + "filedb.tsv")
    df = pd.read_hdf(dataset_dir + "gradient_data_distmap.h5")
    df["g_by_r"] = df["green_bg_mean"]/df["red_bg_mean"]
    print(df.columns)
    #basedir = "figures/figure_sigb_10x_grad/"
    #basedir = "./"
    #normalisation = [("unnormed", (0, 13e3)), ("gradnorm", (0, 1)) ]
    #species = ["jlb021", "jlb039", "jlb088", "jlb095"]
    times = file_df["time"].unique()
    #times = [24, 48, 72, 96]

    ylabel="YFP (AU)"
    plotset = {"linewidth":0.6, "alpha":0.5}
    ax = get_figure(ax, df, file_df, "green_bg_mean", xlim, spec, times, plotset)
    ax.legend()
    ax.set_xlim(0, 150) 
    ax.set_xlabel("Distance from air interface (μm)")
    plt.show()
#%%



if __name__ == "__main__":
    test_fig()