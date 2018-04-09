import argparse
import scipy.io 
import skimage.morphology
import numpy as np

from lib.file_finder import get_paths

def make_background_mask(f, pa):
    basename, dirbase = get_paths(f)
    data = scipy.io.loadmat(dirbase + "_biofilmmask.mat")
    mask = data["image"].astype(np.bool_)
    ## this makes the biofilm bigger so we will acidentally include less 
    mask = skimage.morphology.binary_dilation(mask, skimage.morphology.disk(20))
    mask = ~mask 
    mask[500:, :] = 0 # just look at the top half
    scipy.io.savemat(dirbase + "_background.mat", {"image": mask})
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') #, help="this expects LSM files")
    pa = parser.parse_args()

    for f in pa.files:
        print(f)
        make_background_mask(f, pa)


if __name__ == '__main__':
    main()