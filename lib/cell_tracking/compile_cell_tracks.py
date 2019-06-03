import csv
import os.path

import numpy as np
import pandas as pd
import scipy.io
import skimage.io
import lib.cell_tracking.cell_dimensions as cell_dimensions
import re
import lib.cell_tracking.track_data as track_data

# import warnings

DEBUG = False  # True


def load_compiled_data(path, fail_silently=False):
    try:
        return pd.read_csv(path, sep="\t")
    except FileNotFoundError as e:
        if fail_silently:
            print("Compiled cell file not found, {0}".format(path))
            # warnings.warn("error ", RuntimeWarning)
            return None
    except ValueError as e:
        if fail_silently:
            print("No path given for compiled cell file")
            return None


def get_channel_of_cell(df, cell, chan):
    if not isinstance(cell, list):
        cell = [cell]

    celldf = df[df["cell_id"].isin([int(c) for c in cell])].copy()

    if len(celldf) == 0:
        return [], []

    max_frame = celldf["frame"].max()
    cells_at_max = celldf[celldf["frame"] == max_frame]["cell_id"].values
    final_id = cells_at_max[0]
    celldf = celldf.groupby(by=["frame"]).sum()
    celldf["cell_id"] = final_id
    celldf["frame"] = celldf.index
    celldf = celldf.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
    return celldf["frame"].values, celldf[chan].values
    # cell = df[df["cell_id"].isin(cell)].sort_values(by=["cell_id", "frame"])
    # return cell["frame"].values, cell[chan].values


def compile(data_pattern, td, outpath, channels, start_frame=None, end_frame=None):
    names = ["red", "green", "blue"]
    lab_channels = {names[i]: c for i, c in enumerate(channels)}
    offset_mins = track_data.parse_time(td.metadata["time_offset"])
    timestep_mins = track_data.parse_time(td.metadata["time_offset"])
    data_fields = [
        "frame",
        "time",
        "cell_id",
        "row",
        "col",
        "angle",
        "state",
        "length",
        "width",
        "g_by_r",
    ] + list(lab_channels.keys())

    with open(outpath, "w") as tsvf:
        csvw = csv.DictWriter(tsvf, data_fields, delimiter="\t")
        csvw.writeheader()

        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = td.metadata["max_frames"]
        frames = range(start_frame, end_frame)
        for frame in frames:
            print("frame, ", frame)

            chan_data = {
                lab: skimage.io.imread(data_pattern.format(frame, ch))
                for lab, ch in lab_channels.items()
            }
            chan_data["g_by_r"] = chan_data["green"] / chan_data["red"]
            img_shape = chan_data["red"].shape
            chan_keys = sorted(list(chan_data.keys()))[::-1]

            if DEBUG:
                out_pat = data_pattern.replace("images", "quatcheck")
                thisf = out_pat.format(int(frame), "")
                try:
                    os.mkdir(os.path.dirname(out_pat))
                except FileExistsError:
                    pass
                seg = np.zeros(img_shape, dtype=np.uint8)

            for cell in td.cells.keys():
                cellps = td.get_cell_properties(frame, cell)
                cell_param = td.get_cell_params(frame, cell)
                cellps["frame"] = frame
                cellps["time"] = (frame * timestep_mins) + offset_mins
                cellps["cell_id"] = cell
                cellps.pop("parent")
                cell_pixels = cell_dimensions.get_cell_pixels(*cell_param, img_shape)

                if DEBUG:
                    seg[cell_pixels] = int(cell)
                for ch in chan_keys:
                    if ch == "g_by_r":
                        bad_pixels = np.isinf(chan_data[ch][cell_pixels]) | np.isnan(
                            chan_data[ch][cell_pixels]
                        )
                        cellps[ch] = np.nanmean(chan_data[ch][cell_pixels][~bad_pixels])
                    else:
                        cellps[ch] = np.nanmean(chan_data[ch][cell_pixels])
                csvw.writerow(cellps)

            if DEBUG:
                skimage.io.imsave(thisf, seg)
