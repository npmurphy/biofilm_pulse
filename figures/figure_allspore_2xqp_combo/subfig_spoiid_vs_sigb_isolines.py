import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from sklearn.isotonic import IsotonicRegression
import matplotlib.colors
import scipy.ndimage.filters as ndfilts
from lib import filedb

#plt.style.use('../figstyle.mpl')
# exploratory code is in analysis/figure_spoiid_vs_sigb_raw_cor.py

def get_figure(ax, file_df, cell_df):
    time = 48
    location = "center"
    fids = file_df[(file_df["time"] == time) & (file_df["location"] == location)].index
    #timsct = cell_df[cell_df["global_file_id"].isin(fids)]
    #red_chan = "meannorm_red"
    blu_chan = "meannorm_blue"
    grn_chan = "meannorm_green"

    #timsct = cell_df[cell_df["global_file_id"]==fid]
    timsct = cell_df[cell_df["global_file_id"].isin(fids)]

    gs = 100
    cfpmax = 11 
    yfpmax = 6 
    kwargs = {"gridsize":gs, 
                #"marginals":True, 
                "extent":[0, yfpmax, 0, cfpmax], 
                #"bins": "log"
                "norm": matplotlib.colors.LogNorm(),
                #"alpha":0.4
            }
    # ax[0].hexbin(timsct[red_chan], timsct[blu_chan], **kwargs)
    # ax[0].set_title("RFP-σA vs CFP-spoiid")
    # ax[0].set_ylabel("CFP")
    # ax[0].set_xlabel("RFP")
    # #ax[0].colorbar()
    # ax[1].set_title("RFP-σA vs YFP-σB")
    # ax[1].set_ylabel("RFP")
    # ax[1].set_xlabel("YFP")
    print("Cell N:", len(timsct) )
    d = 0.05
    x = np.arange(0, 6, d)
    y = np.arange(0, 11, d*2)
    X, Y = np.meshgrid(x, y)
    counts, Xedge, Yedge = np.histogram2d(timsct[grn_chan], timsct[blu_chan], bins =(x,y) )
    print(Xedge.shape)
    print(Yedge.shape)
    X, Y = np.meshgrid(Xedge[:-1]+(d/2), Yedge[:-1]+((d*2)/2))
    #Z = np.log10(counts.T)
    Z = (counts.T)
    Z[Z==-np.inf] = 0
    print(Z)
    #Z = counts.T
    Zg = ndfilts.gaussian_filter(Z, 1)
    #Zg = Z
    print(X.shape)
    print(counts.shape)
    hb = ax.hexbin(timsct[grn_chan], timsct[blu_chan], vmin=1, vmax=1000, **kwargs)
    #hb = ax.pcolormesh(X, Y, Zg)#, alpha=0.4)
    import matplotlib.patheffects as pe
    #from matplotlib.patheffects import PathEffects
    CS = ax.contour(X, Y, Zg, norm=matplotlib.colors.LogNorm(), vmin=1, vmax=1000, levels=[2, 10, 100, 1000])
    #, lw=2, path_effects=[pe.Stroke(linewidth=10, foreground='black'), pe.Normal()])
    plt.setp(CS.collections, path_effects=[pe.withStroke(linewidth=5, foreground="black")])
    #ax.set_title("vs PsigB-YFP")
    ax.set_xlabel("Mean normalised P$_{sigB}$-YFP")
    ax.set_ylabel("Mean normalised P$_{spoIID}$-CFP")

    # This didnt work as intended
    # I want some sort of line that separates the cells from non cells
    # regression = IsotonicRegression(increasing=False)
    # regression.fit_transform(timsct[grn_chan], timsct[blu_chan])
    # yfp_vals = np.linspace(0, yfpmax, 100)
    # cfp_pred = regression.predict(yfp_vals)
    # ax.plot(yfp_vals, cfp_pred)

    #fig.suptitle(file_df[file_df.index==fid].name.values[0])
    # ax.set_xlim(0, yfpmax)
    # ax.set_ylim(0, cfpmax)
    return ax, hb, CS


def main():
    basedir = "../../datasets/biofilm_cryoslice/LSM780_63x_spoiid_v_sigb/"
    file_df = filedb.get_filedb(os.path.join(basedir, "filedb.tsv"))
    cell_df = pd.read_hdf(basedir + "rsiga_ysigb_cspoiid_redoedgedata.h5", "cells")

    # Ignore first 2 um 
    cell_df = cell_df[cell_df.distance > 2].copy()

    # # Remove central ridge from two images (48 hours center)
    # lookfiles = [(2, 2600), (3, 1400)]
    # for fid, cut in lookfiles:
    #     cell_df = cell_df[~((cell_df["global_file_id"]==fid) & (cell_df["image_col"] > cut))]
    
    # 33 is where the sigB gradient crosses spoiid strong and 
    # 7 is the gradient peak is 
    #cell_df = cell_df[(cell_df["distance"] < 33) & (cell_df["distance"]> 7)]

    fig, ax = plt.subplots(1,1)
    ax, hb, contour =  get_figure(ax, file_df, cell_df)
    cbar = fig.colorbar(hb)
    cbar.add_lines(contour)
    #cax.hlines(0.5, 0, 1, colors = 'r', linewidth = 10, linestyles = ':')
    plt.show()


if __name__ == "__main__":
    main()