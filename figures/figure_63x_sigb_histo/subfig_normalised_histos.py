import scipy.stats
import numpy as np
import os.path
import pandas as pd
import matplotlib.pyplot as plt
from lib import strainmap
from lib import filedb
from lib.figure_util import strain_color
strain_map, des_strain_map = strainmap.load()

def histo_slice_mean_norm(df, fileids, view_chan, norm_chan, slice_st, slice_end):
    newchan = view_chan +"_slicenorm"
    thesefiles = df[df["global_file_id"].isin(fileids)&(df["distance"]>slice_st)&(df["distance"]<=slice_end)].copy()
    thesefiles[newchan] = thesefiles[view_chan]
    file_means = thesefiles.groupby("global_file_id").mean()[norm_chan]
    for fid, mean_val in file_means.iteritems():
        mean_normed = thesefiles[thesefiles["global_file_id"]== fid][newchan].values / mean_val
        thesefiles.loc[thesefiles["global_file_id"]== fid, newchan] = mean_normed
    return thesefiles

def plot_strain_histos(ax, df, fileids, view_chan, norm_chan, slice_st, slice_end, bins, kwargs):
    newchan = view_chan +"_slicenorm"
    slice_meaned = histo_slice_mean_norm(df, fileids, view_chan, norm_chan, slice_st, slice_end)
    xbins = bins[1:] - ((bins[1]-bins[0])/2)
    print("mean", slice_meaned[newchan].mean())
    print("std", slice_meaned[newchan].std())

    print("cv scipy", scipy.stats.variation(slice_meaned[newchan]))
    print("cv man", slice_meaned[newchan].std()/slice_meaned[newchan].mean())
    print("skew man", slice_meaned[newchan].skew())
    yvals,_ = np.histogram(slice_meaned[newchan].values, bins=bins, density=True)
    ax.plot(xbins, yvals, **kwargs)
    return ax 

def plot_strain_fileindiv_histos(ax, df, fileids, view_chan, norm_chan, slice_st, slice_end, bins, kwargs):
    newchan = view_chan +"_slicenorm"
    slice_meaned = histo_slice_mean_norm(df, fileids, view_chan, norm_chan, slice_st, slice_end)
    xbins = bins[1:] - ((bins[1]-bins[0])/2)
    print("mean", slice_meaned[newchan].mean())
    print("std", slice_meaned[newchan].std())

    print("cv scipy", scipy.stats.variation(slice_meaned[newchan]))
    print("cv man", slice_meaned[newchan].std()/slice_meaned[newchan].mean())
    print("skew man", slice_meaned[newchan].skew())
    yvals,_ = np.histogram(slice_meaned[newchan].values, bins=bins, density=True)
    ax.plot(xbins, yvals, **kwargs)
    return ax 

def get_data_subset(df, file_df, list_of_histos, time, location, output_path):
    strain_dfs = [] 
    for i, (strain, look_chan, norm_chan, lookbins, slice_stend, label, color) in enumerate(list_of_histos):
        fids = file_df[(file_df["time"] == time) &
                        (file_df["location"] == location) &
                        (file_df["strain"] == des_strain_map[strain])].index
        st_df = histo_slice_mean_norm(df, fids, look_chan, norm_chan, slice_stend[0], slice_stend[1])
        strain_dfs += [ st_df ]
    alldf = pd.concat(strain_dfs) 
    alldf.to_hdf(output_path, key="cells")
    return alldf


def get_figure(cell_df, file_df, axes, time, location, list_of_histos):
    for i, (strain, look_chan, norm_chan, lookbins, slicested, label, color) in enumerate(list_of_histos):
        fids = file_df[(file_df["time"] == time) &
                        (file_df["location"] == location) &
                        (file_df["strain"] == des_strain_map[strain])].index
        opts = {"color":color, "label":label}
        print(strain)
        axes[i] = plot_strain_histos(axes[i], cell_df, fids, look_chan, norm_chan, slicested[0], slicested[1], lookbins, opts)
    return axes

def main():
    this_dir = os.path.dirname(__file__)


    basedir = "../../datasets/LSM700_63x_sigb"
    file_df = filedb.get_filedb(os.path.join(this_dir, basedir, "file_list.tsv"))
    cachedpath = os.path.join(this_dir, basedir, "histo_tops_normed.h5")
    
    generate_data_subset = False

    gchan = "green_raw_bg_mean"
    rchan = "red_raw_bg_mean"
    nbins = 100
    slice_srt_end = 5, 7 
    time = 48
    location = "center"
    gmax = 1

    gbins = np.linspace(0, gmax, nbins)

    list_of_histos = [ 
            #("2xqp_sigar_sigby",  gchan, rchan, gbins, slice_srt_end, "2xQP", strain_color["JLB095"]),
            ("wt_sigar_sigby",    gchan, rchan, gbins, slice_srt_end, "WT P$_{sigB}$-YFP", strain_color["JLB021"]),
            ("delqp_sigar_sigby", gchan, rchan, gbins, slice_srt_end, "del qp", strain_color["JLB039"]),
            ("delru_sigar_sigby", gchan, rchan, gbins, slice_srt_end, "del ru", strain_color["JLB088"])]
    
    fig, axhisto = plt.subplots( 1, 1)
    axes = [axhisto] * len(list_of_histos) #, axhisto, axhisto, axhisto]

    if generate_data_subset :
        df = pd.read_hdf(os.path.join(this_dir, basedir, "single_cell_data.h5"), "cells")
        cellsdf = get_data_subset(df, file_df, list_of_histos, time, location, cachedpath)

    else:  
        cellsdf = pd.read_hdf(cachedpath, "cells")


    axes = get_figure(cellsdf, file_df, axes, time, location, list_of_histos)
    #axes[i].set_title(label)
    axes[0].legend()
    plt.show()


if __name__ == '__main__':
    main()