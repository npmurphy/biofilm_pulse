import os.path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import pandas as pd
import skimage.io
from lib.resolutions import PX_TO_UM_LSM780_10x as PX_TO_UM
import lib.figure_util
import numpy as np
import lib.strainmap as strainmap


# from figure_util import dpi
import lib.figure_util as figure_util

figure_util.apply_style()

strain_map, des_strain_map = strainmap.load()


fig = plt.figure()
grid = gs.GridSpec(1, 2, width_ratios=[3, 1])
grid.update(left=0.01, right=0.98, bottom=0.11, top=0.98, hspace=0.04, wspace=0.21)
# grid.update(hspace=0.05)


def prepare_image(image_path):
    scales = {1: (0, 20), 0: (0, 100), 2: (0, 0)}  # green  # red

    image = skimage.io.imread(image_path)

    print(image.shape)
    images = [image[1, :, :], image[0, :, :], np.zeros_like(image[0, :, :])]
    images = [
        skimage.exposure.rescale_intensity(im, in_range=scales[i], out_range=(0, 255))
        for i, im in enumerate(images)
    ]
    # images = [i[1026:2056, 892:1700].copy() for i in images]
    r = 790
    images = [i[r : r + 1024, 0:1026].copy() for i in images]
    # images = [ im.astype(np.uint8) for im in images]
    # images += [ np.zeros_like(imges[-1])]
    outim = np.dstack(images)
    # outim = np.rot90(outim, 3)
    length = 100
    outim = lib.figure_util.draw_scale_bar(
        outim,
        20,
        outim.shape[1] - 200,
        scale_length=length / PX_TO_UM,
        thickness=30,
        legend="{0}μm".format(length),
        fontsize=40,
    )
    return outim


this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB022"]]
imagedir = "/media/nmurphy/BF_Data_Orange/datasets/ancient_sigw/"
biofilm_images = ["SigW_48hrs_center_3.tif"]

letters = figure_util.letters
letter_lab = (0.05, 0.99)
for i, (label, imgpath) in enumerate(zip(strains, biofilm_images)):
    im = prepare_image(os.path.join(imagedir, imgpath))
    aximg = plt.subplot(grid[0])
    # label = figure_util.strain_label[des_strain_map[strain].upper()]
    aximg.imshow(
        im,
        # interpolation="bicubic")
        interpolation="none",
    )
    # aximg.set_title(label, transform=aximg.transAxes)
    # aximg.text(
    #     0.98,
    #     0.02,
    #     label,
    #     ha="right",
    #     va="bottom",
    #     transform=aximg.transAxes,
    #     fontsize=plt.rcParams["axes.titlesize"],
    #     color="white",
    # )
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

data_plots = ["wt_sigar_sigwy"]

for c, strain in enumerate(data_plots):
    dpath = "datasets/ancient_sigw/gradient_summary/{0}.tsv"
    df = pd.read_csv(dpath.format(strain), sep="\t")
    print(df.columns)
    color = figure_util.strain_color[des_strain_map[strain].upper()]
    label = figure_util.strain_label[des_strain_map[strain].upper()]
    ax.plot(df["mean"], df["distance"], color=color, label=label, linewidth=0.5)
    ax.fill_betweenx(df["distance"], df["upsem"], df["downsem"], color=color, alpha=0.4)
# leg = ax.legend(loc="lower right")
# leg.get_frame().set_alpha(1.0)
# ax, leg = figure_util.shift_legend(ax, leg, yshift=0.10, xshift=0.1)

# ax.set_xlim(0.09, 0.29)
ax.set_ylim(150, 0)
ax.set_xlim(0, 0.4)
ax.grid(True)
ax.set_ylabel("Distance from top of biofilm (μm)", labelpad=0)
ax.set_xlabel("YFP/RFP ratio")
ax.text(
    -0.29,
    letter_lab[1],
    letters[1],
    ha="right",
    va="top",
    transform=ax.transAxes,
    fontsize=figure_util.letter_font_size,
)

filename = os.path.join(this_dir, "sup_notjustYFP")
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.75)
fig.set_size_inches(width, height)
# fig.tight_layout()
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".png")
fig.savefig(filename + ".pdf")
fig.clear()
plt.close(fig)
figure_util.print_pdf_size(filename + ".pdf")
