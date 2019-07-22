import os.path
import lib.filedb
import matplotlib.pyplot as plt
import subfig_spore_count_gradient
import pandas as pd
import matplotlib.lines

# import subfig_spore_image

import lib.figure_util
from lib import filedb

lib.figure_util.apply_style()

# fig, cellcount_ax = plt.subplots(1,1)
fig, ax = plt.subplots(3, 1)
clcount_ax = ax[1]
spcount_ax = ax[0]
sppeaks_ax = ax[2]
# x2qpline_ax = ax[3]
axes = [spcount_ax, clcount_ax, sppeaks_ax]  # , x2qpline_ax]

# fig = plt.figure()
# import matplotlib.gridspec as gridspec
# gs = gridspec.GridSpec(3, 1, height_ratios=[0.4, 0.3, 0.3])
# spimg_ax = plt.subplot(gs[0])s
# spcount_ax = plt.subplot(gs[1])
# cellcount_ax = plt.subplot(gs[2])

ylabel_cord = (-0.07, 0.5)

sspb_strains = [
    (st, lib.figure_util.strain_label[st]) for st in ["JLB077", "JLB117", "JLB118"]
]

this_dir = os.path.dirname(__file__)
base = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")

file_df = filedb.get_filedb(os.path.join(base, "file_list.tsv"))
file_df = file_df[
    ~((file_df["name"] == "JLB077_48hrs_center_1_1") & (file_df["dirname"] == "Batch1"))
]
individual = pd.read_csv(
    os.path.join(base, "spore_cell_individual.tsv"), sep="\t", index_col="index"
)

sspb_strains = ["JLB077", "JLB117", "JLB118"]


# Some images had little tiny regions at the end with <10 cell spores in them
# that produced huges spikes of 100% spores etc.
# to ignore this we are using 100 as a minimum sample size.
# 10 does the job, 500, 100 look good at the top but introduce more artifacts later.
# 100 is just a big enough number.

###########
## Spore density
for strain in sspb_strains:
    spcount_ax = subfig_spore_count_gradient.get_figure(
        spcount_ax, file_df, individual, strain, "fraction_spores", 100
    )

# spcount_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
# spcount_ax.set_ylim(0, 0.00031)
spcount_ax.set_ylabel("Spore/cell ratio")
leg = spcount_ax.legend(loc="upper right")
# spcount_ax.get_yaxis().set_label_coords(*ylabel_cord)


# spimg_ax = subfig_spore_count_gradient.get_figure(spimg_ax, cachefile,  sspb_strains, "totalcounts")
# spimg_ax.set_ylabel("Total biofilm mass")
##spcount_ax.set_ylim(0, 0.0003)
# spimg_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
# spimg_ax.get_yaxis().set_label_coords(*ylabel_cord)


###########
## cell density
# cellcount_ax = subfig_cell_count_gradient.get_figure(cellcount_ax, datadir, file_df, sspb_strains, "cell")
# cl_channel = "cell_count_area_scaled"
for strain in sspb_strains:
    clcount_ax = subfig_spore_count_gradient.get_figure(
        clcount_ax, file_df, individual, strain, "area_norm_total_counts", 100
    )

clcount_ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0), useMathText=True)
clcount_ax.set_ylim(0, 0.0017)
clcount_ax.set_ylabel("Spore and cell density")  #
# cellcount_ax.get_yaxis().set_label_coords(*ylabel_cord)
# leg = clcount_ax.legend()


#### peaks
sppeaks_ax = subfig_spore_count_gradient.get_figure_peaks(
    sppeaks_ax, file_df, individual, sspb_strains, "fraction_spores", 100
)
sppeaks_ax.set_yticklabels(sppeaks_ax.get_yticklabels(), rotation=50)
sppeaks_ax.set_ylabel("")
text = "Location of spore gradient peak"

a = matplotlib.lines.Line2D(
    [0],
    [1],
    linestyle="none",
    marker="o",
    markersize=3,
    markerfacecolor="black",
    markeredgecolor="none",
)
# sppeaks_ax.legend([a], [text])  # handles, labels)

### 2xQP individua;
"""
x2qpline_ax = subfig_spore_count_gradient.get_figure_individual(
    x2qpline_ax, file_df, individual, "JLB117", "fraction_spores", 100
)
x2qpline_ax.set_ylim(bottom=0, top=0.25)
x2qpline_ax.set_ylabel("Spore/cell ratio")
text = "{} individual files".format(lib.figure_util.strain_label["JLB117"])
x2qpline_ax.text(
    0.98, 0.98, text, va="top", ha="right", transform=x2qpline_ax.transAxes
)
"""

for a in axes:
    a.yaxis.set_label_coords(-0.09, 0.5)
    a.set_xlim(0, 140)

ax[-1].set_xlabel("Distance from top of biofilm (μm)")
########
## Spore image
########
# sp_image_basedir = "../../data/bio_film_data/data_local_cache/spores_63xbig/"

# files = [{"Path": "Batch3/JLB118_48hrs_center_7_1.lsm", "x": 1832 * 20, "y": 227 *20,
#         "cr_min":0,
#         "cr_max":10000,
#         "cg_min":2000,
#         "cg_max":(2**14), }]
# height = 260 * 20
# width = 700 * 20
# i = files[0]
# spimg_ax = subfig_spore_image.plot_big_image(spimg_ax,
#                                         sp_image_basedir + i["Path"],
#                                         ((i["y"], i["y"] + height),
#                                         (i["x"], i["x"] + width)),
#                                         (height, width),
#                                         i, vertical=False, scalebar=True)
letter_lab = (-0.05, 1.0)
for l, a in zip(lib.figure_util.letters, axes):
    a.text(
        letter_lab[0],
        letter_lab[1],
        l,
        transform=a.transAxes,
        fontsize=lib.figure_util.letter_font_size,
    )

fig.align_ylabels()

filename = "spore_grad_compare"
width, height = lib.figure_util.get_figsize(
    lib.figure_util.fig_width_small_pt, wf=1.0, hf=1.0
)
fig.subplots_adjust(
    left=0.11, right=0.97, top=0.95, bottom=0.08, hspace=0.35
)  # , wspace=0.25)
fig.set_size_inches(width, height)

lib.figure_util.save_figures(fig, filename, ["png", "pdf"], os.path.dirname(__file__))
# print("request size : ", figure_util.inch2cm((width, height)))
# fig.savefig(filename + ".png", dpi=dpi)
# fig.savefig(filename + ".pdf", dpi=dpi)
# figure_util.print_pdf_size(filename + ".pdf")
