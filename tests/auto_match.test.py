
from lib.cell_tracking.auto_match import sub_array_correction
from lib.cell_tracking.auto_match import predict_next_location_simple
from lib.cell_tracking.track_data import TrackData
            
import scipy.spatial.distance

import matplotlib.pyplot as plt

import unittest
import numpy as np
import os.path

def euc_dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

class TestAutoMatchFunctions(unittest.TestCase):

    def test_sub_array_correction(self):
        CC, RR = np.meshgrid(np.arange(0,20), np.arange(0, 20))

        initial_points = np.array([ [6,12], [7, 14], [10,13] ])
        test_image = np.zeros((20,20), dtype=np.uint8)
        vals = np.arange(10, 10 + initial_points.shape[0])
        test_image[initial_points[:,0], initial_points[:,1]] = vals

        offset_r = 5
        offset_c = 10
        end_r, end_c = 15, 15
        sub_array = test_image[offset_r:end_r, offset_c:end_c]
        sub_RR = RR[offset_r:end_r, offset_c:end_c]
        sub_CC = CC[offset_r:end_r, offset_c:end_c]

        # Method one
        tr, tc = np.nonzero(sub_array>0)
        correct = np.column_stack([sub_RR[tr, tc], sub_CC[tr,tc]])

        # simpler method        
        test_points = np.column_stack([tr, tc])
        results = sub_array_correction(test_points, offset_r, offset_c)

        np.testing.assert_array_equal(results, correct)
        np.testing.assert_array_equal(correct, initial_points)
        np.testing.assert_array_equal(results, initial_points)


    def test_predict_next_location_simple(self):

        ## Load up a track file and the image pattern. 
        #td = TrackData("../../proc_data/iphox_movies/BF10_timelapse/Column_2/cell_track.json")
        #p = "../../"
        p = ""
        data_pattern = os.path.join(p, "proc_data/iphox_movies/BF10_timelapse/Column_2/cell_track.json")
        img_pattern = os.path.join(p, "proc_data/iphox_movies/BF10_timelapse/Column_2/Column_2_t{0:03}_ch00.tif")
        td = TrackData(data_pattern)


        direction = +1

        ## choose some positions and run the matcher, see if they pass. 
        cells = list(td.cells.keys())
        for cell in cells:
            print("\n cell", cell)
            #cell = cells[4]
            alive_mask = np.array(td.cells[cell]["state"]) == 1
            #print(alive_mask)
            num_pos = np.sum(alive_mask)
            if num_pos < 2:
                continue

            frames, = np.nonzero(alive_mask) # not using "where". 
            for f in frames[:-1]:
                print(f, end=", ")
                #f = 243
                this_cell = td.cells[cell]
                this_position = this_cell["row"][f], this_cell["col"][f]
                next_position = this_cell["row"][f+direction], this_cell["col"][f+direction]
                this_position

                results = predict_next_location_simple(img_pattern, [(cell, this_position)], f, direction)
                #darray = scipy.spatial.distance.cdist(results[cell], results[cell])
                #print(darray)
                mean_res = np.mean(results[cell], axis=0)
                distance = euc_dist(mean_res, next_position)
                try:
                    self.assertLess(distance, 4) 
                except:
                    print("error!")
                    print(cell, f)
                    print(results)
                    print("cal", mean_res)
                    print("ans", next_position)
                    print("dist", distance)


        
def debug_tracking():
    p = ""
    data_pattern = os.path.join(p, "proc_data/iphox_movies/BF10_timelapse/Column_2/cell_track.json")
    img_pattern = os.path.join(p, "proc_data/iphox_movies/BF10_timelapse/Column_2/Column_2_t{0:03}_ch00.tif")
    td = TrackData(data_pattern)
    direction = +1
    ## choose some positions and run the matcher, see if they pass. 
    cell = "13"
    f = 130

    #f = 243
    this_cell = td.cells[cell]
    this_position = this_cell["row"][f], this_cell["col"][f]
    next_position = this_cell["row"][f+direction], this_cell["col"][f+direction]
    this_position

    results = predict_next_location_simple(img_pattern, [(cell, this_position)], f, direction)
    print(results)
    mean_res = np.mean(results[cell], axis=0)
    print("cal", mean_res)
    import skimage.io

    fig, ax = plt.subplots(1,2, sharex=True, sharey=True)
    img0 = skimage.io.imread(img_pattern.format(f))
    img1 = skimage.io.imread(img_pattern.format(f+direction))
    ax[0].imshow(img0)
    ax[0].scatter(this_position[1], this_position[0], c="red")
    ax[1].imshow(img1)
    ax[1].scatter(next_position[1], this_position[0], c="red")
    ax[1].scatter(results[cell][:,1], results[cell][:,0],  c="blue")
    # darray = scipy.spatial.distance.cdist(results[cell], results[cell])
    # print(darray)
    # print("ans", next_position)
    # distance = euc_dist(mean_res, next_position)
    plt.show()
    


def debug_find_next_cell_location(f, image_pattern, next_image, cell_ids, trackdata, voted_centers):
    import lib.cell_tracking.cell_editor as cell_editor

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


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and (sys.argv[1] == "debug"):
        debug_tracking()
    else:
        unittest.main()
