"""
Docstring
"""
import argparse
import os.path
from collections import Counter

import numpy as np
import scipy.ndimage
import skimage.feature
import skimage.io
import skimage.morphology
import skimage.segmentation

import lib.cell_tracking.cell_dimensions
from lib.cell_tracking import auto_match, cell_dimensions
from lib.cell_tracking.track_db import TrackDB


def get_cell_mask_cells(img_shape, cells):
    mask = np.zeros(img_shape, dtype=np.uint16)
    for i, cell in cells.items():
        rr, cc = lib.cell_tracking.cell_dimensions.get_cell_pixels(*cell, mask.shape)
        mask[rr, cc] = i
    return mask


def get_cell_mask_cellids(img_shape, td, cell_ids, frame):
    cells = {cell_id: td.get_cell_params(frame, cell_id) for cell_id in cell_ids}
    return get_cell_mask_cells(img_shape, cells)


def get_voted_next_cellid(cell_centers, cell_id_img):
    # print("centers", cell_centers)
    voted_ids = cell_id_img[cell_centers[:, 0], cell_centers[:, 1]]
    # print("IDS:", voted_ids)
    unique, counts = np.unique(voted_ids, return_counts=True)
    # print("unique", unique, counts)
    mx = np.argmax(counts)
    vote = int(unique[mx])
    return vote


def track_cells_from_frame(td, image_path, frame):

    now_frame = frame
    next_frame = frame + 1

    now_cells = td.get_cells_in_frame(now_frame, states=None)  # ie all
    next_cells = td.get_cells_in_frame(next_frame, states=None)  # ie all

    approved_cells = [
        cid
        for cid in next_cells
        if td.get_cell_properties(next_frame, cid)["trackstatus"]
        in ["migrated", "approved", "manual"]
    ]

    def get_row_col(frame, cid):
        e = td.get_cell_properties(frame, cid)
        return (e["row"], e["col"])

    possible_targets = set(next_cells).difference(set(approved_cells))
    source_cells = set(now_cells).difference(set(approved_cells))
    source_centers = {cid: get_row_col(now_frame, cid) for cid in source_cells}
    # get the matches and filter them by the possible targets.
    # make a dict of source cells to possible trargets
    # for cells with more than one target, calculate distance and chose the closest.

    next_cellseg = get_cell_mask_cellids((1024, 2048), td, possible_targets, next_frame)
    # skimage.io.imsave("/tmp/seg.tiff", next_cellseg)

    search_distance = 40

    next_pos = auto_match.predict_next_location_simple(
        image_path, source_centers.items(), now_frame, 1, search_w=search_distance
    )

    voted_forward_map = {
        now_cid: get_voted_next_cellid(next_centers, next_cellseg)
        for now_cid, next_centers in next_pos.items()
    }

    target_occurance = Counter(voted_forward_map.values())

    # Any cells that have multiple mappings
    cell_with_multi_in = [
        (cell, count) for cell, count in target_occurance.items() if count > 1
    ]

    # for now print it out
    print("bad news!, these cells have multiple mappings")
    print(cell_with_multi_in)

    # remove these mapping
    cells_to_remap = {
        now_cid: next_cid
        for now_cid, next_cid in voted_forward_map.items()
        if target_occurance[next_cid] == 1
    }

    for now_cid, next_cid in cells_to_remap.items():
        print(now_cid, "->", next_cid)
        td.set_cell_id(next_frame, next_cid, now_cid)
        td.set_cell_properties(next_frame, now_cid, {"trackstatus": "auto"})
    td.save()


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

    frame = args.frame

    td = TrackDB(trackdb)

    track_cells_from_frame(td, image_path, frame)


if __name__ == "__main__":
    main()
