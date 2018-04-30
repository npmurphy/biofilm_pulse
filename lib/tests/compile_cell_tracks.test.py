
import unittest

import numpy as np
#from track_data import TrackData
#'from lib.trimport track_data
from lib.cell_tracking import compile_cell_tracks
#from lib.cell_tracking import cell_tracker

import networkx as nx

class CompileCellTRackTest(unittest.TestCase): 
    def test_get_channel_of_cell_existing(self):
        test_data = "test_data/compiled.tsv"
        compdata = compile_cell_tracks.load_compiled_data(test_data)
        #print(compdata)
        cell_present = "2"
        known_x = [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]
        known_vals = np.array([ 2174.4516129 ,  2390.4       ,  2630.37398374,  2191.38461538,
            2472.        ,  2487.68421053,  2569.43283582,  2743.13253012,
            2624.09090909,  2749.25443787,  2602.23655914,  2695.23566879,
            2836.45360825,  2839.59183673,  2660.30456853,  2696.80382775,
            2710.59649123])
        x_vals, r_vals =  compile_cell_tracks.get_channel_of_cell(compdata, cell_present, "red")
        np.testing.assert_allclose(x_vals, known_x)
        np.testing.assert_allclose(r_vals, known_vals)

    def test_get_channel_of_cell_notexisting(self):
        test_data = "test_data/compiled.tsv"
        compdata = compile_cell_tracks.load_compiled_data(test_data)
        #print(compdata)
        cell_present = "9"
        known_x = []
        known_vals = []
        x_vals, r_vals =  compile_cell_tracks.get_channel_of_cell(compdata, cell_present, "red")
        # np.testing.assert_allclose(x_vals, known_x)
        # np.testing.assert_allclose(r_vals, known_vals)
        self.assertEqual(x_vals, known_x)
        self.assertEqual(r_vals, known_vals)



if __name__ == '__main__':
    unittest.main()