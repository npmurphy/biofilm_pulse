import os
import os.path
from lib.common import read_lsm_channel
import skimage.io
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--channels', nargs="+", default=["r", "g"])
    parser.add_argument('-f', '--files', nargs="+")
    pa = parser.parse_args()

    for fn in pa.files:
        dirname = os.path.dirname(fn)
        filename = os.path.basename(fn)
        basename = ".".join(filename.split(".")[:-1])
        new_dir = os.path.join(dirname, basename)
        try:
            os.mkdir(new_dir)
        except:
            pass
        print("Converting", fn)
        for c in pa.channels:
            img = read_lsm_channel(c, fn)
            #fr = os.path.splitext(fn)[0]
            new_name = basename + "_c" + c + ".tiff"
            new_path = os.path.join(new_dir, new_name)
            print("Writting channel {0} : {1}".format(c, fn))
            skimage.io.imsave(new_path, img)
            mktime = os.stat(fn).st_mtime
            os.utime(new_path, (mktime, mktime))
