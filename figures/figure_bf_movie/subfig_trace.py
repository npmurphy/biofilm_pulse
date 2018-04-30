import numpy as np
import lib.cell_tracking.track_data as track_data
from lib.cell_tracking.track_data import TrackData
import pandas as pd

import matplotlib.pyplot as plt


def load_data(compiled_data_path, cell_track_path):
    td = TrackData(cell_track_path)
    df = pd.read_csv(compiled_data_path, sep="\t")
    return df, td


def plot_trace(ax, df, chan, cell_ids, kwargs):
    cell = df[df["cell_id"].isin(cell_ids)].sort_values(by=["cell_id", "frame"])
    values = cell.groupby("frame").sum()[chan]
    times = cell.groupby("frame").mean()["time"]
    if "color" not in kwargs: kwargs["color"] = np.random.rand(3)
    if "label" not in kwargs: kwargs["label"] = str(cell_ids[-1])
    ax.plot(times, values, **kwargs)
    
    ax.set_xlabel("Time (hours from inoculation)")
    return ax


def get_figure(ax, compiled, tracked):
    tree = tracked.make_tree()
    leaves = track_data.get_leaves(tree)

    for l in leaves:
        opts = {"color": np.random.rand(3),
                "label": str(l)}
        lineage =  tracked.get_cell_lineage(l)
        plot_trace(ax, compiled, "g_by_r", lineage, opts)
    
    return ax




def main():
    fig, ax = plt.subplots(1,1)
    ax = get_figure(ax)


    plt.show()



if __name__ == '__main__':
    main()