import numpy as np
import lib.cell_tracking.track_data as track_data
from lib.cell_tracking.track_data import TrackData
import pandas as pd
import lib.figure_util as figure_util
import matplotlib.pyplot as plt

import scipy.stats

def load_data(compiled_data_path, cell_track_path):
    td = TrackData(cell_track_path)
    df = pd.read_csv(compiled_data_path, sep="\t")
    return df, td

metrics = {"mean": lambda x: x.mean(),
            "std": lambda x: x.std(),
            "CV": scipy.stats.variation }

def plot_hist(ax, df, chan, bins,  **kwargs):
    #cell = df[df["cell_id"].isin(cell_ids)].sort_values(by=["cell_id", "frame"])
    values = df[chan].dropna()
    for name, func in metrics.items(): 
        print(name, func(values.values))

    counts, bins = np.histogram(values, bins=bins) 
    counts = (counts/len(values)) * 100
    cbins = bins[1:] - ((bins[1] - bins[0])/2)
    #times = cell.groupby("frame").mean()["time"]
    # if "color" not in kwargs: kwargs["color"] = np.random.rand(3)
    # if "label" not in kwargs: kwargs["label"] = str(cell_ids[-1])
    ax.barh(cbins, width=counts, height=80, **kwargs)
    ax.set_xlabel("Percentage of cells")
    return ax


def get_figure(ax, compiled, bins, channel, **kwargs):
    ax = plot_hist(ax, compiled, channel, bins, **kwargs)
    
    return ax




def main():
    fig, ax = plt.subplots(1,1)
    ax = get_figure(ax)


    plt.show()



if __name__ == '__main__':
    main()