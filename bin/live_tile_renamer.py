
import shutil 
import os.path
import glob 
import skimage.io
import numpy as np
#import skimage.io.imread()

def make_joined_image(red_path):
    red_img = skimage.io.imread(red_path)
    green_img = skimage.io.imread(red_path.replace("ch00", "ch02"))
    joinchans = np.dstack([red_img, green_img, np.zeros_like(red_img)])
    return joinchans


def main():
    data_dir="/Users/npm33/bf_pulse/proc_data/iphox_live_gradient_checks"
    dset="BF_12hoursnaps2"

    rename = {"ch00": "cr", "ch01":"cp", "ch02":"cg"}

    timepoint_dirs = glob.glob(os.path.join(data_dir, dset, "delRU/*_timepoint"))
    for tp_dir in timepoint_dirs:
        #time = 
        time_dir = os.path.basename(tp_dir)
        time = time_dir.split("_")[0]
        images = glob.glob(os.path.join(tp_dir, "*_ch00.tif"))
        for red_path in images:

            base_name = os.path.basename(red_path).replace("_ch00.tif", "")
            base_name = base_name.replace("_", "")

            new_file_name = "delRU_{0}_{1}".format(time, base_name)
            datadir_path = os.path.join(tp_dir, new_file_name)

            joined_image = make_joined_image(red_path)
            skimage.io.imsave(datadir_path+".tiff", joined_image) 

            try:
                os.mkdir(datadir_path)
            except FileExistsError as e:
                pass
            
            for inchan, outchan in rename.items():
                old_name = os.path.join(red_path.replace("ch00", inchan))
                new_name = os.path.join(datadir_path, "{0}_{1}.tiff".format(new_file_name, outchan))
                shutil.move(old_name, new_name)


if __name__ == '__main__':
    main()