from glob import glob

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

import simulation_processor
import os
#from figure_util import dpi


def get_figure(ax, timsct, title, **kwargs):

    blu_chan = "Asamp"
    grn_chan = "Bsamp"

    gs = 20
    cfpmax = 40 
    yfpmax = 40 

    kwargs = {"gridsize":gs, 
                "extent":[0, yfpmax, 0, cfpmax], 
                "norm": matplotlib.colors.LogNorm() ,
                "cmap": plt.get_cmap("plasma")
            }

    print("Cell N:", len(timsct) )
    hb = ax.hexbin(timsct[grn_chan], timsct[blu_chan], **kwargs)
    timsct["one"] = 1

    green_bins = np.linspace(0, cfpmax, 4)
    green_x = green_bins[1:] - (green_bins[1] - green_bins[0])
    cfp_trend = timsct.groupby(pd.cut(timsct[grn_chan], green_bins)).mean()
    print(timsct.groupby(pd.cut(timsct[grn_chan], green_bins)).sum()["one"].values)

    ax.plot(green_x, cfp_trend[blu_chan].values, "-o", color="k")
    ax.set_title(title)
    ax.set_xlabel("B values")
    ax.set_ylabel("A values")
    return ax
    

def main():
    this_dir = os.path.dirname(__file__)
    runf = os.path.join(this_dir, "../../../stochastic/algo/luna/final_sweeps/")
    pulse_wt_info = glob(runf + "movethresh3/bfsim_avb_qp|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0]
    #pulse_2x_info = ("Pulsing dynamics 2xQP", glob(runf + "movethresh3/bfsim_avbb_qp|*pscale_a=0.7*,pscale_b=0.5*.tsv")[0])
    #bistb_wt_info = ("Bistable WT", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=2.0*.tsv")[0]),
                     #("Bistable 2xQP", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=4.0*.tsv")[0])

    fig, ax = plt.subplots(1,1)
    pulse_wt_df = simulation_processor.get_dataset(pulse_wt_info, max_distance=140.0,  spore_time_hours=0.5)
    #pulse_2x_df = simulation_processor.get_dataset(pulse_2x_info[1], max_distance=140.0,  spore_time_hours=0.5)

    ax = get_figure(ax, pulse_wt_df, "Simulated WT")

    plt.show()


if __name__ == "__main__":
    main() 
