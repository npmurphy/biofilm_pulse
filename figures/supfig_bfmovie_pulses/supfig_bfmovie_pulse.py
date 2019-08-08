import pandas as pd
import numpy as np
import os.path
import skimage.io
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import lib.filedb
import subfig_trace
import subfig_hist

# import subfig_gradient
# import data.bio_film_data.strainmap as strainmap

this_dir = os.path.dirname(__file__)
stylefile = os.path.join(this_dir, "../figstyle.mpl")
plt.style.use(stylefile)
import lib.figure_util as figure_util

# from lib.figure_util import dpi, strain_color, strain_label

fig = plt.figure()

# Making less wide
outer_gs = gridspec.GridSpec(
    2, 2, height_ratios=[1, 1], hspace=0.23, wspace=0.23, width_ratios=[1.7, 1]
)
ax_rfpulses = plt.subplot(outer_gs[0, 0])
ax_yfpulses = plt.subplot(outer_gs[1, 0])
ax_rfhistos = plt.subplot(outer_gs[0, 1])
ax_yfhistos = plt.subplot(outer_gs[1, 1])


# BF movie traces
base_dir = "datasets/iphox_singlecell/BF10_timelapse/"
# base_dir="proc_data/iphox_movies/BF10_timelapse/"
# base_dir =  "datasets_offline/iphox_singlecell/BF10_timelapse/"
movie = "Column_2"
comp_path = os.path.join(base_dir, movie, "compiled_redo.tsv")
ct_path = os.path.join(base_dir, movie, "cell_track.json")
compiled_trace, cell_tracks = subfig_trace.load_data(comp_path, ct_path)
compiled_trace["red"] = compiled_trace["red"]  # /1000
compiled_trace["green"] = compiled_trace["green"]  # 1000
compiled_trace["time"] = compiled_trace["time"] / 60  # hours
print(compiled_trace.columns)

ymax = 3500
rmax = 7000
# ymax = 3.0 #3500
# rmax = 2.0 #6000
plots = [
    ("red", "P$_{sigA}$-RFP (AU)", rmax, ax_rfpulses),
    ("green", "P$_{sigB}$-YFP (AU)", ymax, ax_yfpulses),
]
for chan, ylab, cmax, ax in plots:
    ax = subfig_trace.get_figure(ax, compiled_trace, cell_tracks, chan)
    ax.set_ylabel(ylab)
    ax.set_xlim(20, right=50)
    ax.set_ylim(bottom=0, ymax=cmax)
    ax.ticklabel_format(style="sci", scilimits=(1, 3), axis="y", useMathText=True)

ax_rfpulses.set_xlabel("")


plots = [
    ("red", "P$_{sigA}$-RFP (AU)", rmax, ax_rfhistos),
    ("green", "P$_{sigB}$-YFP (AU)", ymax, ax_yfhistos),
]

# bins = np.linspace(0, 6000, 50)
# print(bins[1] - bins[0])
for chan, ylab, cmax, ax in plots:
    color = figure_util.red if chan == "red" else figure_util.green
    opts = {"color": color}
    bins = np.arange(0, 6000, 120)
    ax = subfig_hist.get_figure(ax, compiled_trace, bins, chan, **opts)
    ax.set_ylabel(ylab)
    ax.set_ylim(bottom=0, ymax=cmax)
    ax.ticklabel_format(style="sci", scilimits=(1, 3), axis="y", useMathText=True)
    ax.set_xlim(0, right=10)
    ax.tick_params(axis="y", which="both", direction="out")  #
    ax.yaxis.labelpad = -1

    # ax.set_ylim(bottom=0)

ax_rfhistos.set_xlabel("")

letter_style = {
    "verticalalignment": "top",
    "horizontalalignment": "right",
    "fontsize": figure_util.letter_font_size,
    # "color": "red"
}

letter_x1 = 0.025
letter_x2 = 0.63
letter_y1 = 0.99
letter_y2 = 0.525
ax_rfhistos.text(letter_x1, letter_y1, "A", transform=fig.transFigure, **letter_style)
ax_rfpulses.text(letter_x2, letter_y1, "B", transform=fig.transFigure, **letter_style)
ax_yfhistos.text(letter_x1, letter_y2, "C", transform=fig.transFigure, **letter_style)
ax_yfpulses.text(letter_x2, letter_y2, "D", transform=fig.transFigure, **letter_style)


filename = "supfig_bfmovie_pulses"
# width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.5 )
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.8)
fig.subplots_adjust(
    left=0.085, right=0.97, top=0.95, bottom=0.11
)  # , hspace=0.25, wspace=0.25)

fig.set_size_inches(width, height)  # common.cm2inch(width, height))
figure_util.save_figures(fig, filename, ["png", "pdf"], base_dir=this_dir)

