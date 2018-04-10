import argparse
import util.file_finder
import scipy.io
import scipy.ndimage
import os.path
import numpy as np

if __name__ == "__main__":
    bfm_lab = "biofilmmask"
    edg_lab = "edgemask"
    bot_lab = "bottommask"
    dst_lab = "distmap"
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs="+")
    parser.add_argument('--filled', type=str, default=edg_lab)
    parser.add_argument('--magnification', type=str, default="63")
    parser.add_argument('--tag', type=str, default="")
    pa = parser.parse_args()

    if pa.magnification == "63":
        from resolutions import PX_TO_UM_LSM700_63x as PX_TO_UM
    elif pa.magnification == "10":
        from resolutions import PX_TO_UM_LSM780_10x as PX_TO_UM
    elif pa.magnification == "20":
        from resolutions import PX_TO_UM_LSM700_20x as PX_TO_UM
    elif pa.magnification == "63-LSM780":
        from resolutions import PX_TO_UM_LSM780_63x as PX_TO_UM
    else:
        print("NOT a vaild magnification value")
        PX_TO_UM = 1.0


    for lsm_file in pa.files:
        print("Distmap: {0}".format(lsm_file))
        base_dir = os.path.dirname(lsm_file)
        base_file = os.path.basename(lsm_file)

        base_no_ext = os.path.splitext(base_file)[0]
        base_no_ext_tag = base_no_ext
        if pa.tag:
            base_no_ext_tag  += "_" + pa.tag

        base_fn = os.path.join(base_dir, base_no_ext, base_no_ext_tag + ".mat")

        fn = util.file_finder.insert_dir_in_path(base_no_ext, lsm_file)

        biofilm_path = util.file_finder.get_labeled_path(base_fn, bfm_lab)
        distmap_path = util.file_finder.get_labeled_path(base_fn, dst_lab)
        edge_path    = util.file_finder.get_labeled_path(base_fn, pa.filled)

        biofilm_mask = scipy.io.loadmat(biofilm_path)["image"]
        edge_mask = scipy.io.loadmat(edge_path)["image"]

        distmap = scipy.ndimage.morphology.distance_transform_edt(edge_mask)
        distmap = distmap * PX_TO_UM # 0.05 # convert to microns
        distmap_mask = distmap * biofilm_mask

        try:
            dat = scipy.io.loadmat(distmap_path)
            _ = dat["image"] # trigger the type error
        except FileNotFoundError as error:
            dat = {}
        except TypeError as error: # scipy stopped raising a FNF error!
            dat = {}
        savename = "distmap_masked" if pa.filled == edg_lab else "distbot_masked"
        #, "distmap_unmasked" : distmap.astype(np.float32)
        data = {savename: distmap_mask.astype(np.float32)}
        dat.update(data)
        scipy.io.savemat(distmap_path, dat, do_compression=True)
