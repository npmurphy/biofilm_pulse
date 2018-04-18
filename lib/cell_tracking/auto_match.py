from lib.cell_tracking.track_data import TrackData
import skimage.io
import skimage.filters
import skimage.morphology
import os.path
import scipy.io
import matplotlib.pyplot as plt 
import lib.cell_tracking.cell_editor as cell_editor
import numpy as np
from lib.cell_tracking import cell_dimensions
from sklearn.neighbors import KDTree
import sys
from lib.cell_tracking import auto_segment
import shutil
import argparse
#TODO remember the basis was computed on images gaused by 2. might be too much

# Try using the basis to segment the cells. 
# for all the frames with ellipses on them. 
# get datapoints at the center of my ellipses and get the imagejet 
# also get the ellipses for each cell and get the imagejets corresponding to 
# that. Save out this dataset. 

# get the center of this cluster. 
# then try to do a distance walk that increases the KDtree query 
# optimize for a distance that gives the best fit with the cells we draw.  


def predict_next_location(jet_pattern, list_of_positions, this_jets, this_frame, next_frame):
    
    # inefficient 
    locs = np.arange(31, 1024-31)
    CC, RR = np.meshgrid(locs, locs)

    def get_jets(frame_number):
        image_jets = scipy.io.loadmat(jet_pattern.format(frame_number))["jets"] # ["max", "min"]
        return np.dstack([image_jets, RR, CC])

    if this_jets is None:
        this_jets = get_jets(this_frame)
    next_jets = get_jets(this_frame+1)

    next_data = next_jets.reshape((np.prod(next_jets.shape[0:2]), next_jets.shape[2]), order="F")
    # find a subregion to make into a tree
    #print("POS", list_of_positions)
    rows, cols = zip(*[ (r,c) for _, (r,c) in list_of_positions])
    #print(rows, cols)
    min_row, max_row = np.min(rows), np.max(rows)
    min_col, max_col = np.min(cols), np.max(cols)
    #print(min_row, max_row, min_col, max_col)
    wander = 40 
    mask = ((next_data[:,-2]<(max_row + wander)) & 
            (next_data[:,-2]>(min_row - wander)) & 
            (next_data[:,-1]>(min_col - wander)) & 
            (next_data[:,-1]<(max_col + wander)))
    smaller = next_data[mask]
 
    kdtree = KDTree(smaller)
    results = {}
    for cell_id, (cell_row, cell_col) in list_of_positions:
        target_cell = np.atleast_2d(this_jets[cell_row-31, cell_col-31, :])
        dists, indexes = kdtree.query(target_cell, 10)
        print("Distances", dists)
        hits = smaller[indexes] 
        #print(hits.shape)
        result_rows = hits[0, :, -2]
        print("I think rows are ", result_rows)
        result_cols = hits[0, :, -1]
        print("I think cols are ", result_cols)
        result = np.dstack([result_rows, result_cols])[0,:,:]
        print("This is rows and cols? ", result)
        results[cell_id] = result
    return next_jets, results


def find_out_line(next_image, cell_voted_centers):
    # img_gauss = skimage.filters.gaussian(next_image, 1.0)
    # img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
    # scell_width = 20 
    # scell_disc = skimage.morphology.disk(scell_width/2)
    #img_enhan = skimage.filters.rank.enhance_contrast(img_gauss_01, scell_disc)
    # img_enhan[img_enhan < 100]=0
    #mask = img_enhan > 100
    #labels = skimage.morphology.label(mask.astype(np.int))
    model_path = "data/bio_film_data/data_local_cache/iphox_movies/testing/BB3_washed_glass_long/Position004_track/"
    model_path = model_path + 'kmeans_2class_f150.pkl'
    rows, cols = zip(*[(vc[:,0], vc[:,1]) for (k, vc) in cell_voted_centers.items()])
    # print(rows)
    # print("NIALL", np.hstack(rows).shape)
    # mn_r, mx_r = np.hstack(rows).min(), np.hstack(rows).max()
    # mn_c, mx_c = np.hstack(cols).min(), np.hstack(cols).max()
    # margin = 40
    # print(mn_r-margin,mx_r+margin," ",  mn_c-margin, mx_c+margin)

    #mini_image = next_image[mn_r-margin:mx_r+margin, mn_c-margin:mx_c+margin]
    mini_image = next_image
    labels = auto_segment.auto_segment(model_path, mini_image)
    regions = skimage.measure.regionprops(labels)
    results = {}
    for cell_id, voted_centers in cell_voted_centers.items():
        #print(voted_centers)
        votes = labels[voted_centers[:,0], voted_centers[:,1]]
        pvotes = votes[votes>0]
        labs, counts  = np.unique(pvotes, return_counts=True)
        try:
            majority = labs[np.argmax(counts)]
        except ValueError as e:
            print("problem getting label for ", cell_id )
            continue
            #raise e 

        debug = "Votes are {0}  result was: {1} with {2}% of the vote".format(votes, majority, (np.max(counts)/len(votes))*100)
        print(debug)
        cell = regions[majority-1]
        assert(majority == cell.label)
        #print("label", majority, cell.label)
        results[cell_id] = cell_dimensions.regionprops_to_props(cell) 

    return labels, results


def debug_find_next_cell_location(f, image_pattern, next_image, cell_ids, trackdata, voted_centers):
    fig, ax = plt.subplots(1,2, sharex=True, sharey=True)
    current_image = skimage.io.imread(image_pattern.format(f))
    next_image = skimage.io.imread(image_pattern.format(f+1)) 
    ax[0].imshow(current_image)
    ax[1].imshow(next_image)
    for cell_id in cell_ids:
        current_cell = trackdata.get_cell_params(f, cell_id)
        print("Curent cell", current_cell)
        cell = cell_editor.get_cell(*current_cell, facecolor="none", edgecolor="red", linewidth=2)
        ax[0].add_patch(cell)
        ax[1].scatter(voted_centers[cell_id][:,1], voted_centers[cell_id][:,0], c="red")
    plt.show()
    sys.exit()


def debug_next_cell_segmentation(segment_image, image, voted_centers, out_cells):
    fig, ax = plt.subplots(1,2, sharex=True, sharey=True)
    
    ax[0].imshow(image)
    ax[1].imshow(segment_image)
    for cell_id in voted_centers:
        ax[1].scatter(voted_centers[cell_id][:,1], voted_centers[cell_id][:,0], c="red")

        if out_cells is not None:
            current_cell = out_cells[cell_id]
            cell = cell_editor.get_cell(*current_cell, facecolor="none", edgecolor="red", linewidth=2)
            ax[1].add_patch(cell)
    plt.show()
    sys.exit()

def guess_next_cell_gui(trackdata, cell_id, this_frame, jet_pattern, image_pattern):
    prev_frame = this_frame - 1
    print("Frame: {0} to {1}".format(prev_frame, this_frame))

    if trackdata.get_cell_state(prev_frame, cell_id) <= 0: 
        raise ValueError("Cell {0} has a non positive state in frame {1}".format(cell_id, prev_frame))
    
    cell_params = trackdata.get_cell_params(prev_frame, cell_id)
    print("PREV loc ", cell_params)
    cell_col, cell_row = (int(np.round(i)) for i in cell_params[0])

    cell_centers = [(cell_id, (cell_row, cell_col))]
    print("CELL CENTERS", cell_centers)
    next_jet = None # if this is slow we can store the jet and pass it in
    next_jet, voted_centers = predict_next_location(jet_pattern, cell_centers, next_jet, prev_frame, this_frame)
    ## voted centers are comming out here in x, y order
    image = skimage.io.imread(image_pattern.format(this_frame)) 
    print("VOTED CENTERS", voted_centers) 
        
    _, out_cells = find_out_line(image, voted_centers)
    print("new geuss RESULT", out_cells)

    for cell_id, cell_params in out_cells.items():
        trackdata.set_cell_params(this_frame, cell_id, cell_params)
        trackdata.set_cell_state(this_frame, cell_id, 1)
    return trackdata

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--file_list', type=str)
    # parser.add_argument('--cell_list', type=str)
    # #parser.add_argument('--gauss', type=float, default=None)
    # parser.add_argument('--patch_radius', type=int, default=10)

    # args = parser.parse_args()

    basedir="data/bio_film_data/data_local_cache/iphox_movies/testing/"
    dataset="BB3_washed_glass_long"
    lookat="Position004_track"
    pattern=lookat + "_t{0:03d}_ch01.tif" 
    image_pattern = os.path.join(basedir, dataset, lookat, pattern)
    jet_pattern = os.path.join(basedir, dataset, lookat, lookat + "_t{0:03d}_ch01.tif.mat")
    #track_path =  os.path.join(basedir, dataset, lookat, "cell_track.json")
    track_path =  os.path.join(basedir, dataset, lookat, "cell_track.json")

    #next_frame_matching_debug = True
    next_frame_matching_debug = False
    next_frame_segmentation_debug = False 
    #next_frame_segmentation_debug = True
    next_frame_see_ellipse = False

    trackdata = TrackData(track_path)

    #cell_ids = ["2","8", "9", "28", "30"]
    # 9 is weird 
    cell_ids = ["53"]
    #cell_ids = ["4", "2","8", "28", "30", "7"]
    #start_frame = 150
    start_frame = 239
    stop_frame = 360

    def get_cell_centers(f, cell_id):
        cell_params = trackdata.get_cell_params(f, cell_id)
        cell_col, cell_row = (int(np.round(i)) for i in cell_params[0])
        return (cell_row, cell_col)

    next_jet = None
    for f in range(start_frame, stop_frame):
        print("Frame: {0} to {1}".format(f, f+1))
        cell_centers = [ (cell_id, get_cell_centers(f, cell_id)) 
                            for cell_id in cell_ids
                                if trackdata.get_cell_state(f, cell_id) > 0]
        next_jet, voted_centers = predict_next_location(jet_pattern, cell_centers, next_jet, f, f+1)
        next_image = skimage.io.imread(image_pattern.format(f+1)) 
        
        if next_frame_matching_debug:
            debug_find_next_cell_location(f, image_pattern, next_image, cell_ids, trackdata, voted_centers)

        if next_frame_segmentation_debug:
            model_path = "data/bio_film_data/data_local_cache/iphox_movies/testing/BB3_washed_glass_long/Position004_track/"
            model_path = model_path + 'kmeans_2class_f150.pkl'
            labels = auto_segment.auto_segment(model_path, next_image)
            debug_next_cell_segmentation(labels, next_image, voted_centers, None)

        labels, out_cells = find_out_line(next_image, voted_centers)

        if next_frame_see_ellipse:
            debug_next_cell_segmentation(labels, next_image, voted_centers, out_cells)

        for cell_id, cell_params in out_cells.items():
            if trackdata.get_cell_state(f+1, cell_id) == 0:
                trackdata.set_cell_params(f+1, cell_id, cell_params)
                trackdata.set_cell_state(f+1, cell_id, 1)
        
        try:
            save_path = track_path.replace("ck.js", "ck_f{0}.js".format(f+1))
            shutil.move(track_path, save_path)
        except FileNotFoundError as e:
            pass
        
        trackdata.save(track_path)
    
    
if __name__ == "__main__":
    main()