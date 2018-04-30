import skimage.io
import scipy.io
import sys
import numpy as np

def main(mask_path):
    mask = scipy.io.loadma(mask_path)["image"].astype(np.uint8)
    mask *= 255
    skimage.io.imsave(mask_path.replace("mat", "tiff"), mask)


if __name__ == '__main__':
    mask_path = sys.argv[1]
    main(mask_path)