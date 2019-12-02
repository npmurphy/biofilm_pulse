"""
Docstring
"""
import skimage.morphology
# import skimage.feature
# import skimage.segmentation
import skimage.io
#import scipy.ndimage
import scipy.io

import numpy as np
#import os.path

import lib.cell_tracking.cell_dimensions
from lib.cell_tracking.track_db import TrackDB


def proc_image(img):
    gimg = skimage.filters.gaussian(img, sigma=1.2).astype(np.float32)
    ri_img = skimage.exposure.rescale_intensity(
        gimg, in_range="image", out_range=(0, 1)
    )
    return ri_img


def make_target_images(frame, im_shape, td):
    cell_ids = td.get_cells_in_frame(frame, states=["there", "divided"])

    centers = np.zeros(im_shape, dtype=np.uint8)
    mask = np.zeros(im_shape, dtype=np.uint8)

    for cell_id in cell_ids:
        cell = td.get_cell_params(frame, cell_id)
        rr, cc = lib.cell_tracking.cell_dimensions.get_cell_pixels(*cell, mask.shape)
        mask[rr, cc] = 1
        centers[int(np.round(cell[0][1])), int(np.round(cell[0][0]))] = 1

    centers = skimage.morphology.dilation(centers, skimage.morphology.disk(2))
    targets = np.dstack([mask, centers])
    return targets


def creat_data_sets_steps(im, size=64, rotations=4, step=64):
    im = np.atleast_3d(im)
    dims = im.shape[-1]
    sliceup = skimage.util.view_as_windows(im, (size, size, dims), step=step)

    Xlist = []
    out_put_shape = (dims, size, size)

    def reshape(r, c, i):
        rotated = np.rot90(sliceup[r, c, 0, :, :, :], k=i, axes=(0, 1))
        swapped = np.empty(out_put_shape)
        for d in range(dims):
            swapped[d, :, :] = rotated[:, :, d]
        return swapped

    grid_r, grid_c = sliceup.shape[:2]
    cords = [(r, c) for c in range(grid_c) for r in range(grid_r)]

    for i in range(rotations):
        al_the_ims = [reshape(r, c, i) for r, c in cords]
        Xlist += [np.stack(al_the_ims, axis=0)]

    return np.vstack(Xlist), sliceup.shape


def appender(accum_data, new_data):
    if accum_data is None:
        accum_data = new_data.copy()
    else:
        accum_data = np.vstack([accum_data, new_data])
    return accum_data


# def get_cell_mask_cellids(img_shape, td, cell_ids, frame):
#     cells = {cell_id: td.get_cell_params(frame, cell_id) for cell_id in cell_ids}
#     return get_cell_mask_cells(img_shape, cells)


def main():
    trackdb = "/home/nmurphy/Dropbox/work/projects/bf_pulse/bf10_track.sqllite"
    filepaths = {
        "basedir": "/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/",
        "dataset": "BF10_timelapse",
        "lookat": "Column_2",
    }
    frames = {
        50: ((0, 16), (13, 23)),
        51: ((0, 16), (13, 16)),
        52: ((0, 16), (13, 16)),
        53: ((0, 16), (13, 16)),
        54: ((0, 16), (13, 16)),
        55: ((0, 16), (13, 16)),
    }
    image_path = "{basedir}/{dataset}/{lookat}/{lookat}_t{{0:03d}}_ch00.tif".format(
        **filepaths
    )

    td = TrackDB(trackdb)

    w = 64
    X_train = None
    Y_train = None

    for frame, (rows, cols) in frames.items():
        c_start, c_end = cols
        r_start, r_end = rows

        im = proc_image(skimage.io.imread(image_path.format(frame)))
        targets = make_target_images(frame, im.shape[:2], td)

        train_sub_section = im[r_start * w : r_end * w, c_start * w : c_end * w]
        train_sub_section_label = targets[
            r_start * w : r_end * w, c_start * w : c_end * w, :
        ]

        frame_X_train, _ = creat_data_sets_steps(
            train_sub_section, size=w, rotations=4, step=32
        )
        X_train = appender(X_train, frame_X_train)
        frame_Y_train, _ = creat_data_sets_steps(
            train_sub_section_label, size=w, rotations=4, step=32
        )
        Y_train = appender(Y_train, frame_Y_train)

    scipy.io.savemat("training_50-55_1.mat", {"train_X": X_train, "train_Y": Y_train})


if __name__ == "__main__":
    main()
