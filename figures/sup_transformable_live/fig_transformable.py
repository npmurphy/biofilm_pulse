import sys
import os.path
import pandas as pd
import numpy as np
import skimage.io
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.axes
from lib import filedb
import subfig_draw_bin

sys.path += [os.path.join(os.path.dirname(__file__), "../figure_63x_sigb_histo/")]
import subfig_normalised_histos

# import subfig_indivfile_histo

# import subfig_trace
# import subfig_gradient

# import data.bio_film_data.strainmap as strainmap

this_dir = os.path.dirname(__file__)
stylefile = os.path.join(this_dir, "../figstyle.mpl")
plt.style.use(stylefile)
import lib.figure_util as figure_util
from lib import strainmap

letters = figure_util.letters # hiding first column of axis
# from lib.figure_util import dpi, strain_color, strain_label


#%% load strains
strain_to_type, type_to_strain = strainmap.load()
strain_to_type = {s: t[0] for s, t in strain_to_type.items()}
cell_types = np.unique([t for t in strain_to_type.values()])
type_to_strain = dict(zip(cell_types, [[]] * len(cell_types)))
for strain, typel in strain_to_type.items():
    type_to_strain[typel] = type_to_strain[typel] + [strain]

w = 2048
h = 1548
wh63 = 500
strains_to_plot = [
    (
        "delru_sigar_sigby",
        "Δ$\mathit{rsbRU}$ P$_{\mathit{sigB}}$-YFP",
        (
            (
                "Set_2/48hrs/JLB088_48hrs_20x_3.tif",
                ((220, 220 + h), (0, 0 + w)),  # row, cols
                20,
            ),
            (
                "Set_2/48hrs/63x/JLB088_48hrs_63x_3.tif",
                ((1548, 1548 + wh63), (1548, 1548 + wh63)),  # row, cols
                63,
            ),
        ),
    ),
    (
        "etdelru_sigar_sigby",
        "et-Δ$\mathit{rsbRU}$ P$_{\mathit{sigB}}$-YFP",
        (
            (
                "Set_2/48hrs/NEB_009_48hrs_20x_4.tif",
                ((450, 450 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_1/48hrs/63x/NEB008_48hrs_63x_4.tif",
                ((1360, 1360 + wh63), (1100, 1100 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
    # (
    #     "et_sigar_sigby",
    #     "et-WT P$_{\mathit{sigB}}$-YFP",
    #     (
    #         (
    #             "Set_1/48hrs/JLB106_48hrs_20x_3.tif",
    #             ((500, 500 + h), (0, 0 + w)),  # row, cols
    #             0,
    #         ),
    #         (
    #             "Set_1/48hrs/63x/JLB106_48hrs_63x_3.tif",
    #             ((600, 600 + wh63), (1548, 1548 + wh63)),  # row, cols
    #             0,
    #         ),
    #     ),
    # ),
    (
        "et2xqp_sigar_sigby",
        "et-2×$\mathit{rsbQP}$ P$_{sigB}$-YFP",
        (
            (
                "Test_snaps/48hrs/NEB011_48hrs_20x_5.tif",
                ((500, 500 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_2/48hrs/63x/NEB_011_48hrs_63x_3.tif",
                ((574, 574 + wh63), (820, 820 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
    (
        "etdelsigf_sigar_sigby",
        "et-Δ$\mathit{rsbRU}$-Δ$\mathit{σF}$ P$_{\mathit{sigB}}$-YFP",
        (
            (
                "Set_2/48hrs/NEB_018_48hrs_20x_2.tif",
                ((315, 315 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_2/48hrs/63x/NEB_018_48hrs_63x_3.tif",
                ((433, 423 + wh63), (423, 423 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
    (
        "et_sigar_yflay",
        "et-WT P$_{\mathit{yflA}}$-YFP",
        (
            (
                "Set_2/48hrs/NEB_024_48hrs_20x_1.tif",
                ((200, 200 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_1/48hrs/63x/NEB025_48hrs_63x_3.tif",
                ((1125, 1125 + wh63), (800, 800 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
    (
        "et_sigar_csbby",
        "et-WT P$_{\mathit{csbB}}$-YFP",
        (
            (
                "Set_2/48hrs/NEB_026_48hrs_20x_1.tif",
                ((0, 0 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_1/48hrs/63x/NEB026_48hrs_63x_1.tif",
                ((732, 732 + wh63), (1528, 1528 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
    (
        "et_sigar_sigay",
        "et-WT P$_{\mathit{sigA}}$-YFP",
        (
            (
                "Test_snaps/48hrs/NEB034_48hrs_20x_4.tif",
                ((500, 500 + h), (0, 0 + w)),  # row, cols
                0,
            ),
            (
                "Set_2/48hrs/63x/NEB_034_48hrs_63x_4.tif",
                ((190, 190 + wh63), (190, 190 + wh63)),  # row, cols
                0,
            ),
        ),
    ),
]

n_strains = len(strains_to_plot)
# fig, axes = plt.subplots(n_strains, 4)
# ax_gradnt = axes[:, 0]
# ax_gradim = axes[:, 1]
# ax_histos = axes[:, 2]
# ax_cellim = axes[:, 3]

dummyfig = plt.figure()
fig = plt.figure()
#gs = gridspec.GridSpec(n_strains, 4, width_ratios=[0.33, 0.29, 0.18, 0.2], wspace=0.12)
gs = gridspec.GridSpec(n_strains, 3, width_ratios=[0.43, 0.27, 0.3], wspace=0.12)

# Making less wide
# outer_gs = gridspec.GridSpec(2, 2,
#                             height_ratios=[1, 2.2],
#                             hspace=0.18, wspace=0.25,
#                             width_ratios=[0.7, 1])
# pic_trace_gs  = gridspec.GridSpecFromSubplotSpec(2, 1,
#                                   height_ratios=[2, 1],
#                                   subplot_spec = outer_gs[1,:],
#                                   hspace=0.03)

#ax_gradnt = np.array([plt.subplot(gs[g, 0]) for g in range(n_strains)])
ax_gradnt = np.array([matplotlib.axes.Axes(dummyfig, [0,1,2,3]) for g in range(n_strains)])
ax_gradim = np.array([plt.subplot(gs[g, 0]) for g in range(n_strains)])
ax_histos = np.array([plt.subplot(gs[g, 1]) for g in range(n_strains)])
ax_cellim = np.array([plt.subplot(gs[g, 2]) for g in range(n_strains)])


#%%%%%%%%%%%%%%%
# Plot gradients
################
dpath = "datasets/lsm700_live20x_newstrain1/gradient_summary/{0}.tsv"
legend_pos = [
    "center right",
    "upper left",
    "upper left",
    "center right",
    "center right",
    "upper left",
    "upper center",
    "lower right",
]
for i, (strain_name, label, _) in enumerate(strains_to_plot):
    df = pd.read_csv(dpath.format(strain_name), sep="\t")
    color = "blue"  # figure_util.strain_color[des_strain_map[strain].upper()]
    # figure_util.strain_label[des_strain_map[strain].upper()]
    p, = ax_gradnt[i].plot(
        df["distance"], df["mean"], color=color, label=label, linewidth=0.5
    )
    ax_gradnt[i].fill_between(
        df["distance"], df["upsem"], df["downsem"], color=color, alpha=0.4
    )
    ax_gradnt[i].set_ylim(0, 1.5)
    ax_gradnt[i].grid()
    ax_gradnt[i].set_xlim(left=0, right=150)
    ax_gradnt[i].tick_params(
        axis="x", which="both", direction="out"
    )  # , length=2, pad=0)
    ax_gradnt[i].tick_params(
        axis="y", which="both", direction="out"
    )  # , length=2, pad=0)
    # leg = ax_gradnt[i].legend(loc="upper right")
    ax_gradnt[i].set_ylabel(label.split(" ")[0])  # YFP/RFP ratio")
    # ax_gradnt[i].yaxis.label.set_color(p.get_color())
    ax_gradnt[i].tick_params(axis="y", colors=p.get_color())  # , **tkw)
    # if strain_name == "et_sigar_sigay":
    red_green_ax = ax_gradnt[i].twinx()
    lines = [p]
    labels = ["YFP/RFP"]
    for color, lab in [("red", "P$_{sigA}$-RFP"), ("green", label.split(" ")[1])]:
        df[color + "_mean"] /= 10000
        df[color + "_upsem"] /= 10000
        df[color + "_downsem"] /= 10000
        p, = red_green_ax.plot(
            df["distance"], df[color + "_mean"], color=color, label=label, linewidth=0.5
        )
        lines += [p]
        labels += [lab]
        red_green_ax.fill_between(
            df["distance"],
            df[color + "_upsem"],
            df[color + "_downsem"],
            color=color,
            alpha=0.4,
        )
        # red_green_ax.set_ylim(0, 50000)
        red_green_ax.set_ylim(0, 5)
        # red_green_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0),useOffset=False) # useMathText=True,
        red_green_ax.spines["right"].set_visible(True)
    red_green_ax.legend(lines, labels, loc=legend_pos[i], framealpha=0.7)#.set_zorder(10000)
    grand_lab = (-0.25, 0.97)
    ax_gradnt[i].text(
        grand_lab[0],
        grand_lab[1],
        letters[0] + "." + letters[i].lower(),
        va="top",
        ha="left",
        color="black",
        fontsize=figure_util.letter_font_size,
        transform=ax_gradnt[i].transAxes,
    )

ax_gradnt[-1].set_xlabel("Distance from top of biofilm (μm)")

# ax_gradnt[0].text(
#     0.001,
#     0.5,
#     "Mean ratio of P$_{X}$_YFP to P$_{trp}$ RFP",
#     va="top",
#     transform=fig.transFigure,
#     rotation=90,
# )

#%%%%%%%%%%%%%%%
# Plot Histos
################


basedir = "datasets/new_strain_snaps1/"
cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))

# only look around the mean value.
# def is_a_good_cell(v, mean=10300, std=3500):
#     if (v < mean + std) & (v > mean - std):
#         return True
#     else:
#         return False

# just exclude the small gauss
def is_a_good_cell(v, mean=10300, std=3500):
    if v > (mean - std):
        return True
    else:
        return False


cell_df["good_cell"] = cell_df["red_raw_mean"].apply(is_a_good_cell)
# def get_data_subset(df, file_df, list_of_histos, time, location, output_path):
nbins = 100
gbins = np.linspace(0, 4, nbins)
#         #("2xqp_sigar_sigby",  gchan, rchan, gbins, slice_srt_end, "2xQP", strain_color["JLB095"]),
#         ("wt_sigar_sigby",    gchan, rchan, gbins, slice_srt_end, "WT P$_{sigB}$-YFP", strain_color["JLB021"]),

df = cell_df.loc[(cell_df["good_cell"]), :]
for i, (strain_name, label, _) in enumerate(strains_to_plot):
    fids_df = file_df[
        (
            file_df["strain"].isin(type_to_strain[strain_name])
            & (file_df["time"] == 48.0)
        )
    ]
    fids = fids_df.index
    print("63x: ", label)
    print((fids_df["strain"] + fids_df["dirname"]).unique())
    print(
        len(fids),
        "images from ",
        len((fids_df["strain"] + fids_df["dirname"]).unique()),
    )
    ax_histos[i] = subfig_normalised_histos.plot_strain_fileindiv_histos(
        ax_histos[i],
        df,
        fids,
        "green_raw_meannorm",
        "red_raw_meannorm",
        0,
        100,
        gbins,
        {"color": "blue", "alpha": 0.3},
    )
    # "green_raw_mean", "red_raw_mean",
    ax_histos[i].set_ylabel("Percentage of cells")
    ax_histos[i].set_xlim(0, 3)  # gbins.max())
    ax_histos[i].set_ylim(0, 8.5)
    ax_histos[i].tick_params(
        axis="x", which="both", direction="out"
    )  # , length=2, pad=0)
    ax_histos[i].tick_params(
        axis="y", which="both", direction="out"
    )  # , length=2, pad=0)

    hisletter_lab = (0.05, 0.97)
    ax_histos[i].text(
        hisletter_lab[0],
        hisletter_lab[1],
        letters[1] + "." + letters[i].lower(),
        va="top",
        ha="left",
        color="black",
        fontsize=figure_util.letter_font_size,
        transform=ax_histos[i].transAxes,
    )

    # axhisto.yaxis.set_major_locator(mticker.MaxNLocator(nbins=3, integer=True))
ax_histos[-1].set_xlabel("Normalised cell fluorecence")


#%%%%%%%%%%%%%%%%%%
## Gradient images
##################
FP_max_min = [(0, (2 ** 16) - 1), (0, 45000), (0,1)]  # RFP  # YFP

for i, (strain_name, label, image_prop) in enumerate(strains_to_plot):
    if len(image_prop) == 0:
        continue
    grad_image, grad_region, scalebar = image_prop[0]
    path = os.path.join("datasets/lsm700_live20x_newstrain1/images", grad_image)
    ax_gradim[i] = subfig_draw_bin.get_figure(
        ax_gradim[i],
        label,
        path,
        grad_region,
        [0, 1],
        FP_max_min,
        (0, 100),  # not doing yet
        add_scale_bar=scalebar,
    )
    grand_lab = (0.03, 0.97)
    ax_gradim[i].text(
        grand_lab[0],
        grand_lab[1],
        letters[0] + "." + letters[i].lower(),
        va="top",
        ha="left",
        color="white",
        fontsize=figure_util.letter_font_size,
        transform=ax_gradim[i].transAxes,
    )
    ax_gradim[i].text(
        0.97,
        0.03,
        label,
        va="bottom",
        ha="right",
        color="white",
        fontsize=6,
        transform=ax_gradim[i].transAxes,
    )

#%%%%%%%%%%%%%%%%%%
## Cell images
##################
FP_Single_max_min = [(0, 40000), (0, 30000), (0, 1)]  # RFP  # YFP #CFP

for i, (strain_name, label, image_prop) in enumerate(strains_to_plot):
    if len(image_prop) == 0:
        continue
    cell_image, cell_region, scalebar = image_prop[1]
    path = os.path.join("datasets/new_strain_snaps1/images", cell_image)
    ax_cellim[i] = subfig_draw_bin.get_figure(
        ax_cellim[i],
        label,
        path,
        cell_region,
        [0, 1],
        FP_Single_max_min,
        (0, 100),  # not doing yet
        add_scale_bar=scalebar,
    )
    grand_lab = (0.03, 0.97)
    ax_cellim[i].text(
        grand_lab[0],
        grand_lab[1],
        letters[2] + "." + letters[i].lower(),
        va="top",
        ha="left",
        color="white",
        fontsize=figure_util.letter_font_size,
        transform=ax_cellim[i].transAxes,
    )
    ax_cellim[i].text(
        0.97,
        0.03,
        label,
        va="bottom",
        ha="right",
        color="white",
        fontsize=6,
        transform=ax_cellim[i].transAxes,
    )


#%% save
filename = "sup_transformable"
# width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.5 )
# width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=2.0)
#height = figure_util.cm2inch(24.7)[0]
height = figure_util.cm2inch(19)[0]
#width = figure_util.cm2inch(17.73)[0]
width = figure_util.cm2inch(12.0)[0]
print(width)
fig.subplots_adjust(
    left=0.01, right=0.99, top=0.99, bottom=0.05,
    hspace=0.25 # wspace=0.25)
)  

fig.set_size_inches(width, height)  # common.cm2inch(width, height))
figure_util.save_figures(fig, filename, ["png", "pdf"], base_dir=this_dir)
# figure_util.save_figures(fig, filename, ["png"], base_dir=this_dir)

