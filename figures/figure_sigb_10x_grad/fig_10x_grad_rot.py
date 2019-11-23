import os.path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import pandas as pd
import skimage.io

import lib.strainmap as strainmap


import lib.figure_util as figure_util

figure_util.apply_style()

strain_map, des_strain_map = strainmap.load()


letter_lab = (0.05, 0.95)

fig = plt.figure()
grid = gs.GridSpec(3, 2, width_ratios=[3, 1.1])  # , height_ratios=[1.0, 0.8])
grid.update(left=0.0000000, right=0.97, bottom=0.1, top=0.98, hspace=0.04, wspace=0.2)
# grid.update(hspace=0.05)

this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB021", "JLB088", "JLB039"]]
biofilm_images = [
    "SigB_48hrs_center_1_1_100615_sect.jpg",
    "delRU_48hrs_3_6_100615sect.jpg",
    "delQP_48hrs_2_5_100615_sect.jpg",
]


letters = figure_util.letters
for i, (label, imgpath) in enumerate(zip(strains, biofilm_images)):
    im = skimage.io.imread(os.path.join(this_dir, "images", imgpath))
    aximg = plt.subplot(grid[i, 0])
    # label = figure_util.strain_label[des_strain_map[strain].upper()]
    aximg.imshow(
        im,
        # interpolation="bicubic")
        interpolation="none",
    )
    # aximg.set_title(label, transform=aximg.transAxes)
    aximg.text(
        0.98,
        0.02,
        label,
        ha="right",
        va="bottom",
        transform=aximg.transAxes,
        fontsize=plt.rcParams["axes.titlesize"],
        color="white",
    )
    aximg.grid(False)
    aximg.axis("off")
    aximg.text(
        letter_lab[0],
        letter_lab[1],
        letters[i],
        transform=aximg.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        color="white",
        fontsize=figure_util.letter_font_size,
    )

ax = plt.subplot(grid[:, 1])

data_plots = ["wt_sigar_sigby", "delru_sigar_sigby", "delqp_sigar_sigby"]

for c, strain in enumerate(data_plots):
    dpath = "datasets/LSM780_10x_sigb/gradient_summary/{0}.tsv"
    df = pd.read_csv(dpath.format(strain), sep="\t")
    print(df.columns)
    color = figure_util.strain_color[des_strain_map[strain].upper()]
    label = figure_util.strain_label[des_strain_map[strain].upper()]
    ax.plot(df["mean"], df["distance"], color=color, label=label, linewidth=0.5)
    ax.fill_betweenx(df["distance"], df["upsem"], df["downsem"], color=color, alpha=0.4)

leg = ax.legend(loc="lower right")
leg.get_frame().set_alpha(1.0)
ax, leg = figure_util.shift_legend(ax, leg, yshift=0.10, xshift=0.1)

ax.set_xlim(0.09, 0.29)
ax.set_ylim(150, 0)
ax.set_ylabel("Distance from top of biofilm (μm)", labelpad=0)
ax.set_xlabel("YFP/RFP ratio")
ax.text(
    -0.29,
    1.0,
    letters[3],
    ha="right",
    va="top",
    transform=ax.transAxes,
    fontsize=figure_util.letter_font_size,
)

filename = os.path.join(this_dir, "fig_10x_grad")
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.8)
fig.set_size_inches(width, height)
# fig.tight_layout()
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".png")
fig.savefig(filename + ".pdf")
fig.clear()
plt.close(fig)
figure_util.print_pdf_size(filename + ".pdf")

