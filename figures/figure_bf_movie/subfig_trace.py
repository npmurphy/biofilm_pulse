import numpy as np
import lib.cell_tracking.track_data as track_data
from lib.cell_tracking.track_data import TrackData
import pandas as pd
import lib.figure_util as figure_util
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

    print(leaves)

    for l in leaves:
        opts = {"color": "gray", #np.random.rand(3),
                "linewidth": 0.5,
                "label": str(l)}
        lineage =  tracked.get_cell_lineage(l)
        plot_trace(ax, compiled, "g_by_r", lineage, opts)


    short_cells = [ "18", "33", "25", 20, 36, 30, 17 ]
    #['1 '6', '34', '29', '11', '22', '1', '32']
    select_cells = [ "34", "28", "10" ]
    nice_colors = [ figure_util.red, figure_util.green, figure_util.blue]
    for cell, color in zip(select_cells, nice_colors):
        opts = {"color": color,
                "linewidth": 2,
                "label": str(l)}
        lineage =  tracked.get_cell_lineage(cell)
        plot_trace(ax, compiled, "g_by_r", lineage, opts)
    
    return ax




def main():
    fig, ax = plt.subplots(1,1)
    ax = get_figure(ax)


    plt.show()



if __name__ == '__main__':
    main()