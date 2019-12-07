import os.path

import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import skimage.io
import skimage.transform

import lib.figure_util as figure_util
import lib.strainmap as strainmap
from lib.resolutions import PX_TO_UM_LSM700_63x as PX_TO_UM

figure_util.apply_style()

strain_map, des_strain_map = strainmap.load()


# fig = plt.figure()
fig, ax = plt.subplots(2, 1)


def prepare_image(
    image_path, scale_bar_length, sb_cp, scale_image=1, external_scale=None
):

    image = skimage.io.imread(image_path)
    print(image_path, image.shape)
    if scale_image != 1:
        image = skimage.transform.rescale(
            image, scale_image, preserve_range=True, anti_aliasing=True
        ).astype(np.uint8)
    thickness = 30  # int(60 * scale_image)
    if external_scale is not None:
        scale_image = scale_image * external_scale

    # red max
    # 61768
    # 65262
    # green max
    # 65124
    # 65525
    fl_range = {"red_min": 0, "red_max": 35000, "green_min": 0, "green_max": 25000}
    reimage = []
    for r, ch in enumerate(["red", "green"]):
        im = skimage.exposure.rescale_intensity(
            image[r],
            in_range=(fl_range[ch + "_min"], fl_range[ch + "_max"]),
            out_range=(0, 255),
        ).astype(np.uint8)
        reimage += [im]
    reimage += [reimage[1]]  # make cyan
    image = np.dstack(reimage)

    # length = scale_bar_length #/ scale_image
    print("Final scale image ", scale_image)
    print("PX to uM ", PX_TO_UM)
    print("pixels in 1 uM ", 1 / PX_TO_UM)
    print(" scaled PX to uM ", (PX_TO_UM / scale_image))
    print(" rescaled pixels in 1uM ", 1 / (PX_TO_UM / scale_image))
    print("pixels for 10 uM ", 10 / (PX_TO_UM / scale_image))
    print("dtype", image.dtype)
    outim = figure_util.draw_scale_bar(
        image,
        20,
        image.shape[1] - sb_cp,
        scale_length=scale_bar_length / (PX_TO_UM / scale_image),
        thickness=thickness,
        legend="{0} μm".format(scale_bar_length),
        fontsize=0,
    )
    return outim


this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB077", "JLB117"]]
imagedir = this_dir

images = [
    "JLB077_48hrs_center_3_1_reduced20.tif",
    "JLB117_48hrs_center_4_1_reduced20.tif",
]


letters = figure_util.letters
letter_lab = (0.07, 0.98)

for r, (strain, imgpath) in enumerate(zip(strains, images)):
    im = prepare_image(os.path.join(imagedir, imgpath), 100, 150, external_scale=0.05)
    ax[r].grid(False)
    ax[r].axis("off")
    # label = figure_util.strain_label[des_strain_map[strain].upper()]
    ax[r].imshow(
        im,
        # interpolation="bicubic")
        interpolation="none",
    )
    ax[r].text(
        0.025,
        0.99,
        letters[r],
        transform=ax[r].transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        color="white",
        fontsize=figure_util.letter_font_size,
    )


filename = os.path.join(this_dir, "sup_longspore")
width, height = figure_util.get_figsize(
    figure_util.fig_width_medium_pt, wf=1.0, hf=0.475
)
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
