import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from lib import figure_util

def get_figure(ax, df, chan, chosen_traces, frames_include, bg_style, ch_style):
    max_frame = df["frames"].max()
    start_frame = max_frame - frames_include
    df = df[df["frames"] >= start_frame].copy()
    df["frames"] = df["frames"] - start_frame
    df["time"] = (df["frames"]*15)/60
    
    nice_colors = [ figure_util.red, figure_util.green, figure_util.blue, figure_util.yellow]

    for cell in df["cells"].unique():
        this_cell = df[df["cells"] == cell]

        if np.any((this_cell["time"]<4)&(this_cell["time"]>3)&(this_cell[chan]>158)):
            print(cell)
        
        ax.plot(this_cell["time"], this_cell[chan], **bg_style)
    for cell, color in zip(chosen_traces, nice_colors):
        ch_style.update({"label": str(cell), 
                         "color":color})
        this_cell = df[df["cells"] == cell]
        ax.plot(this_cell["time"], this_cell[chan], **ch_style)
    return ax


def main():
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/padmovies_brightfield/traces/")
    frames = 21
    strains = [ #("sigb",  "MR", frames, [83, 134, 198, 112]),
                #("sigb",  "MY", frames, [83, 134, 198, 112]),
                ("delru", "MY", frames, [57, 74,  101, 105] ),
                #("delqp", "MY", frames, [91, 71, 89, 65])]
    ]
    fig, ax = plt.subplots(len(strains), 1)
    ax = np.atleast_1d(ax)


    bg_style= {"linewidth":0.5, "alpha":0.4, "color":"gray", "label":'_nolegend_'}
    hl_style= {"linewidth":3, "alpha":0.4}

    for i, (filen, chan, frames_include, hlcells) in enumerate(strains):
        df = pd.read_csv(os.path.join(basedir, filen + ".tsv"), sep="\t", )
        #hlcells= [47 , 70 , 105 , 106 , 137]
        ax[i] = get_figure(ax[i], df, chan, hlcells, frames_include, bg_style, hl_style )
        ax[i].set_ylim(0,300)
        ax[i].set_xlim(0,5.25)
        ax[i].legend()
    plt.show()


if __name__ == '__main__':
    main()