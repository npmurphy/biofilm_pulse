"""
Docstring
"""
import argparse
import skimage.morphology
import skimage.feature
import skimage.segmentation
import skimage.io
import scipy.ndimage

import numpy as np
import os.path

import lib.cell_tracking.cell_dimensions
from lib.cell_tracking.track_db import TrackDB
from lib.cell_tracking import auto_match, cell_dimensions


def get_ellipses(probs, seeds):
    # dist = scipy.ndimage.morphology.distance_transform_edt(probs > 0.98)
    # local_max = skimage.feature.peak_local_max(dist, indices=False, min_distance=2)
    # local_max = skimage.morphology.dilation(local_max, selem=skimage.morphology.disk(3))
    # maxim_l, n = scipy.ndimage.label(local_max)
    wsh = skimage.segmentation.watershed(-probs, seeds, mask=probs > 0.98)

    wsh = skimage.morphology.remove_small_objects(wsh, min_size=100)

    regions = skimage.measure.regionprops(wsh)

    ellipses = {}
    for region in regions:
        el = lib.cell_tracking.cell_dimensions.regionprops_to_props(region)
        # el_sets = lib.cell_tracking.cell_dimensions.props_to_mplellipse(*el)
        ellipses[region.label] = el
    return ellipses


def shift_ellipse(cell_props, c_offset, r_offset):
    center, length, width, angle = cell_props
    return (center[0] + c_offset, center[1] + r_offset), length, width, angle


def get_cell_mask_cells(img_shape, cells):
    mask = np.zeros(img_shape, dtype=np.uint16)
    for i, cell in cells.items():
        rr, cc = lib.cell_tracking.cell_dimensions.get_cell_pixels(*cell, mask.shape)
        mask[rr, cc] = i
    return mask


def get_cell_mask_cellids(img_shape, td, cell_ids, frame):
    cells = {cell_id: td.get_cell_params(frame, cell_id) for cell_id in cell_ids}
    return get_cell_mask_cells(img_shape, cells)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", type=int, required=True)
    args = parser.parse_args()

    trackdb = "/home/nmurphy/Dropbox/work/projects/bf_pulse/bf10_track.sqllite"
    filepaths = {
        "basedir": "/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/",
        "dataset": "BF10_timelapse",
        "lookat": "Column_2",
    }
    image_path = "{basedir}/{dataset}/{lookat}/{lookat}_t{{0:03d}}_ch00.tif".format(
        **filepaths
    )

    td = TrackDB(trackdb)

    now_frame = args.frame
    next_frame = now_frame + 1
    # width = 64
    # c_start, c_end = 0, 16
    # r_start, r_end = 0, 16

    now_image = image_path.format(now_frame)
    next_image = image_path.format(next_frame)

    now_cells = td.get_dataframe_of_cell_properties_in_frame(now_frame)
    next_cells = td.get_dataframe_of_cell_properties_in_frame(next_frame)

    # if a cell is tracked in the next frame remove it from the now set
    next_cells_done_already = next_cells["cell_id"].values
    now_cells = now_cells.loc[~now_cells["cell_id"].isin(next_cells_done_already), :]

    source_centers = now_cells.set_index("cell_id")[["row", "col"]].to_dict(
        orient="index"
    )
    source_centers = {k: (v["row"], v["col"]) for k, v in source_centers.items()}

    search_distance = 40

    next_pos = auto_match.predict_next_location_simple(
        image_path, source_centers.items(), now_frame, 1, search_w=search_distance
    )

    segmented = skimage.io.imread(
        os.path.join(
            os.path.dirname(next_image),
            "model3",
            os.path.basename(next_image).replace("_ch00", ""),
        )
    )

    center_labels = np.zeros_like(segmented[0, :, :], dtype=np.uint16)
    for cell_id, position in next_pos.items():
        center_labels[position[:, 0], position[:, 1]] = cell_id

    # r_offset = r_start * 64
    # c_offset = c_start * 64
    # rows = slice(r_offset, r_end * width)
    # cols = slice(c_offset, c_end * width)
    ellipses = get_ellipses(segmented[0, :, :], center_labels)
    # segmt[1, rows, cols])
    # print(ellipses)

    # ellipses_shift = {
    #     i: shift_ellipse(e, r_offset, c_offset) for (i, e) in enumerate(ellipses)
    # }

    # pre_cells = td.get_cells_in_frame(frame, states=None)  # ie all
    # print(pre_cells)
    # if pre_cells:
    #     old_seg = get_cell_mask_cellids(segmt.shape[1:], td, pre_cells, frame)
    #     new_seg = get_cell_mask_cells(segmt.shape[1:], ellipses_shift)
    #     rr, cc = np.where((old_seg > 0) & (new_seg > 0))
    #     overlap = new_seg[rr, cc]
    #     cells = np.unique(overlap)
    #     counts = np.bincount(new_seg[rr, cc])
    #     for c in cells:
    #         print(c, counts[c])
    #         if counts[c] > 50:
    #             ellipses_shift.pop(c)

    td.add_new_ellipses_to_frame(ellipses, next_frame, {"trackstatus": "auto"})
    td.save()


if __name__ == "__main__":
    main()
