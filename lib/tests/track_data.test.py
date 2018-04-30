import unittest

from lib.cell_tracking.track_data import TrackData
import lib.cell_tracking.track_data as track_data
from lib.cell_tracking import cell_dimensions
from lib.cell_tracking import cell_tracker

import networkx as nx

class TrackDataTest(unittest.TestCase): 
    def test_final_decentants(self):
        test_tree = [(0, 1), (0, 4), (1, 2), (1,5), (2,14), (1,3), (4,6), (5,8), (5,7), (7,9), (7,10), (7, 11), (11, 12), (11,13)]
        tree = nx.DiGraph()
        for p, c in test_tree:
            tree.add_edge(p, c)
        #nx.draw_networkx(tree, pos=track_data.hierarchy_pos(tree,0), with_labels=True)
        #plt.show()
        final = track_data.get_final_decendents(tree, 5)
        self.assertEqual(final, [8, 9, 10, 12, 13])


    def test_time_parser(self):
        tests = [(1, 31, "1h31m"), (None, 14, "14m"), (4, None, "04h"), (3,0, "3h0m")]

        for hour, mins, time_string in tests:
            mins = 0 if mins is None else mins
            hour = 0 if hour is None else hour
            ans = hour*60 + mins 
            test = track_data.parse_time(time_string)
            self.assertAlmostEqual(ans, test)
        
if __name__ == '__main__':
    unittest.main()

