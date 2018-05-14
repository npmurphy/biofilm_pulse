import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io

import figure_util
import filedb

plt.style.use('../figstyle.mpl')

# Some images had little tiny regions at the end with <10 cell spores in them 
# that produced huges spikes of 100% spores etc. 
# to ignore this we are using 100 as a minimum sample size. 
# 10 does the job, 500, 100 look good at the top but introduce more artifacts later. 
# 100 is just a big enough number. 

def get_figure(ax, cache_path, sspb_strains):
    spore_data = scipy.io.loadmat(cache_path)
    print(spore_data.keys())
    #distance = 0
    #mean_count = 1
    #std_count = 2
    #sem_count = 3
    #total_count = 3
    for strain, name in sspb_strains:
        def g(val):
            return spore_data[strain + "_" + val].flatten()
        color = figure_util.strain_color[strain]
        ax.plot(g("dists"), g("sporeratio_mean"), color=color, label=name) 
        ax.fill_between(g("dists"),
                        g("sporeratio_mean") - g("sporeratio_sem"), 
                        g("sporeratio_mean") + g("sporeratio_sem"),  
                         color=color, alpha=0.3)

    ax.set_xlim(0, g("dists").max())
    ax.set_ylim(bottom=0)
    #ax.legend()
    ax.set_xlabel("Distance from air interface (μm)")
    ax.set_ylabel("Proportion of cells that are spores")
    return ax


def main():
    sspb_strains = [('JLB077', "WT",   ),
                    ('JLB117', "2×rsbQP",)]
    fig_main, ax = plt.subplots(1,1, sharex=True)
    ax = get_figure(ax, "spore_plot_cache.mat", sspb_strains)
    plt.show()


if __name__ == "__main__":
    main()
