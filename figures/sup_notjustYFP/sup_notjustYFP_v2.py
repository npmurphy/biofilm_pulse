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


fig, ax = plt.subplots(2, 3)


def prepare_image(image_path):

    image = skimage.io.imread(image_path)

    image = np.rot90(image, -1)
    length = 100
    outim = lib.figure_util.draw_scale_bar(
        image,
        20,
        image.shape[1] - 250,
        scale_length=length / PX_TO_UM,
        thickness=50,
        legend="{0}μm".format(length),
        fontsize=80,
    )
    return outim


this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB022", "JLB035"]]
# imagedir = "/media/nmurphy/BF_Data_Orange/datasets/ancient_sigw/"
imagedir = "/home/nmurphy/work/projects/bf_pulse/figures/sup_notjustYFP/sigW_fig_data"

rfponly_images = [
    "RFP_only_48hrs_center_2_channels_crop.tif",
    "RFP_only_48hrs_center_RED_60_crop.tif",
    "RFP_only_48hrs_center_GREEN_25_crop.tif",
]
sigW_images = [
    "SigW_48hrs_center_2channels_crop.tif",
    "SigW_48hrs_center_RED_60_crop.tif",
    "SigW_48hrs_center_GREEN_25_crop.tif",
]

letters = figure_util.letters
letter_lab = (0.06, 0.99)
for r, (label, strain_ims) in enumerate(zip(strains, [sigW_images, rfponly_images])):
    for i, imgpath in enumerate(strain_ims):
        im = prepare_image(os.path.join(imagedir, imgpath))
        aximg = ax[r, i]  # plt.subplot(grid[0])
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
            letters[(r * 3) + i],
            transform=aximg.transAxes,
            verticalalignment="top",
            horizontalalignment="right",
            color="white",
            fontsize=figure_util.letter_font_size,
        )


filename = os.path.join(this_dir, "sup_notjustYFP")
width, height = figure_util.get_figsize(
    figure_util.fig_width_medium_pt, wf=1.0, hf=0.64
)
fig.subplots_adjust(
    left=0.01, right=0.99, top=0.99, bottom=0.01, hspace=0.05, wspace=0.05
)
fig.set_size_inches(width, height)
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".png")
fig.savefig(filename + ".pdf")
fig.clear()
plt.close(fig)
figure_util.print_pdf_size(filename + ".pdf")
