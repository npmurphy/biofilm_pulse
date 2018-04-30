import skimage.io
import glob
#import sys
import numpy as np
import json
import os.path

def main():
    channels = {"red": "cr", "green": "cg"}
    result = {} 
    pattern = "/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks/BF_12hoursnaps2/background/" 
    chan_means = { k: [] for k in channels.keys() }
    for channel, extension in channels.items():
        file_pat = os.path.join(pattern, "*_{}.tiff".format(extension))
        print(file_pat)
        for imgpath in glob.glob(file_pat):
            print(imgpath)
            im = skimage.io.imread(imgpath)
            meanv = im.mean()
            chan_means[channel] += [ meanv ]
            print(meanv)

    final_vals = { chan +"_bg": np.mean(chan_means[chan]) for chan in channels }
    with open("/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks/bg_values.json", "w") as fo:
        json.dump(final_vals, fo)

if __name__ == '__main__':
    #sys.argv[1]
    
    main()