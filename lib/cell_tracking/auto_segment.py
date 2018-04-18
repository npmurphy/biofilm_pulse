#from processing.cell_tracking.track_data import TrackData
import skimage.io
import skimage.filters
import skimage.morphology
import os.path
import scipy.io
# import matplotlib.pyplot as plt 
# import processing.cell_tracking.cell_editor as cell_editor
import numpy as np
#from processing.cell_tracking import cell_dimensions
#from sklearn.neighbors import KDTree
#import sys
import sklearn.cluster
import skimage.feature
#TODO remember the basis was computed on images gaused by 2. might be too much 


## The Clustering segmentation method comes from 
#processing/cell_tracking/iphox_eigen_segment.ipynb#

from sklearn.externals import joblib


def get_filtered_image(img):
    img_gauss = skimage.filters.gaussian(img, 1.1)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))


    cell_width = 12 
    cell_disc = skimage.morphology.disk(cell_width/2)

    # scell_width = 20 
    # scell_disc = skimage.morphology.disk(scell_width/2)
    #img_cont_01 = skimage.filters.rank.enhance_contrast((img_gauss_01*255).astype(np.uint8), scell_disc)

    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
    img_hat_01 = skimage.exposure.rescale_intensity(img_hat, out_range=(0, 1.0))

    # img_sobel = skimage.filters.sobel(img_gauss_01)
    # img_sobel_01 = skimage.exposure.rescale_intensity(img_sobel, out_range=(-1, 1.0))
    gamma = 1.2
    img_gauss_very = skimage.filters.gaussian(img, 2.5)
    img_gauss_very_01 = skimage.exposure.rescale_intensity(img_gauss_very, out_range=(0, 1.0))
    img_gamma = skimage.exposure.adjust_gamma(img_gauss_very_01, gamma=gamma)
    img_lap = skimage.filters.laplace(img_gamma, ksize=20)
    maxextreme = np.max([np.max(img_lap), np.abs(np.min(img_lap))])
    img_lap_01 = skimage.exposure.rescale_intensity(img_lap, in_range=(-maxextreme, maxextreme),out_range=(-1, 1.0))

    #img_filtered = np.dstack([img_gauss_01, img_cont_01, img_hat_01, img_sobel_01])
    img_filtered = np.dstack([img_gauss_01, img_hat_01, img_lap_01])
    
    local_max = skimage.feature.peak_local_max(img_hat_01, min_distance=7, threshold_rel=0.1, exclude_border=True, indices=False)
    cell_seeds = skimage.morphology.label(local_max)

    return img_filtered, cell_seeds 

def get_image_data(img):
    img_f, seeds = get_filtered_image(img)
    img_fd = img_f.reshape((np.prod(img_f.shape[0:2]), img_f.shape[2]), order="F")
    return img_fd, seeds

def make_kmeans_model(example_image):
    img_d_ks = sklearn.cluster.KMeans(2, max_iter=600)
    img_filtered_dim, _ = get_image_data(example_image)
    img_d_ks.fit(img_filtered_dim)
    return img_d_ks

def simple_clustering(img, kmeans):
    img_filtered_dim, seeds = get_image_data(img)
    labeled_img_dim = kmeans.predict(img_filtered_dim)
    nlabeled_dim_img = labeled_img_dim.reshape(img.shape[0], img.shape[1]).T
    nlabeled_dim_img = skimage.morphology.binary_erosion(nlabeled_dim_img, selem=skimage.morphology.disk(1))

    dists = scipy.ndimage.morphology.distance_transform_edt(nlabeled_dim_img)
    labeled = skimage.segmentation.watershed(image=-dists, mask=nlabeled_dim_img, markers=seeds)
    return labeled

def auto_segment(model_path, img):
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        model = make_kmeans_model(img)
        joblib.dump(model, model_path)
    return simple_clustering(img, model)    


### 
# This was part of a failed attempt to use eigen values  to 
# segment. this code might be useful later for training a model
# def get_training_data():
#     basedir="data/bio_film_data/data_local_cache/iphox_movies/testing/"
#     dataset="BB3_washed_glass_long"
#     lookat="Position004_track"
#     pattern=lookat + "_t{0:03d}_ch01.tif" 
#     image_pattern = os.path.join(basedir, dataset, lookat, pattern)
#     jet_pattern = os.path.join(basedir, dataset, lookat, lookat + "_t{0:03d}_ch01.tif.mat")
#     data_dir = os.path.dirname(jet_pattern)
#     #track_path =  os.path.join(basedir, dataset, lookat, "cell_track.json")
#     track_path =  os.path.join(basedir, dataset, lookat, "cell_segment_training.json")
#     DEBUG = True

#     trackdata = TrackData(track_path)

#     # Try using the basis to segment the cells.
#     # for all the frames with ellipses on them. 
#     image_shape = 1024
#     margin = 31
#     jet_shape = 1024 - (margin*2)
#     training_data = []
#     cells_list = trackdata.get_cells_list()
#     bad_cells_list = [ 28, 9]
#     good_cells_list =  [ g for g in cells_list if g not in bad_cells_list]
#     print(good_cells_list)
#     for frame in range(0, 400):
#         mask = np.zeros((image_shape,image_shape), dtype=np.uint8)
#         cells_here = 0
#         for cell_id in good_cells_list:
#             if trackdata.get_cell_state(frame, cell_id) != 0:
#                 cell_params = trackdata.get_cell_params(frame, cell_id)
#                 pixel = cell_dimensions.get_cell_pixels(*cell_params, (image_shape, image_shape))
#                 mask[pixel] = 1
#                 cells_here += 1
            

#         if cells_here == 0:
#             print("no cells on frame ", frame)
#             continue

#         # also get the ellipses for each cell and get the imagejets corresponding to 
#         # that. Save out this dataset. 
#         smask = mask[margin:-margin, margin:-margin]
#         print("SMASK", smask.shape)
#         image_jets = scipy.io.loadmat(jet_pattern.format(frame))["jets"] 
#         print("Mask", image_jets.shape)
#         rows, cols = np.where(smask)
#         this_frame = image_jets[rows, cols, :]
#         print(this_frame.shape)
#         training_data += [this_frame]
#         # if DEBUG == True:
#         #     #import skimage.io
#         #     image = skimage.io.imread(jet_pattern.format(frame).replace(".mat", ""))
#         #     simage = image[margin:-margin, margin:-margin]
#         #     debug = np.zeros_like(simage)
#         #     rows, cols = np.where(smask)
#         #     debug[rows,cols] = simage[rows, cols]
#         #     debug_dir = os.path.dirname(jet_pattern.format(frame))
#         #     debug_file = os.path.basename(jet_pattern.format(frame)).replace(".mat", "")
#         #     try:
#         #         os.mkdir(os.path.join(debug_dir, "debug"))
#         #     except FileExistsError as e:
#         #         pass
#         #     debug_path = os.path.join(debug_dir, "debug", debug_file)
#         #     skimage.io.imsave(debug_path, debug)
#     result = np.vstack(training_data)    
#     print(result.shape)
#     scipy.io.savemat(os.path.join(data_dir, "cell_points.mat"), {"data": result})


#def main():

    
# if __name__ == "__main__":
#     get_training_data()