from hypothesis import given, example
from hypothesis.strategies import text, tuples, floats, integers
import unittest

import numpy as np

from track_data import TrackData
from processing.cell_tracking import cell_dimensions
from processing.cell_tracking import cell_tracker

import skimage.io
import argparse
import cell_dimensions
import scipy.optimize
import numpy as np
    
from scipy import interpolate
    
import skimage.exposure
import skimage.filters
import skimage.morphology


def test_fit_cell_3():
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse
    test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106//mean5/img_{:03d}_r.tif"
    initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    guess_cell = np.array([470., 123, 10, 5, 73])

    image = skimage.io.imread(test_pattern.format(39))
    image = exagerate_image(image)

    fig, ax = plt.subplots(1, 1)
    e1 = Ellipse(*initial_cell, facecolor="none", edgecolor="blue")
    ax.add_patch(e1)
    new_cell = fit_cell_3(image, initial_cell, guess_cell)
    
    # pix = cell_dimensions.get_cell_pixels(*new_cell, image.shape)
    # image[pix] = 255//2
    ax.imshow(image, cmap=plt.cm.hot)

    print(new_cell)
    e2 = Ellipse(*new_cell, facecolor="none", edgecolor="green")
    ax.add_patch(e2)
    # ax.set_ylim(180, 60)
    # ax.set_xlim(350, 600)
    plt.show()

def test_fit_cell():
    import matplotlib.pyplot as plt
    #import cell_dimensions
    from matplotlib.patches import Ellipse
    test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106//mean5/img_{:03d}_r.tif"
    #test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/images/img_{:03d}_r.tif"
    #startframe = 39
    #cellid = 3
    #trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    #td = TrackData(trackpath)
    #initial_cell = td.get_cell_params(startframe, cellid)
    # this is x, y
    initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    print(initial_cell)
    #initial_cell

    image = skimage.io.imread(test_pattern.format(39))
    img_gauss = skimage.filters.gaussian(image, 1.1)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
    cell_disc = skimage.morphology.disk(7.5/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
    image = skimage.exposure.rescale_intensity(img_hat, out_range=(0, 255)).astype(np.uint8)
    #image = np.invert(image)

    # pix = cell_dimensions.get_cell_pixels(*initial_cell, image.shape)
    # image = np.zeros_like(image)
    # image[pix] = 255

    fig, ax = plt.subplots(1, 1)
    e1 = Ellipse(*initial_cell, facecolor="none", edgecolor="blue")
    ax.add_patch(e1)
    #new_cell, scores, pmap = fit_cell_2(image, initial_cell)
    new_cell = fit_cell_2(image, initial_cell)
    
    # pix = cell_dimensions.get_cell_pixels(*new_cell, image.shape)
    # image[pix] = 255//2
    ax.imshow(image, cmap=plt.cm.hot)

    print(new_cell)
    e2 = Ellipse(*new_cell, facecolor="none", edgecolor="green")
    ax.add_patch(e2)
    # ax.set_ylim(180, 60)
    # ax.set_xlim(350, 600)
    plt.show()

def test_gui_interpolate():
    trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    td = TrackData(trackpath)
    cell_id = 9
    print(td.cells["9"]["length"])
    ntd = gui_interpolate(td, cell_id, 385)
    print(ntd.cells.keys())
    print(ntd.cells["9"]["length"])

def test_interpolate_tracks():
    import matplotlib.pyplot as plt
    #startframe = 39
    cell_id = 3
    trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    td = TrackData(trackpath)
    #initial_cell = td.get_cell_params(startframe, cellid)
    # this is x, y
    #initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    st = 24
    ed = 176
    interped = interpolate_tracks(td, cell_id, st, ed)
    
    cell_states = np.array(td.cells[str(cell_id)]["state"])
    known_states = cell_states > 0
    known_states[:st] = False
    known_states[ed+1:] = False
    known_frames, = np.where(known_states)
    points = np.array(td.cells[str(cell_id)]["length"])[known_frames]

    plt.plot(np.arange(st, ed, 1), interped[2,st:ed])
    plt.plot(known_frames, points, "o", color="red")
    plt.show()
    #initial_cell
    
def view_angle_discontinuity_corrections(orig, computed, new_orig):
    import matplotlib.pyplot as plt

    sample_frames = np.linspace(0, 100, num=len(orig)).astype(int)
    fig, ax = plt.subplots(1,1)
    
    ax.plot(sample_frames, orig, "o-", label="input", markersize=20)
    ax.plot(sample_frames, computed, "^-", label="smoothed")
    ax.plot(sample_frames, new_orig, "s-", label="make_like_input")
    ax.legend()
    plt.show()


       
def view_trace_plot(all_frames, key_frames, inputs, computed, infered):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1,1)
    ax.plot(key_frames, inputs,   "o-", label="input", markersize=10)
    ax.plot(key_frames, computed, "^-", label="inputs_after_inference")
    ax.plot(all_frames, infered, ".-", label="infered")
    ax.legend()
    plt.show()
       
       

class TestCellTrackers(unittest.TestCase):
    def test_angle_dicontinuity_anticlockwise(self):
        inputs = np.deg2rad([ 10, 50, 70, 80, -85, -50, -20, -5, 5, 10])
        expected = np.deg2rad([10, 50, 70, 80, 95, 130, 160, 175, 185, 190])
        smoothed = cell_tracker.angle_discontinuity_smoother(inputs)
        inputs_comp = [cell_dimensions.limit_angle(a) for a in smoothed]
        #np.set_printoptions(precision=2, suppress=True)
        # print("Input", np.rad2deg(anticlockwise))
        # print("reconvert", np.rad2deg(corr_anti_ccheck_clock))
        # print("smoothed", np.rad2deg(smoothed))
        # print("expected", np.rad2deg(expected))
        #view_angle_discontinuity_corrections(inputs, smoothed, inputs_comp)
        np.testing.assert_allclose(inputs_comp, inputs)
        np.testing.assert_allclose(smoothed, expected)

    def test_angle_dicontinuity_anticlockwise_360(self):
        anticlockwise = np.deg2rad([ 10, 50, 70, -85, -50, -20, -5, 10, 40, 70, -80, -60, -30, -10, 0, 20, 30])
        corr_anti_clock = cell_tracker.angle_discontinuity_smoother(anticlockwise)
        check_anticlock = np.array([cell_dimensions.limit_angle(a) for a in corr_anti_clock])
        #view_angle_discontinuity_corrections(anticlockwise, corr_anti_clock, check_anticlock)
        np.testing.assert_allclose(anticlockwise, check_anticlock, rtol=1e7, atol=1e-7)

    def test_angle_dicontinuity_clockwise(self):
        clockwise = np.deg2rad([10, -10, -45, -80, -90,   80,   60,   20,    5,    0, -10, -30])
        expected  = np.deg2rad([10, -10, -45, -80, -90, -100, -120, -160, -175, -180, -190, -210])
        corr_clock = cell_tracker.angle_discontinuity_smoother(clockwise)
        check_clock = [cell_dimensions.limit_angle(a) for a in corr_clock]
        #view_angle_discontinuity_corrections(clockwise, corr_clock, check_clock)
        np.testing.assert_allclose(corr_clock, expected)
        np.testing.assert_allclose(clockwise, check_clock, atol=1e-7)
    
    def test_angle_dicontinuity_clockwise_then_anti_clock(self):
        inputs   = np.deg2rad([10, -10, -45, -80, -90,   80,   60,   20,    5,    0, -10,   -30,  -10,    0,   20,   30,   50,   70,  -85, -50, -20 ])
        expected = np.deg2rad([10, -10, -45, -80, -90, -100, -120, -160, -175, -180, -190, -210, -190, -180, -160, -150,  -130, -110, -85, -50, -20 ])
        smoothing = cell_tracker.angle_discontinuity_smoother(inputs)
        check_input = [cell_dimensions.limit_angle(a) for a in smoothing]
        #view_angle_discontinuity_corrections(inputs, smoothing, check_input)
        #np.set_printoptions(precision=2, suppress=True)
        # print("Input", np.rad2deg(inputs))
        # print("reconvert", np.rad2deg(check_input))
        # print("smoothed", np.rad2deg(smoothing)[15:])
        # print("expected", np.rad2deg(expected)[15:])
        np.testing.assert_allclose(smoothing, expected)
        np.testing.assert_allclose(check_input, inputs, atol=1e-7)


    def test_interpolate_tracks_angles(self):
        maxframes = 100
        td = TrackData("./nothing.json", maxframes=maxframes)
        td.cells["1"] = td.get_empty_entry()
        # between 90 and -90
        inputs   = np.deg2rad([10, -10, -45, -80, -90,   80,   60,   20,    5,    0, -10,   -30,  -10,    0,   20,   30,   50,   70,  -85, -50, -20 ])
        interpolated_on = np.deg2rad([10, -10, -45, -80, -90, -100, -120, -160, -175, -180, -190, -210, -190, -180, -160, -150,  -130, -110, -85, -50, -20 ])
        input_frames = np.linspace(0, maxframes-1, len(inputs)).astype(np.int)
        all_frames = np.arange(0, maxframes)

        cell = {"state":1, "angle": 0}
        for i, f in enumerate(input_frames):
            cell["angle"] = inputs[i]
            td.set_cell_properties(f, "1", cell)

        ntd = cell_tracker.gui_interpolate(td, "1", maxframes-1)
        result = np.array(ntd.cells["1"]["angle"])
        
        #view_trace_plot(all_frames, input_frames, inputs, result[input_frames], result)
        np.testing.assert_allclose(result[input_frames], inputs)

    



if __name__ == '__main__':
    unittest.main()
