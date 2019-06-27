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

this_dir = os.path.dirname(__file__)
# stylefile = os.path.join(this_dir, "../figstyle.mpl")
import seaborn as sns

figure_util.apply_style()


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
    )
]
sigavsigb = file_df[
    (
        file_df["strain"].isin(type_to_strain["et_sigar_sigby"])
        & (file_df["time"] == 48.0)
    )
]

red_chan = "red_raw_mean"
green_chan = "green_raw_mean"
cell_df[red_chan] = cell_df[red_chan]/ 10000
cell_df[green_chan] = cell_df[green_chan] / 10000

strain_sigby = cell_df.loc[cell_df["global_file_id"].isin(sigavsigb.index), :]
strain_sigay = cell_df.loc[cell_df["global_file_id"].isin(sigavsiga.index), :]


def plot_regression(x, y, ax=None, **kwargs):
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    nx = np.linspace(x.min(), x.max(), 100)
    print(nx)
    print(intercept + slope * nx)
    if ax is not None:
        ax.plot(
            nx,
            intercept + slope * nx,
            label="R$^2$: {0:0.03f}".format(r_value ** 2),
            **kwargs
        )
    return ax


fig = plt.figure()
gs = fig.add_gridspec(nrows=2, ncols=2, height_ratios=[0.2, 0.8], width_ratios=[0.8, 0.2], 
    wspace=0.06, hspace=0.06)# left=0.05, right=0.48, wspace=0.05)
ax_joint = fig.add_subplot(gs[1,0])
ax_mx = fig.add_subplot(gs[0,0], sharex=ax_joint)
ax_my = fig.add_subplot(gs[1, 1], sharey=ax_joint)
ax_leg = fig.add_subplot(gs[0, 1])
ax_leg.axis("off")
# red_chan = "red_raw_meannorm"
# green_chan = "red_raw_meannorm"
# bins = np.linspace(0,3.0,100)

rbins = np.linspace(0, 2, 100)
gbins = np.linspace(0, 4, 100)


# strain_sigby.plot.scatter(x=red_chan, y=green_chan,s=2, ax=ax, c="cyan", alpha=0.2)# label=r"P$_{\mathrm{sigA}}$-RFP P$_{\mathrm{sigB}}$-YFP")
strain_sigby.plot.scatter(
    x=red_chan,
    y=green_chan,
    s=2,
    ax=ax_joint,
    c=[figure_util.black],
    alpha=0.2,
    edgecolors="none",
)  # , label="P$_{\mathrm{sigA}}$-RFP P$_{\mathrm{sigA}}$-YFP")
strain_sigay.plot.scatter(
    x=red_chan,
    y=green_chan,
    s=2,
    ax=ax_joint,
    c=[figure_util.red],
    alpha=0.2,
    edgecolors="none",
)  # , label="P$_{\mathrm{sigA}}$-RFP P$_{\mathrm{sigA}}$-YFP")
#cbarax = 
# sns.jointplot(strain_sigay[red_chan], strain_sigay[green_chan], cmap=plt.cm.plasma, joint_kws={ "linewidths":0.5})
# sns.jointplot(strain_sigby[red_chan], strain_sigby[green_chan], cmap=plt.cm.plasma, joint_kws={ "linewidths":1})
sns.kdeplot(strain_sigay[red_chan], strain_sigay[green_chan], ax=ax_joint, cmap=plt.cm.plasma, linewidths=0.5)
sns.kdeplot(strain_sigby[red_chan], strain_sigby[green_chan], ax=ax_joint, cmap=plt.cm.plasma, linewidths=0.5)

sns.kdeplot(strain_sigby[red_chan], ax=ax_mx, color=figure_util.black, legend=False, shade=True)
sns.kdeplot(strain_sigay[red_chan], ax=ax_mx, color=figure_util.red, legend=False, shade=True)
sns.kdeplot(strain_sigby[green_chan], ax=ax_my, color=figure_util.black, legend=False, vertical=True, shade=True)
sns.kdeplot(strain_sigay[green_chan], ax=ax_my, color=figure_util.red, legend=False, vertical=True, shade=True)


ax_joint.scatter(
    x=[],
    y=[],
    s=10,
    c=[figure_util.black],
    alpha=1,
    label=r"P$_{\mathrm{sigA}}$-RFP P$_{\mathrm{sigB}}$-YFP",
)
ax_joint.scatter(
    x=[],
    y=[],
    s=10,
    c=[figure_util.red],
    label=r"P$_{\mathrm{sigA}}$-RFP P$_{\mathrm{sigA}}$-YFP",
)

ax_joint = plot_regression(
    strain_sigby[red_chan],
    strain_sigby[green_chan],
    ax=ax_joint,
    color=figure_util.black,
    linestyle="-",
    linewidth=2,
)
ax_joint = plot_regression(
    strain_sigay[red_chan],
    strain_sigay[green_chan],
    ax=ax_joint,
    color=figure_util.red,
    linestyle="-",
    linewidth=2,
)

xmin = 1.0300 - 0.3500
ax_joint.set_xlim(xmin, rbins.max())
ax_joint.set_ylim(0, gbins.max())
ax_mx.ticklabel_format(style='sci',scilimits=(0,0),axis='y',useMathText=True )
ax_my.ticklabel_format(style='sci',scilimits=(0,0),axis='x',useMathText=True )


# ax.set_title("RFP vs YFP")
# arts = [asiga, asigb]
# labels = [siga.get_label(), asigb.get_label()]
ax_joint.legend(loc="center right")#, bbox_to_anchor=(0, 0), bbox_transform=ax_leg.transAxes)
ax_joint.set_xlabel("RFP flouresence (AU)")
ax_joint.set_ylabel("YFP flouresence (AU)")


filename = "sup_sigayfp"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.0)
fig.set_size_inches(width, height)
fig.subplots_adjust(left=0.10, bottom=0.1, top=0.97, right=0.97)
# fig.tight_layout()
figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)
#figure_util.save_figures(fig, filename, ["png"], this_dir)
