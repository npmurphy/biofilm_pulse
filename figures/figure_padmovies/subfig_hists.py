import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from lib import figure_util

def get_statistics(df, chan):
    
    means = df.groupby("Number").mean()[chan]
    print(means)
    print("STD", means.std())

def get_figure(ax, df, chan, bins, hstyle):
    print(chan)
    df = df.dropna()
    get_statistics(df, chan)
    xbins = bins[1:] - ((bins[1] - bins[0])/2)

    ycounts, xpos = np.histogram(df[chan].values, bins=bins)
    yvals = (ycounts/len(df)) * 100
    print(np.sum(yvals))
    ax.bar(xbins, yvals, **hstyle)
    return ax


def main():
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/padmovies_brightfield/hists/")
    bin_width = 10
    nbins = np.arange(-10, 240, bin_width)
    strains = [ ("wt",    "MR", "JLB021", 280, nbins),
                ("wt",    "MY", "JLB021", 200, nbins),
                ("delru", "MY", "JLB088", 200, nbins),
                ("delqp", "MY", "JLB039", 200, nbins)]    
    fig, ax = plt.subplots(len(strains), 1)
    ax = np.atleast_1d(ax)

    # bg_style= {"linewidth":0.5, "alpha":0.4, "color":"gray", "label":'_nolegend_'}

    for i, (filen, chan, strainnum, xmax, bins) in enumerate(strains):
        df = pd.read_csv(os.path.join(basedir, filen + ".tsv"), sep="\t", )
        h_style= {"width": ((nbins[1] - nbins[0]) ) * 0.8,
                  "alpha":1.0,
                  "color":figure_util.strain_color[strainnum]}
        #hlcells= [47 , 70 , 105 , 106 , 137]
        ax[i] = get_figure(ax[i], df, chan, bins, h_style )
        ax[i].set_ylim(0,32)
        ax[i].set_xlim(-10,xmax)
        #ax[i].legend()
    plt.show()


if __name__ == '__main__':
    main()