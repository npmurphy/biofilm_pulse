import re
from glob import glob

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib import gridspec

import figure_util
import simulation_processor
from figure_util import dpi

plt.style.use('../figstyle.mpl')


def plot_spore(ax, biofilm_df, **kwargs):
    grped = biofilm_df.groupby("dist")
    num_sims = len(biofilm_df.sim_id.unique())
    #print("Max spore", np.max(((grped["spore"]).apply(np.count_nonzero))/num_sims))
    spore_prcnt = grped["spore"].sum() / num_sims 
    line = ax.plot(grped["dist"].median(), spore_prcnt, **kwargs)
    # ax.fill_between(grped["dist"].median(),
    #                 grped["Bsamp"].mean() - grped["Bsamp"].sem(),
    #                 grped["Bsamp"].mean() + grped["Bsamp"].sem(), alpha=0.4, **kwargs)
    return ax, line


def get_figure(ax, wt_df, x2_df, **kwargs):
    ax, wtp = plot_spore(ax, wt_df, color=figure_util.strain_color["JLB077"], label="WT")
    ax, x2p = plot_spore(ax, x2_df, color=figure_util.strain_color["JLB117"], label="2xQP")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.legend()
    return ax, [wtp, x2p]
    

def main():
    runf = "../../algo/luna/final_sweeps/"
    pulse_wt_info = ("Pulsing dynamics WT", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0])
    pulse_2x_info = ("Pulsing dynamics 2xQP", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.5*.tsv")[0])
    #bistb_wt_info = ("Bistable WT", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=2.0*.tsv")[0]),
            #("Bistable 2xQP", glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=4.0*.tsv")[0])

    fig, ax = plt.subplots(1,1)
    pulse_wt_df = simulation_processor.get_dataset(pulse_wt_info[1], max_distance=140.0,  spore_time_hours=0.5)
    pulse_2x_df = simulation_processor.get_dataset(pulse_2x_info[1], max_distance=140.0,  spore_time_hours=0.5)

    ax, sbplots = get_figure(ax, pulse_wt_df, pulse_2x_df)

    plt.show()


if __name__ == "__main__":
    main() 