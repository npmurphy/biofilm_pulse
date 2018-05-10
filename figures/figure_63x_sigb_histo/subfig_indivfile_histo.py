import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
import scipy.io
from lib.analysis.sigb_histograms import make_indivfile_histogram
import lib.figure_util as figure_util
figure_util.apply_style()

def make_cached_data(df, column, inbins, slice_info, dset, percentile, basedir="."):
    bins = np.linspace(*inbins)
    histo_res = make_indivfile_histogram(df,
                                         column,
                                         bins,
                                         slice_info,
                                         percentages=True,
                                         percentile=percentile,
                                         print_out_stats=True)
    names = "cbins", "indiv_hists", "mean_indiv", "histo_all", "uniques", "n", "stats"
    save = { k: v for (k, v) in zip(names, histo_res)} 
    datadir = os.path.join(basedir, "data")
    try: 
        os.mkdir(datadir)
    except FileExistsError as e:
        pass
    path = os.path.join(datadir, "{column}_{inbins}_{slice_info}_{percentile}_{dset}.mat".format(**locals()))
    scipy.io.savemat(path, save)
    return save


def get_cached_data(column, inbins, slice_info, dset, percentile, basedir="."):
    path = os.path.join(basedir, "data/{column}_{inbins}_{slice_info}_{percentile}_{dset}.mat".format(**locals()))
    save = scipy.io.loadmat(path)
    if save is None:
        raise FileNotFoundError("couldnt find file: " + path)
    return save


def get_figure(ax, df, column, inbins, slice_info, dset, percentile, use_cache, basedir=".", kwargs={}):
    
    # histo_res = make_indivfile_histogram(df, column, inbins, slice_info, 
    #                 percentages=True, percentile=percentile, print_out_stats=True)
    # cbins, indiv_hists, mean_indiv, histo_all, uniques, n, stats
    if use_cache:
        save = get_cached_data(column, inbins, slice_info, dset, percentile, basedir)
        (meanval, std, mskewval, pskewval, modeval, cvval) = save["stats"].flatten()
    else:
        save = make_cached_data(df, column, inbins, slice_info, dset, percentile, basedir)
        (meanval, std, mskewval, pskewval, modeval, cvval) = save["stats"]
    cbins = save["cbins"].flatten()
    indiv_hists = save["indiv_hists"]
    histo_all = save["histo_all"].flatten()

    if "max_min" not in kwargs:
        kwargs["max_min"] = "indiv"
    if kwargs["min_max"] == "std":
        min_stdiv = histo_all - np.std(indiv_hists, axis=0)
        max_stdiv = histo_all + np.std(indiv_hists, axis=0)
        ax.fill_between(cbins, max_stdiv, min_stdiv, color=kwargs["color"], alpha=0.3)
    elif kwargs["max_min"] == "color":
        min_extents = np.min(indiv_hists, axis=0)
        max_extents = np.max(indiv_hists, axis=0)
        ax.fill_between(cbins, max_extents, min_extents, color=kwargs["color"], alpha=0.3)
    elif kwargs["max_min"] == "indiv":
        for i in range(indiv_hists.shape[0]):
            ax.plot(cbins, indiv_hists[i, :], color="gray", alpha=0.3)
    else:
        pass

    if "mode_mean" in kwargs and kwargs["mode_mean"] is False:
        model, meanl = None, None
    else:
        model = ax.axvline(modeval, color=figure_util.mode_color, label="Mode", linewidth=1.0, linestyle=":") 
        meanl =  ax.axvline(meanval, color=figure_util.mean_color, label="Mean", linewidth=1.0, linestyle="-.") 
    line, = ax.plot(cbins, histo_all, color=kwargs["color"])
    ax.locator_params(axis='x', nbins=4)
    #ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, steps=[0, 3, 6, 9]))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, integer=True))
    return ax, line, (model, meanl)
