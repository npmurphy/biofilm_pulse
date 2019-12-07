import skimage.io
import skimage.exposure
import skimage.morphology
import scipy.io
import numpy as np

from lib.resolutions import PX_TO_UM_LSM700_63x as PX_TO_UM_63
from lib.resolutions import PX_TO_UM_LSM700_20x as PX_TO_UM_20
from lib.figure_util import draw_scale_bar


def process_fp(im, ROI, min_fp, max_fp, scale_down):
    lim = im.copy()
    lim[im < min_fp] = 0
    # print(min_fp, max_fp)

    rescale = skimage.exposure.rescale_intensity(
        lim, in_range=(min_fp, max_fp), out_range=(0, 255)
    ).astype(np.uint8)
    cuted = rescale[ROI]
    new_size = tuple(int(np.floor(i * scale_down)) for i in cuted.shape)
    scaled = skimage.transform.resize(cuted, new_size, order=1) * 255
    return scaled.astype(np.uint8)


def out_line_inclusion_zone_and_edge(img_path, slice_start, slice_stop, roi):
    distmap = scipy.io.loadmat(img_path.replace(".tiff", "_distmap.mat"))[
        "distmap_masked"
    ].astype(np.float32)
    msk = (distmap > slice_start) & (distmap < slice_stop)
    erode = skimage.morphology.binary_erosion(msk, selem=skimage.morphology.disk(3))
    mask = msk & (~erode)
    bfmask = distmap > 0
    bf_erode = skimage.morphology.binary_erosion(
        bfmask, selem=skimage.morphology.disk(3)
    )
    bf_edge = bfmask & (~bf_erode)
    return (
        mask[roi[0][0] : roi[0][1], roi[1][0] : roi[1][1]],
        bf_edge[roi[0][0] : roi[0][1], roi[1][0] : roi[1][1]],
    )


def get_figure(
    ax, name, impath, roi, chans, FP_max_min, slicel, add_scale_bar=0, **kwargs
):
    slice_srt, slice_end = slicel
    im = skimage.io.imread(impath)
    print(impath)
    print("MEAN:", im[:, :, 1].mean())
    # print("MEAN+2std:", im[:, :, 1].mean() + 2 * im[:, :, 1].std())
    print("Median/Maximum", np.median(im[:, :, 1].flatten() / im[:, :, 1].max()))
    print("Median:", np.median(im[:, :, 1].flatten()))
    print("Maximum:", im[:, :, 1].max())
    scale_down = 0.25
    images = [0, 0, 0]
    # outline, edge = out_line_inclusion_zone_and_edge(impath, slice_srt, slice_end, roi)
    for c in range(3):
        cim = np.zeros(im.shape[:2], dtype=np.uint8)
        if c in chans:
            cim = im[:, :, c]

        rois = (slice(roi[0][0], roi[0][1]), slice(roi[1][0], roi[1][1]))
        if c == 1:
            # this was ok, but et-WT still too dark
            # low = im[:,:,1].mean() - 2*im[:,:,1].std()
            # high = im[:,:,1].max()
            low = 0
            high = 7 * np.mean(
                im[:, :, 1].flatten()
            ) 
            if "63" in impath:
                high = 8 * np.mean(
                im[:, :, 1].flatten()
            ) 
            print("SCALE:", high)
            FP_max_min = (FP_max_min[0], (low, high), FP_max_min[2])

        images[c] = process_fp(
            cim, rois, FP_max_min[c][0], FP_max_min[c][1], scale_down
        )

        #     # print("S", images[c].shape)
        # else:
        #     rois = (roi[0][1] - roi[0][0], roi[1][1] - roi[1][0])

        # im = skimage.exposure.rescale_intensity(im, in_range=(fl_range[ch + "_min"], fl_range[ch + "_max"]), out_range=(0,255)).astype(np.uint8)

    # imchans += [im.astype(np.uint8)]

    if add_scale_bar == 20:
        length = 100
        PX_TO_UM = PX_TO_UM_20 / scale_down
        pos_r_c = (30, 330)
        width = 30
        fs = 42

    elif add_scale_bar == 63:
        PX_TO_UM = PX_TO_UM_63 / scale_down
        length = 5
        width = 10
        pos_r_c = (10, 80)
        fs = 16

    img = np.dstack(images)
    # img[outline, :] = [ 255, 255, 255]
    # img[edge, :] = [ 255, 255, 0]
    # img = np.rot90(img, 3)
    if add_scale_bar:
        print("making scale bar")
        img = draw_scale_bar(
            img,
            *pos_r_c,
            (length / PX_TO_UM),
            width,
            "{0}μm".format(length),
            fontsize=0, #fs
        )
    ax.imshow(img, interpolation="none", aspect=1)
    # ax.set_title(name)
    ax.grid(False)
    ax.axis("off")

    return ax
