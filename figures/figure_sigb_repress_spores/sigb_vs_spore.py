import pandas as pd


# import numpy as np
import os.path
import numpy as np
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_spoiid_vs_sigb_raw_cor
from figures.figure_allspore_2xqp_combo import subfig_sigb_grad
from figures.sup_63x_gradients import subfig_plot_grad_errors

# import subfig_density_gradient
from figures.figure_allspore_2xqp_combo import subfig_spore_count_gradient

# import subfig_histograms
import subfig_spoiid_image

# import subfig_spoiid_vs_sigb_isolines
# from lib import strainmap
import lib.figure_util as figure_util

figure_util.apply_style()
# from lib.figure_util import strain_color, strain_label
# import matplotlib.ticker as mpt

fig = plt.figure()
# fig, ax = plt.subplots(1,3)
# gs = gridspec.GridSpec(2, 2, width_ratios=[0.8,1.0], height_ratios=[1, 1], wspace=0.4)
# gs = gridspec.GridSpec(3, 3, width_ratios=[0.3, 0.35, 0.35])

# spimg_ax = plt.subplot(ax[0])
# corr_ax = plt.subplot(ax[1])
# sb_grad_ax = plt.subplot(ax[2]) # also spores
# spimg_ax = plt.subplot(gs[1, 0])
# corr_ax = plt.subplot(ax[1])
# corr_ax = plt.subplot(gs[1, 1])

corr_ax = fig.add_axes([0.59, 0.095, 0.33, 0.391111111111111])
# cbar.ax = Bbox(x0=0.8327536231884058, y0=0.09999999999999987, x1=0.89, y1=0.49111111111111105)

# sb_grad_ax = plt.subplot(gs[0,:]) # also spores
sb_grad_ax = fig.add_axes([0.1, 0.5888888888888888, 0.7900000000000001, 0.391111111111])
spimg_ax = fig.add_axes([0.1, 0.095, 0.2925925925925927, 0.39111111111111])
# for a in [corr_ax, cbar.ax, sp_grad_ax, spimg_ax]:
#     pos2 = a.get_position(original=False) # get the original position
#     print(pos2)

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

corr_ax, corr_cb = subfig_spoiid_vs_sigb_raw_cor.get_figure(corr_ax, file_df, cell_df)
corr_ax.set_xlabel("Mean normalised P$_{sigB}$-YFP", labelpad=-0.5)
corr_ax.set_ylabel("Mean norm'd P$_{spoIID}$-CFP")
corr_ax.yaxis.labelpad = 0

# #corr_ax, corr_cb, cont_cb = subfig_spoiid_vs_sigb_isolines.get_figure(corr_ax, file_df, cell_df)
cbar = fig.colorbar(corr_cb, ax=corr_ax)
# #cbar.add_lines()#corr_cb)
cbar.ax.set_ylabel("Number of cells", rotation=270)
# print("orig pad  = ", cbar.ax.yaxis.labelpad)
cbar.ax.yaxis.labelpad = 10


# cfp_thresh = 3000
# cfp_thresh = 2000
# time = 48
# location = "center"
# fids = file_df[(file_df["time"] == time) & (file_df["location"] == location)].index
# green_bins = np.linspace(0, 50000, 100)
# green_x = green_bins[1:] - (green_bins[1] - green_bins[0])


# timsct = cell_df[cell_df["global_file_id"].isin(fids)].copy()
# timsct["one"] = 1
# timsct["gthn"] = (timsct["mean_blue"] > cfp_thresh).values
# counts = timsct.groupby(pd.cut(timsct["mean_green"], green_bins)).sum()
# corr_ax.plot(green_x, counts["gthn"]/counts["one"], label=str(cfp_thresh))
# count_ax = corr_ax.twinx()
# count_ax.plot(green_x, counts["one"],color="blue")
# corr_ax.set_xlim(green_bins[0], green_bins[-1])
# corr_ax.set_ylabel("% of cells with P$_{spoIID}$-CFP over threshold")
# corr_ax.set_xlabel("P$_{\sigma^B}$-YFP")
# corr_ax.set_ylim(0, 1.0)

# plt.legend()


###########
## 63x sigb grad
###########
normalisation = [  # ("unnormed", (0, 8e3), "P$_{sigB}$-YFP (AU)"),
    ("ratio", (0, 1), "YFP/RFP Ratio")
]
spec = "jlb021"
this_dir = os.path.join(os.path.dirname(__file__))
base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/gradients")

# plotset = {"linewidth":0.5, "alpha":0.3, "color":figure_util.green}
plotset = {
    "alpha": 0.3,
    "color": figure_util.green,
    "label": figure_util.strain_label["JLB021"] + " P$_{sigB}$-YFP",
}
for n, (norm, ylim, ylabel) in enumerate(normalisation):
    args = (sb_grad_ax, base, norm, ylim, "sem", spec, [48], plotset)
    sb_grad_ax = subfig_plot_grad_errors.get_figure(*args)

# tenx_basepath = os.path.join(this_dir, "../../datasets/LSM780_10x_sigb/")
# tenx_gradient_df = pd.read_hdf(os.path.join(tenx_basepath, "gradient_data.h5"), "data")
# print(tenx_gradient_df.columns)
# tenx_gradient_df["ratio"] = tenx_gradient_df["green_bg_mean"]/tenx_gradient_df["red_bg_mean"]
# tenx_file_df = filedb.get_filedb(os.path.join(tenx_basepath, "filedb.tsv"))
# sb_grad_ax = subfig_sigb_grad.get_figure(sb_grad_ax, tenx_file_df, tenx_gradient_df, ["wt_sigar_sigby"])
sb_grad_ax.set_ylabel("YFP/RFP Ratio", color=figure_util.green)
sb_grad_ax.set_ylim(0, 0.4)
sb_grad_ax.set_xlim(0, 140)
sp_grad_ax = sb_grad_ax.twinx()

sspb_strains = ["JLB077"]
spbase = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")
spfile_df = filedb.get_filedb(os.path.join(spbase, "file_list.tsv"))
spfile_df = spfile_df[
    ~(
        (spfile_df["name"] == "JLB077_48hrs_center_1_1")
        & (spfile_df["dirname"] == "Batch1")
    )
]
spindividual = pd.read_csv(
    os.path.join(spbase, "spore_cell_individual.tsv"), sep="\t", index_col="index"
)
spchan = "fraction_spores"
spkw = {"color": figure_util.blue, "label": "WT Spores"}
for strain in sspb_strains:
    sp_grad_ax = subfig_spore_count_gradient.get_figure(
        sp_grad_ax, spfile_df, spindividual, strain, spchan, 100, spkw
    )

# sp_grad_ax.set_xlabel("Distance from top of biofilm (μm)", labelpad=-2)

lines, labels = [], []
for a in [sb_grad_ax, sp_grad_ax]:
    ln, lb = a.get_legend_handles_labels()
    lines += ln
    labels += lb

# lines, labels = zip(*[
# print(labels)
# print(type(lines))
# print(lines[0])
leg = sb_grad_ax.legend(lines, labels)
sp_grad_ax.spines["right"].set_visible(True)
sb_grad_ax.set_xlabel("Distance from top of biofilm (μm)", labelpad=-0.05)
sp_grad_ax.set_ylabel(
    "Spore/cell ratio", labelpad=7, rotation=270, color=figure_util.blue
)


################
## SpoIID image
################
spoiid_base = os.path.join(
    this_dir, "../../proc_data/fp3_unmixing/rsiga_ysigb_cspoiid/"
)
spimg_ax = subfig_spoiid_image.get_figure(spimg_ax, spoiid_base, this_dir)

# props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
props = {"facecolor": "none", "edgecolor": "none"}
# spimg_ax.text(0.0, -0.05, "P$_{sigA}$-RFP", transform=spimg_ax.transAxes,
#         fontsize=figure_util.letter_font_size,
#         verticalalignment='top',
#         horizontalalignment='left',
#         color=figure_util.red,
#         bbox=props)
# spimg_ax.text(1.0, -0.05, "P$_{sigB}$-YFP", transform=spimg_ax.transAxes,
#         fontsize=figure_util.letter_font_size,
#         verticalalignment='top',
#         horizontalalignment='right',
#         color=figure_util.green,
#         bbox=props)
# spimg_ax.text(0.0, -0.18, "P$_{spoIID}$-CFP", transform=spimg_ax.transAxes,
#         fontsize=figure_util.letter_font_size,
#         verticalalignment='top',
#         horizontalalignment='left',
#         color=figure_util.blue,
#         bbox=props)

letter_style = {
    "verticalalignment": "top",
    "horizontalalignment": "right",
    "fontsize": figure_util.letter_font_size,
    # "color": "red"
}

letter_x = 0.03
letter_y = 0.48
axes = [spimg_ax, spimg_ax, corr_ax]
axes[0].text(letter_x, 0.995, "A", transform=fig.transFigure, **letter_style)
axes[1].text(letter_x, letter_y, "B", transform=fig.transFigure, **letter_style)
axes[2].text(0.45, letter_y, "C", transform=fig.transFigure, **letter_style)


filename = "sigb_vs_spores"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.8)
fig.set_size_inches(width, height)  # common.cm2inch(width, height))
# fig.subplots_adjust(left=0.10, right=0.89, top=0.98, bottom=0.1, hspace=0.25, wspace=0.4)

#     #pos2 = #copy.copy(pos1)
#     pos2.x0 = pos2.x0 + 0.1
#     a.set_position(pos2, which="both") # set a new position
#     pos3 = a.get_position(original=False) # get the original position
#     print(pos3)

# fig.align_ylabels()

figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
