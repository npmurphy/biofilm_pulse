import matplotlib.pyplot as plt
import pandas as pd
import os

def get_figure(ax, df, chan, chosen_traces, frames_include, bg_style, ch_style):
    max_frame = df["frames"].max()
    start_frame = max_frame - frames_include
    df = df[df["frames"] > start_frame]
    
    df["time"] = (df["frames"]*15)/60
    for cell in df["cells"].unique():
        this_cell = df[df["cells"] == cell]
        print(cell)
        style = ch_style if cell in chosen_traces else bg_style
        ax.plot(this_cell["time"], this_cell[chan], **style)
    return ax


def main():
    this_dir = os.path.dirname(__file__)
    basedir = os.path.join(this_dir, "../../datasets/padmovies_brightfield/traces/")
    frames = 25
    strains = [ ("sigb",  "MR", frames),
                ("sigb",  "MY", frames),
                ("delru", "MY", frames),
                ("delqp", "MY", frames)]
    fig, ax = plt.subplots(len(strains), 1)

    bg_style= {"linewidth":0.5}#, "color":gray}
    bg_style= {"linewidth":1}

    for i, (filen, chan, frames_include) in enumerate(strains):
        df = pd.read_csv(os.path.join(basedir, filen + ".tsv"), sep="\t", )
        print(df.head())
        ax[i] = get_figure(ax[i], df, chan, [], frames_include, bg_style, bg_style )
        ax[i].set_ylim(0,250)
    plt.show()


if __name__ == '__main__':
    main()