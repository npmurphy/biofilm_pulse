import argparse
import os.path

import scipy.io
import skimage.io

from sklearn.externals import joblib
from lib import file_finder
from lib.processing.segment import segment_rf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", nargs="+")
    parser.add_argument("--model", type=str)
    parser.add_argument("--mask_name", type=str)
    parser.add_argument("--remove_cr_from_mat_path", action="store_true", default=False)
    pa = parser.parse_args()

    model = joblib.load(pa.model)

    for f in pa.files:

        im = skimage.io.imread(f)
        improc = segment_rf.get_features(im)
        segment = model.predict(improc).reshape(im.shape)

        matpath = os.path.splitext(f)[0] + ".mat"
        if pa.remove_cr_from_mat_path:
            matpath = matpath.replace("_cr.", ".")
        maskpath = file_finder.get_labeled_path(matpath, pa.mask_name)

        scipy.io.savemat(maskpath, {"image": segment})


if __name__ == "__main__":
    main()
