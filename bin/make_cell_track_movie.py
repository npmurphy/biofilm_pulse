import os
import os.path
import numpy as np

from matplotlib.patches import Ellipse

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
import skimage.io
import skimage.morphology

from processing.cell_tracking import cell_dimensions
from processing.cell_tracking.track_data import TrackData

def get_ellipse_params(cell_data):
    #fr = df[df["frame"] == frame].to_dict(orient="records")[0]
    return (cell_data["col"], cell_data["row"]), cell_data["length"], cell_data["width"], cell_data["angle"]

def bit16_to_bit8(im):
    imr = skimage.exposure.rescale_intensity(im[:,:,0], in_range=(0, 30000), out_range=(0,255)).astype(np.uint8)
    img = skimage.exposure.rescale_intensity(im[:,:,1], in_range=(0, 40000), out_range=(0,255)).astype(np.uint8)
    imb = skimage.exposure.rescale_intensity(im[:,:,2], in_range=(0, 6897), out_range=(0,255)).astype(np.uint8)
    imx = np.dstack([imr, img, imb]) #np.zeros_like(imr)])
    return imx

def get_image(image_pattern, frame, channels):
    images = [ skimage.io.imread(image_pattern.format(frame, ch)) for ch in channels ]
    #images = [ skimage.filters.gaussian(im, sigma=3, preserve_range=True).astype(np.uint16) for im in images]
    #images = [ skimage.filters.gaussian(im, sigma=3) for im in images]
    rescales = {
        "r": (0, 30000),
        "g": (0, 40000),
        "b": (0, 6897) }

    for ch, i in zip(channels, range(len(images))):
        images[i] = skimage.exposure.rescale_intensity(images[i],
                                                        in_range=rescales[ch], 
                                                        out_range=(0,255)).astype(np.uint8)

    if len(images) < 3:
        images += [np.zeros_like(images[0])]
    imx = np.dstack(images)
    return imx

def make_movie(df, td, image_pattern, output_pattern, channels, cell):
    cell_lin = td.get_cell_lineage(cell)
    print("lineage", cell_lin)
    celldf = df[df["cell_id"].isin(cell_lin)].sort_values(by=["cell_id", "frame"]).copy()

    just_living = celldf[celldf["state"]>0]
    start = just_living["frame"].min()
    print("st", start)
    end = just_living["frame"].max()

    cell_data = just_living[just_living["frame"] == start].to_dict(orient="records")[0]
    center = (cell_data["col"], cell_data["row"])

    print("Cetner is",center)
        
    fig =  plt.figure()
    fig.set_size_inches(10,10)
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 0.25, 0.25])
    aximg = plt.subplot(gs[0])
    axplt = plt.subplot(gs[1])
    axdif = plt.subplot(gs[2])
    axes = [aximg, axplt, axdif]
    artists = [None, None, None] 

    #channels = ["r", "g", "b"]
    color_look = {"r":"red", "g":"green", "b":"blue"}

    for i in range(start, end):
        print(i)
        all_cell_data = just_living[just_living["frame"] == i].to_dict(orient="records")
        print(all_cell_data)
        cell_data = just_living[just_living["frame"] == i].to_dict(orient="records")[0] 
        cell = cell_data["cell_id"]
        print("cuurent cell", cell)
        print("cell:", cell_data)
        
        current_image = get_image(image_pattern, i, channels) 
        current_ellipse = get_ellipse_params(cell_data)
        #center = current_ellipse[0]
        window = 100
        if artists[0] is None:
            print("no image making one")
            artists[0] = aximg.imshow(current_image)
            aximg.set_xlim(center[0]-window, center[0]+window)
            aximg.set_ylim(center[1]+window, center[1]-window)
        else:
            print("updating image")
            artists[0].set_data(current_image)
            #aximg.draw_artist(artists[0])

        print(artists) 
        if artists[1] is None and cell_data["state"]>0:
            print("adding ellipse")
            artists[1] = Ellipse(*current_ellipse, edgecolor="white", alpha=0.5, facecolor="none")
            aximg.add_patch(artists[1])
        elif cell_data["state"] == 0:
            print("removing ellipse")
            if artists[1] is not None:
                a = artists[1]
                a.remove()
                artists[1] = None

        else:
            print("changing ellipse")
            artists[1] = cell_dimensions.set_mplellipse_props(artists[1], *current_ellipse)
            aximg.draw_artist(artists[1])

        time = (i*10)/60
        if artists[2] is not None:
            artists[2].remove()
        artists[2] = axplt.axvspan(time-0.1, time+0.1, color="grey", alpha=0.4) 
        
        #for ax, art in zip(axes, artists):
        #    ax.draw_artist(art)

        # aximg.annotate(str(cell_data["local_num"]), 
        #                xy=(cell_data["col"], cell_data["row"]),
        #                xytext=(cell_data["col"]+50,cell_data["row"]+50 ), 
        #                color="yellow")


        for chan in channels:
            color = color_look[chan]
            axplt.plot((celldf["frame"]*10)/60, celldf[chan], color=color, linestyle="-", marker=".")

        axplt.set_xlabel("hours")

        # axplt.set_ylim(bottom=0)
        # axplt.plot(cell_data["frame"], cell_data["red"], color="blue", linestyle="-", marker="*")
        # axplt.plot(cell_data["frame"], cell_data["green"], color="blue", linestyle="-", marker="*")
        # rate_of_change = np.diff(this_celldf["green"])
        # axdif.plot(this_celldf["frame"][1:], rate_of_change, color="green", linestyle="-", marker=".")
        # if i > 0:
        #     axdif.plot(cell_data["frame"], rate_of_change[int(cell_data["frame"])-1], color="blue", linestyle="-", marker="*")
        fig.canvas.draw_idle()
        fig.savefig(output_pattern.format(i), dpi=300)
        #fig.clear()
        #fig.close()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--dataset", type=str)
    parser.add_argument('-t', "--trackdata", type=str)
    parser.add_argument('-i', "--image_pattern", type=str)
    parser.add_argument('-o', "--output_pattern", type=str)
    parser.add_argument('-c', "--cell", type=int)
    parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])
    arguments = parser.parse_args()

    #path = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/sp8_movies/del_fast_slow/time_lapse_sequence/fast_img_2_106/compiled.tsv"
    df = pd.read_csv(arguments.dataset, sep="\t")
    #df["rg"] = df["g"]/df["r"]
    #df["rb"] = df["b"]/df["r"]
    td = TrackData(arguments.treedata)

    try:
        os.mkdir(os.path.dirname(arguments.output_pattern))
    except FileExistsError as e:
        pass

    make_movie(df, td, arguments.image_pattern, arguments.output_pattern,
                 arguments.channels, arguments.cell)


if __name__ == '__main__':
    main()
