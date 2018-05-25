import os.path
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from lib import figure_util
#plt.style.use('../figstyle.mpl')

def get_figure(ax, df):
    a = ax.plot(df["Time"]/3600, df["A"], color=figure_util.blue, label="A")
    #ax.plot(df["Time"]/3600, df["GaB"])
    b = ax.plot(df["Time"]/3600, df["B"], color=figure_util.green, label="B")

    g = ax.axhline(y=0.923386, color="gray", linestyle="--")#, label="Spore threshold")

    ax.legend(loc="upper right")
    return ax, [a,b, g]


def get_seed(path):
    bn = os.path.basename(path)
    name = bn.split("|")[0]
    return name.split("seed")[1]

# def smooth_the_graph(df):
#     df["Time"]
#     df["A"] -


def main():
    runf = "../../algo/luna/final_sweeps/"

    trace_paths = glob(runf + "movethresh3/bfsim_b_trace_seed*|*pscale_a=0.7*,pscale_b=0.25*.tsv") # wildtype pulses
    trace_bistable_paths = glob(runf + "movethresh3/bfsim_b_trace_seed*|*pscale_a=3.6*,pscale_b=2.0*.tsv") # bistable

    fig, ax = plt.subplots(len(trace_paths), 2)
    for t, trace_path in enumerate(trace_paths):
        seed = get_seed(trace_path)
        traces = pd.read_csv(trace_path, sep="\t")
        ax[t, 0], lines = get_figure(ax[t, 0], traces)
        ax[t, 0].set_title(seed)
    #plt.show()
    
    for t, trace_path in enumerate(trace_bistable_paths):
        seed = get_seed(trace_path)
        traces = pd.read_csv(trace_path, sep="\t")
        ax[t, 1], lines = get_figure(ax[t, 1], traces)
        ax[t, 1].set_title(seed)
    plt.show()


if __name__ == '__main__':
    main()