import unittest

from track_data import TrackData
import track_data
from processing.cell_tracking import cell_dimensions
from processing.cell_tracking import cell_tracker

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


if __name__ == '__main__':
    unittest.main()

