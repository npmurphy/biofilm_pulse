import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
import matplotlib.colors
import lib.filedb as filedb

import scipy.stats

# plt.style.use('../figstyle.mpl')
# exploratory code is in analysis/figure_spoiid_vs_sigb_raw_cor.py


def plot_regression(x, y, ax=None, **kwargs):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    nx = np.linspace(x.min(), x.max(), 100)
    print(nx)
    print(intercept + slope * nx)
    if slope < 0:
        space = " "
    else:
        space = ""
    #label_str = "R$^2$:      {2}{0:0.03f}\nSlope: {1:0.03f}"
    label_str = "Slope: {1:0.03f}"
    if ax is not None:
        ax.plot(
            nx,
            intercept + slope * nx,
            label=label_str.format(r_value ** 2, slope, space),
            **kwargs
        )
    return ax


def get_figure(ax, file_df, cell_df):
    time = 48
    location = "center"
    fids = file_df[(file_df["time"] == time) & (file_df["location"] == location)].index
    print(fids)
    # timsct = cell_df[cell_df["global_file_id"].isin(fids)]
    red_chan = "meannorm_red"
    blu_chan = "meannorm_blue"
    grn_chan = "meannorm_green"

    # timsct = cell_df[cell_df["global_file_id"]==fid]
    timsct = cell_df[cell_df["global_file_id"].isin(fids)]

    gs = 100
    cfpmax = 11
    yfpmax = 4
    kwargs = {
        "gridsize": gs,
        # "marginals":True,
        "extent": [0, yfpmax, 0, cfpmax],
        # "bins": "log"
        "norm": matplotlib.colors.LogNorm(),
        "cmap": plt.get_cmap("plasma"),
    }

    green_bins = np.linspace(0.5, yfpmax, 11)
    green_x = green_bins[1:] - (green_bins[1] - green_bins[0])
    cfp_trend = timsct.groupby(pd.cut(timsct[grn_chan], green_bins)).mean()
    print(timsct.groupby(pd.cut(timsct[grn_chan], green_bins)).count()[grn_chan].values)
    print("Cell N:", len(timsct))
    hb = ax.hexbin(timsct[grn_chan], timsct[blu_chan], **kwargs)
    ax = plot_regression(
        timsct[grn_chan], timsct[blu_chan], ax=ax, color="black", linewidth=1
    )
    ax.legend()
    # ax.plot(green_x, cfp_trend[blu_chan].values, marker=".", linestyle="-", color="black")

    # ax.set_title("vs PsigB-YFP")

    # This didnt work as intended
    # I want some sort of line that separates the cells from non cells
    # regression = IsotonicRegression(increasing=False)
    # regression.fit_transform(timsct[grn_chan], timsct[blu_chan])
    # yfp_vals = np.linspace(0, yfpmax, 100)
    # cfp_pred = regression.predict(yfp_vals)
    # ax.plot(yfp_vals, cfp_pred)

    # fig.suptitle(file_df[file_df.index==fid].name.values[0])
    ax.set_xlim(0, yfpmax)
    ax.set_ylim(0, cfpmax)
    return ax, hb


def main():
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/LSM780_63x_spoiid_v_sigb/")
    file_df = filedb.get_filedb(os.path.join(basedir, "filedb.tsv"))
    print(file_df)
    cell_df = pd.read_hdf(basedir + "rsiga_ysigb_cspoiid_redoedgedata.h5", "cells")

    # Ignore first 2 um
    cell_df = cell_df[cell_df.distance > 2].copy()

    fig, ax = plt.subplots(1, 1)
    ax, hb = get_figure(ax, file_df, cell_df)
    fig.colorbar(hb)
    plt.show()


if __name__ == "__main__":
    main()
