import os.path

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import skimage.io
import skimage.transform

import lib.figure_util as figure_util
import lib.strainmap as strainmap
from lib.resolutions import PX_TO_UM_LSM780_63x as PX_TO_UM

figure_util.apply_style()

strain_map, des_strain_map = strainmap.load()


fig = plt.figure()
grid = gs.GridSpec(2, 2)


def prepare_image(
    image_path, scale_bar_length, sb_cp, scale_image=1, external_scale=None
):

    image = skimage.io.imread(image_path)
    if scale_image != 1:
        image = skimage.transform.rescale(
            image, scale_image, preserve_range=True, anti_aliasing=True
        ).astype(np.uint8)
    thickness = 30  # int(60 * scale_image)
    if external_scale is not None:
        scale_image = scale_image * external_scale

    # length = scale_bar_length #/ scale_image
    print("Final scale image ", scale_image)
    print("PX to uM ", PX_TO_UM)
    print("pixels in 1 uM ", 1 / PX_TO_UM)
    print(" scaled PX to uM ", (PX_TO_UM / scale_image))
    print(" rescaled pixels in 1uM ", 1 / (PX_TO_UM / scale_image))
    print("pixels for 10 uM ", 10 / (PX_TO_UM / scale_image))
    outim = figure_util.draw_scale_bar(
        image,
        20,
        image.shape[1] - sb_cp,
        scale_length=scale_bar_length / (PX_TO_UM / scale_image),
        thickness=thickness,
        legend="{0} μm".format(scale_bar_length),
        fontsize=40,
    )
    return outim


this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB021", "JLB098"]]
imagedir = "/media/nmurphy/BF_Data_Orange/proc_data/root_data"

big_image = ["JLB021_48hrs_tile_scan_1_new_bright_10xReduction.tif"]
small_images = ["JLB021_48hrs_root_1_63x_3.tif", "JLB098_48hrs_root_1_63x_2.tif"]

letters = figure_util.letters
letter_lab = (0.07, 0.98)

## Big Image
im = prepare_image(
    os.path.join(imagedir, big_image[0]), 100, 400, external_scale=0.1
)  # , scale_image=(10, 10, 1))
axbig = plt.subplot(grid[0, 0:2])
axbig.grid(False)
axbig.axis("off")
# label = figure_util.strain_label[des_strain_map[strain].upper()]
axbig.imshow(
    im,
    # interpolation="bicubic")
    interpolation="none",
)
axbig.text(
    0.025,
    0.99,
    letters[0],
    transform=axbig.transAxes,
    verticalalignment="top",
    horizontalalignment="right",
    color="white",
    fontsize=figure_util.letter_font_size,
)


for r, (label, strain_ims) in enumerate(zip(strains, small_images)):
    im = prepare_image(os.path.join(imagedir, strain_ims), 20, 230, scale_image=0.5)
    aximg = plt.subplot(grid[1, r])
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
        letters[1 + r],
        transform=aximg.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        color="white",
        fontsize=figure_util.letter_font_size,
    )


filename = os.path.join(this_dir, "sup_roots")
width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=0.7)
fig.subplots_adjust(
    left=0.01, right=0.99, top=0.99, bottom=0.01, hspace=0.02, wspace=0.01
)
fig.set_size_inches(width, height)
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".png")
fig.savefig(filename + ".pdf")
fig.clear()
plt.close(fig)
figure_util.print_pdf_size(filename + ".pdf")
