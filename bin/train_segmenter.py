import argparse
import os.path

import scipy.io
import skimage.io

from sklearn.externals import joblib
from lib import file_finder
from lib.processing.segment import segment_rf


def load_img_mask_pair(file, maskname, remove_cr=False):
    img = skimage.io.imread(file)
    matpath = os.path.splitext(file)[0] + ".mat"
    if remove_cr:
        matpath = matpath.replace("_cr.", ".")
    maskpath = file_finder.get_labeled_path(matpath, maskname)

    try:
        mask = scipy.io.loadmat(maskpath)["image"]
    except TypeError as e:
        raise FileNotFoundError("could not find", maskpath)
    return img, mask


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", nargs="+")
    parser.add_argument("--model", type=str)
    parser.add_argument("--mask_name", type=str)
    parser.add_argument("--remove_cr_from_mat_path", action="store_true", default=False)
    pa = parser.parse_args()

    model = segment_rf.get_model()

    print(pa.files)
    list_of_img_mask = [
        load_img_mask_pair(f, pa.mask_name, pa.remove_cr_from_mat_path) for f in pa.files
    ]

    train_x, train_y, test_x, test_y = segment_rf.get_training_set(list_of_img_mask)

    model.fit(train_x, train_y)

    print("score: ", model.score(test_x, test_y))

    joblib.dump(model, pa.model)


if __name__ == "__main__":
    main()
