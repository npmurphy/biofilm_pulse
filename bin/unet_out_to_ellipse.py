"""
Docstring
"""
import skimage.morphology
import skimage.feature
import skimage.segmentation
import skimage.io
import scipy.ndimage

import numpy as np
import os.path

import lib.cell_tracking.cell_dimensions
from lib.cell_tracking.track_db import TrackDB


def get_ellipses(probs, mask):
    dist = scipy.ndimage.morphology.distance_transform_edt(probs > 0.98)
    local_max = skimage.feature.peak_local_max(dist, indices=False, min_distance=2)
    local_max = skimage.morphology.dilation(local_max, selem=skimage.morphology.disk(3))
    maxim_l, n = scipy.ndimage.label(local_max)
    wsh = skimage.segmentation.watershed(-probs, maxim_l, mask=probs > 0.98)

    wsh = skimage.morphology.remove_small_objects(wsh, min_size=100)

    regions = skimage.measure.regionprops(wsh)

    ellipses = []
    for region in regions:
        el = lib.cell_tracking.cell_dimensions.regionprops_to_props(region)
        # el_sets = lib.cell_tracking.cell_dimensions.props_to_mplellipse(*el)
        ellipses += [el]
    return ellipses


def shift_ellipse(cell_props, c_offset, r_offset):
    center, length, width, angle = cell_props
    return (center[0] + c_offset, center[1] + r_offset), length, width, angle

def get_cell_mask_cells(img_shape, cells):
    mask = np.zeros(img_shape, dtype=np.uint16)
    for i, cell in cells.items():
        rr, cc = lib.cell_tracking.cell_dimensions.get_cell_pixels(*cell, mask.shape)
        mask[rr,cc] = i
    return mask

def get_cell_mask_cellids(img_shape, td, cell_ids, frame):
    cells = {cell_id: td.get_cell_params(frame, cell_id) for cell_id in cell_ids} 
    return get_cell_mask_cells(img_shape, cells)
    
def main():
    trackdb = "/home/nmurphy/Dropbox/work/projects/bf_pulse/bf10_track.sqllite"
    filepaths = {
        "basedir": "/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/",
        "dataset": "BF10_timelapse",
        "lookat": "Column_2",
    }
    image_path = "{basedir}/{dataset}/{lookat}/{lookat}_t{{0:03d}}_ch00.tif".format(
        **filepaths
    )

    frame = 55
    width = 64
    c_start, c_end = 0, 16
    r_start, r_end = 0, 16

    this_image = image_path.format(frame)
    # image = skimage.io.imread(this_image)
    segmt = skimage.io.imread(
        os.path.join(
            os.path.dirname(this_image),
            "simp",
            os.path.basename(this_image).replace("_ch00", ""),
        )
    )
    td = TrackDB(trackdb)
    r_offset = r_start * 64
    c_offset = c_start * 64
    rows = slice(r_offset, r_end * width)
    cols = slice(c_offset, c_end * width)
    ellipses = get_ellipses(segmt[0, rows, cols], segmt[1, rows, cols])
    #print(ellipses)

    ellipses_shift = { i : shift_ellipse(e, r_offset, c_offset) for (i, e) in enumerate(ellipses)}

    pre_cells = td.get_cells_in_frame(frame, states=None) # ie all
    print(pre_cells)
    if pre_cells:
        old_seg = get_cell_mask_cellids(segmt.shape[1:], td, pre_cells, frame)
        new_seg = get_cell_mask_cells(segmt.shape[1:], ellipses_shift)
        rr, cc = np.where((old_seg>0) & (new_seg>0))
        overlap = new_seg[rr,cc]
        cells = np.unique(overlap)
        counts = np.bincount(new_seg[rr,cc])
        for c in cells:
            print(c, counts[c])
            if counts[c] > 50:
                ellipses_shift.pop(c)

    td.add_new_ellipses_to_frame(ellipses_shift.values(), frame)
    td.save()


if __name__ == "__main__":
    main()