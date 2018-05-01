import skimage.io
import glob
#import sys
import numpy as np
import argparse
import json
import os.path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--directories', type=str, nargs="+")
    parser.add_argument('-o', '--output', type=str)
    pa = parser.parse_args()

    channels = {"red": "cr", "green": "cg"}
    result = {} 
    for directory in pa.directories: 
        chan_means = { k: [] for k in channels.keys() }
        for channel, extension in channels.items():
            file_pat = os.path.join(directory, "*_{0}.tiff".format(extension))
            print(file_pat)
            for imgpath in glob.glob(file_pat):
                print(imgpath)
                im = skimage.io.imread(imgpath)
                meanv = im.mean()
                chan_means[channel] += [ meanv ]
                print(meanv)

    final_vals = { chan +"_bg": np.mean(chan_means[chan]) for chan in channels }
    with open(pa.output, "w") as fo:
        json.dump(final_vals, fo)


if __name__ == '__main__':
    #sys.argv[1]
    
    main()