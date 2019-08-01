import os.path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import scipy.io
import scipy.stats

import lib.figure_util as figure_util
from lib import filedb, strainmap
from lib.figure_util import timecolor

from figures.sup_transformable_live import subfig_draw_bin

this_dir = os.path.dirname(__file__)
# stylefile = os.path.join(this_dir, "../figstyle.mpl")
import seaborn as sns

figure_util.apply_style()
letters = figure_util.letters

basedir = "/media/nmurphy/BF_Data_Orange/datasets/new_strain_snaps1/"
cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))


def is_a_good_cell(v, mean=10300, std=3500):
    if v > mean - std:
        return True
    else:
        return False


cell_df["good_cell"] = cell_df["red_raw_mean"].apply(is_a_good_cell)
cell_df_filter = cell_df.loc[cell_df["good_cell"], :]

cell_df = cell_df_filter.copy()

strain_to_type, type_to_strain = strainmap.load()
strain_to_type = {s: t[0] for s, t in strain_to_type.items()}

cell_types = np.unique([t for t in strain_to_type.values()])


type_to_strain = dict(zip(cell_types, [[]] * len(cell_types)))
for strain, typel in strain_to_type.items():
    type_to_strain[typel] = type_to_strain[typel] + [strain]

sigavsiga = file_df[
    (
        file_df["strain"].isin(type_to_strain["et_sigar_sigay"])
        & (file_df["time"] == 48.0)
        # & (file_df["dirname"] == "Set_2/48hrs/63x")
    )
]
# print(sigavsiga)

red_chan = "red_raw_mean"
green_chan = "green_raw_mean"
cell_df[red_chan] = cell_df[red_chan] / 10000
cell_df[green_chan] = cell_df[green_chan] / 10000

xmin = 1.0300 - 0.3500
# strain_sigby = cell_df.loc[cell_df["global_file_id"].isin(sigavsigb.index), :]
strain_sigay = cell_df.loc[cell_df["global_file_id"].isin(sigavsiga.index), :]

set_2 = strain_sigay["global_file_id"].isin([19, 20, 21])
set_3 = strain_sigay["global_file_id"].isin([102, 103, 104, 105])
set_2_yfp_mean = strain_sigay.loc[set_2, green_chan].mean()
set_3_yfp_mean = strain_sigay.loc[set_3, green_chan].mean()
print("set_2 green mean", set_2_yfp_mean)
print("set_3 green mean", set_3_yfp_mean)
shift = set_2_yfp_mean - set_3_yfp_mean
print("shifting by ", shift)
strain_sigay.loc[set_3, green_chan] = strain_sigay.loc[set_3, green_chan] + shift

# mean_x = (file_df["dirname"] == "Set_2/48hrs/63x")

# strain_sigay_other_set = cell_df.loc[cell_df["global_file_id"].isin(sigavsiga.index), :]
# strain_sigay = strain_sigay.loc[strain_sigay[red_chan] >= xmin, :]


def plot_regression(x, y, ax=None, **kwargs):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    nx = np.linspace(x.min(), x.max(), 100)
    # print(nx)
    # print(intercept + slope * nx)
    if ax is not None:
        ax.plot(
            nx,
            intercept + slope * nx,
            label="R$^2$: {0:0.02f}".format(r_value ** 2),
            **kwargs
        )
    return ax


fig = plt.figure()
gs = fig.add_gridspec(
    nrows=2,
    ncols=2,
    height_ratios=[0.3, 0.7],
    width_ratios=[0.5, 0.5],
    wspace=0.06,
    hspace=0.06,
)  # left=0.05, right=0.48, wspace=0.05)
ax_joint = fig.add_subplot(gs[1, :])
# ax_mx = fig.add_subplot(gs[0, 0], sharex=ax_joint)
# ax_my = fig.add_subplot(gs[1, 1], sharey=ax_joint)
# ax_leg = fig.add_subplot(gs[0, 1])
# ax_leg.axis("off")
ax_20x = fig.add_subplot(gs[0, 0])  # fig.add_axes([0.065, 0.78, 0.45, 0.21])
ax_63x = fig.add_subplot(gs[0, 1])  # fig.add_axes([0.5, 0.78, 0.45,0.21])


w = 2048
h = 1548
wh63 = 500
FP_max_min = [(0, (2 ** 16) - 1), (0, 45000), (0, 1)]  # RFP  # YFP
label = r"et-WT P$_{\mathit{sigA}}$-YFP"
grad_image = "Test_snaps/48hrs/NEB034_48hrs_20x_4.tif"
grad_region = ((500, 500 + h), (0, 0 + w))  # row, cols
scalebar = 20

path = os.path.join("datasets/lsm700_live20x_newstrain1/images", grad_image)
ax_20x = subfig_draw_bin.get_figure(
    ax_20x,
    label,
    path,
    grad_region,
    [0, 1],
    FP_max_min,
    (0, 100),  # not doing yet
    add_scale_bar=scalebar,
)
grand_lab = (0.03, 0.97)
ax_20x.text(
    grand_lab[0],
    grand_lab[1],
    "A",
    va="top",
    ha="left",
    color="white",
    fontsize=figure_util.letter_font_size,
    transform=ax_20x.transAxes,
)

#%%%%%%%%%%%%%%%%%%
## Cell images
##################
FP_Single_max_min = [(0, 40000), (0, 30000), (0, 1)]  # RFP  # YFP #CFP
cell_image = "Set_2/48hrs/63x/NEB_034_48hrs_63x_4.tif"
cell_region = ((190, 190 + wh63), (190, 190 + wh63))  # row, cols
scalebar = 63

path = os.path.join("datasets/new_strain_snaps1/images", cell_image)
ax_63x = subfig_draw_bin.get_figure(
    ax_63x,
    label,
    path,
    cell_region,
    [0, 1],
    FP_Single_max_min,
    (0, 100),  # not doing yet
    add_scale_bar=scalebar,
)
grand_lab = (0.03, 0.97)
ax_63x.text(
    grand_lab[0],
    grand_lab[1],
    "B",
    va="top",
    ha="left",
    color="white",
    fontsize=figure_util.letter_font_size,
    transform=ax_63x.transAxes,
)
ax_joint.text(
    grand_lab[0],
    grand_lab[1],
    "C",
    va="top",
    ha="left",
    color="black",
    fontsize=figure_util.letter_font_size,
    transform=ax_joint.transAxes,
)

###############################
###########################
############################
# red_chan = "red_raw_meannorm"
# green_chan = "red_raw_meannorm"
# bins = np.linspace(0,3.0,100)

rbins = np.linspace(0, 2, 100)
gbins = np.linspace(0, 4, 100)


strain_sigay.plot.scatter(
    x=red_chan,
    y=green_chan,
    s=2,
    ax=ax_joint,
    c=[figure_util.red],
    alpha=0.2,
    edgecolors="none",
)
# cbarax =
# sns.jointplot(strain_sigay[red_chan], strain_sigay[green_chan], cmap=plt.cm.plasma, joint_kws={ "linewidths":0.5})
# sns.jointplot(strain_sigby[red_chan], strain_sigby[green_chan], cmap=plt.cm.plasma, joint_kws={ "linewidths":1})
sns.kdeplot(
    strain_sigay[red_chan],
    strain_sigay[green_chan],
    ax=ax_joint,
    cmap=plt.cm.bone,
    linewidths=0.5,
)
# ax_joint.scatter(
#     x=[],
#     y=[],
#     s=10,
#     c=[figure_util.red],
#     label=r"P$_{\mathit{sigA}}$-RFP P$_{\mathit{sigA}}$-YFP",
# )

print(strain_sigay[red_chan].min())

ax_joint = plot_regression(
    strain_sigay[red_chan],
    strain_sigay[green_chan],
    ax=ax_joint,
    color=figure_util.red,
    linestyle="-",
    linewidth=2,
)


ax_joint.set_xlim(xmin, rbins.max())
ax_joint.set_ylim(0, gbins.max())
ax_joint.legend(
    loc="center right"
)  # , bbox_to_anchor=(0, 0), bbox_transform=ax_leg.transAxes)
ax_joint.set_xlabel("RFP flouresence (AU)")
ax_joint.set_ylabel("YFP flouresence (AU)")


filename = "sup_sigayfp"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.2)
fig.set_size_inches(width, height)
fig.subplots_adjust(left=0.10, bottom=0.08, top=0.99, right=0.97)
# fig.tight_layout()
figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)
# figure_util.save_figures(fig, filename, ["png"], this_dir)

