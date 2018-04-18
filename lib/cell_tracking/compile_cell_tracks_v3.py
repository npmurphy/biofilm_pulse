import csv
import os.path
from collections import OrderedDict
from glob import glob

import numpy as np
import pandas as pd
import parse
import scipy.io
import scipy.ndimage
import argparse
#import tifffile
import skimage.io
from lib.cell_tracking.track_data import TrackData
import lib.cell_tracking.cell_dimensions as cell_dimensions
DEBUG = False #True

def load_compiled_data(path):
    if path is None:
        return None
    if os.path.splitext(path)[1] == ".tsv":
        try:
            return pd.read_csv(path, sep="\t")
        except FileNotFoundError as e:
            return None
    else:
        return None
    # elif os.path.splitext(path)[1] == "h5":
    #     pd.read_hdf(path, dir)

def get_channel_of_cell(df, cell, chan):
    print(df.columns)
    try: 
        _ = len(cell)
    except TypeError: 
        cell = [cell]

    celldf = df[df["cell_id"].isin([int(c) for c in cell])].copy()
    max_frame = celldf["frame"].max()
    #print("mf ", max_frame)
    cells_at_max = celldf[celldf["frame"]==max_frame]["cell_id"].values
    #print(cells_at_max)
    #if cells_at_max
    #print("cm ", cells_at_max)
    final_id = cells_at_max[0]
    celldf = celldf.groupby(by=["frame"]).sum()
    celldf["cell_id"] = final_id
    celldf["frame"] = celldf.index
    celldf = celldf.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
    return celldf["frame"].values, celldf[chan].values
    # cell = df[df["cell_id"].isin(cell)].sort_values(by=["cell_id", "frame"])
    # return cell["frame"].values, cell[chan].values

def compile(data_pattern, track_data, outpath, channels):
    names = ["red", "green", "blue"]
    lab_channels = {names[i]:c for i, c in enumerate(channels)}
    data_fields = ["frame", "cell_id", "row", "col", "angle", "state", "length", "width", "g_by_r"] + list(lab_channels.keys())

    with open(outpath, 'w') as tsvf:
        csvw = csv.DictWriter(tsvf, data_fields, delimiter='\t')
        csvw.writeheader()

        for frame in range(track_data.metadata["max_frames"]):
            print("frame, ", frame)
            
            chan_data = { lab: skimage.io.imread(data_pattern.format(frame, ch)) for lab, ch in lab_channels.items()}
            chan_data["g_by_r"] = chan_data["green"]/chan_data["red"]
            img_shape = chan_data["red"].shape
            chan_keys = sorted(list(chan_data.keys()))[::-1]

            if DEBUG :
                out_pat  = data_pattern.replace("images", "quatcheck")
                thisf = out_pat.format(int(frame), "")
                try:
                    os.mkdir(os.path.dirname(out_pat))
                except FileExistsError:
                    pass
                seg = np.zeros(img_shape, dtype=np.uint8)

            for cell in track_data.cells.keys():
                cellps = track_data.get_cell_properties(frame, cell)
                cell_param = track_data.get_cell_params(frame, cell)
                cellps["frame"] = frame
                cellps["cell_id"] = cell
                cellps.pop("parent")
                cell_pixels = cell_dimensions.get_cell_pixels(*cell_param, img_shape )

                # cell_pixels = cell_dimensions.get_cell_pixels((cellps["col"],cellps["row"]), 
                #                                                 cellps["length"], cellps["width"], 
                #                                                 cellps["angle"], img_shape )
                if DEBUG:
                    seg[cell_pixels] = int(cell)
                for ch in chan_keys:
                    #     print("cell", cell, "ratio nans: ", np.sum(np.isnan(chan_data[ch][cell_pixels])))
                    # if ("r" == ch) and (np.sum(chan_data[ch][cell_pixels]==0)>0):
                    #     print("cell", cell, "zeros: ", np.sum(chan_data[ch][cell_pixels]==0))
                    #     print("cell", cell, "red nan: ", np.sum(np.isnan(chan_data[ch][cell_pixels]==0)))
                    #     #print("cell", cell, "zeros: ", np.sum(chan_data[ch][cell_pixels]==0)
                    #     X = True
                    if (ch == "g_by_r"):
                        bad_pixels = np.isinf(chan_data[ch][cell_pixels]) | np.isnan(chan_data[ch][cell_pixels])
                        cellps[ch] = np.nanmean(chan_data[ch][cell_pixels][~bad_pixels])
                        # cell_
                        # print("cell", cell, "ratio inf: ", np.sum(np.isinf(chan_data[ch][cell_pixels])))
                        # print("cell", cell, "ratio nans: ", np.sum(np.isnan(chan_data[ch][cell_pixels])))
                    else:
                        cellps[ch] = np.nanmean(chan_data[ch][cell_pixels])


                csvw.writerow(cellps)

            if DEBUG:
                skimage.io.imsave(thisf, seg)
    #return pd.read_csv(outpath, sep="\t")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_pattern', type=str, required=True)
    parser.add_argument('--trackdata', type=str, required=True)
    #parser.add_argument('--cells', nargs="+", type=int, default=[])
    parser.add_argument('--out_file', type=str, required=True) 
    parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])
    pa = parser.parse_args()
        
    trackdata = TrackData(pa.trackdata)
    print("channels ", pa.channels)
    compile(pa.image_pattern, trackdata, pa.out_file, pa.channels)



if __name__ == "__main__":
    main()
