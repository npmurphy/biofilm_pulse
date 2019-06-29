import pandas as pd

# import numpy as np
import os.path
import numpy as np
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from figures.figure_allspore_2xqp_combo import subfig_sigb_grad
from figures.sup_63x_gradients import subfig_plot_grad_errors

# from figures.figure_sigb_repress_spores import subfig_spoiid_vs_sigb_raw_cor
import subfig_spoiid_vs_sigb_raw_cor

# import subfig_density_gradient
from figures.figure_allspore_2xqp_combo import subfig_spore_count_gradient

# import subfig_histograms

# import subfig_spoiid_vs_sigb_isolines
# from lib import strainmap

import lib.figure_util as figure_util

figure_util.apply_style()
# from lib.figure_util import strain_color, strain_label
# import matplotlib.ticker as mpt

np.random.seed(47)
fig = plt.figure()


corr_ax = fig.add_axes([0.10, 0.2, 0.33, 0.75])
anti_ax = fig.add_axes([0.53, 0.19, 0.42, 0.75])
## cbar.ax = Bbox(x0=0.8327536231884058, y0=0.09999999999999987, x1=0.89, y1=0.49111111111111105)


########
## Spore spoiid correlation
########
this_dir = os.path.dirname(__file__)
basedir = os.path.join(this_dir, "../../datasets/LSM780_63x_spoiid_v_sigb/")
file_df = filedb.get_filedb(os.path.join(basedir, "filedb.tsv"))
print(file_df)
cell_df = pd.read_hdf(basedir + "rsiga_ysigb_cspoiid_redoedgedata.h5", "cells")
# Ignore first 2 um (only done for consistency)
cell_df = cell_df[cell_df["distance"] > 2].copy()

corr_ax.tick_params(direction="out")
anti_ax.tick_params(direction="out")

corr_ax, corr_cb = subfig_spoiid_vs_sigb_raw_cor.get_figure(corr_ax, file_df, cell_df)
corr_ax.set_xlabel("Mean normalised P$_{\mathit{sigB}}$-YFP", labelpad=-0.5)
corr_ax.set_ylabel("Mean norm'd P$_{\mathit{spoIID}}$-CFP")
corr_ax.yaxis.labelpad = 0
corr_ax.xaxis.labelpad = 2

########
## Spore Anti correlation
########
shuffle_df = cell_df.copy()
# shuffle_df["meannorm_blue"] = (
#     shuffle_df["meannorm_blue"].sample(frac=1).reset_index(drop=True)
# )
shuffle_df["meannorm_green"] = (
    shuffle_df["meannorm_green"].sample(frac=1).reset_index(drop=True)
)
anti_ax, anti_cb = subfig_spoiid_vs_sigb_raw_cor.get_figure(
    anti_ax, file_df, shuffle_df
)
anti_ax.set_xlabel("Shuffled P$_{\mathit{sigB}}$-YFP values", labelpad=-0.5)
anti_ax.set_ylabel("Mean norm'd P$_{\mathit{spoIID}}$-CFP")
anti_ax.yaxis.labelpad = 0
anti_ax.xaxis.labelpad = 2

# #corr_ax, corr_cb, cont_cb = subfig_spoiid_vs_sigb_isolines.get_figure(corr_ax, file_df, cell_df)
cbar = fig.colorbar(anti_cb, ax=anti_ax)

cbar.ax.tick_params(direction="out", length=1, width=0.5, colors="k")
cbar.ax.set_ylabel("Number of cells", rotation=270)
# print("orig pad  = ", cbar.ax.yaxis.labelpad)
cbar.ax.yaxis.labelpad = 7


props = {"facecolor": "none", "edgecolor": "none"}

letter_style = {
    "verticalalignment": "top",
    "horizontalalignment": "right",
    "fontsize": figure_util.letter_font_size,
    # "color": "red"
}

letter_y = 0.99
axes = [corr_ax, anti_ax]
axes[0].text(0.03, letter_y, "A", transform=fig.transFigure, **letter_style)
axes[1].text(0.455, letter_y, "B", transform=fig.transFigure, **letter_style)


filename = "spoiid_anticorr"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.5)
fig.set_size_inches(width, height)  # common.cm2inch(width, height))
# fig.subplots_adjust(left=0.10, right=0.89, top=0.98, bottom=0.1, hspace=0.25, wspace=0.4)

#     #pos2 = #copy.copy(pos1)
#     pos2.x0 = pos2.x0 + 0.1
#     a.set_position(pos2, which="both") # set a new position
#     pos3 = a.get_position(original=False) # get the original position
#     print(pos3)

# fig.align_ylabels()

figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
