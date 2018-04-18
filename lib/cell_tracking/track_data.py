import json
import shutil 
import datetime
import networkx as nx
from lib.cell_tracking import cell_dimensions

from typing import Dict

class TrackData(object):
    _default_states = {
        "0": "NE",
        "1": "growing",
        "2": "divided",
        "3": "disapeared",
        "4": "sporulating",
        "5": "spore"}

    def __init__(self, path, maxframes=None):
        try:
            with open(path, "r") as fo:
                loaded = json.load(fo)
                self.cells = loaded["cells"] #: Dict(str: Dict(str, ))
                self.metadata = loaded["metadata"]
                self.states = {v: int(k) for k, v in self.metadata["states"].items()}
        except FileNotFoundError as e:
            self.metadata = {
                    "max_frames": maxframes,
                    "states": self._default_states }
            self.states = {v: int(k) for k, v in self.metadata["states"].items()}
            self.cells = {}


    def save(self, path):
        ext = '.{:%Y-%m-%d_%H-%M}'.format(datetime.datetime.now())
        try:
            shutil.move(path, path + ext)
        except FileNotFoundError as e:
            pass
        with open(path, "x") as fo:
            data = {"cells": self.cells,
                    "metadata": self.metadata}
            json.dump(data, fo, indent=True, sort_keys=True)

    
    def get_cell_params(self, frame, cell_id:str):
        #cell_id = str(cell_id)
        center = (self.cells[cell_id]["col"][frame], 
                  self.cells[cell_id]["row"][frame])
        length = self.cells[cell_id]["length"][frame]
        width = self.cells[cell_id]["width"][frame]
        angle = self.cells[cell_id]["angle"][frame]
        return center, length, width, angle
    
    def set_cell_params(self, frame, cell_id:str, cell_props):
        center, length, width, angle = cell_props 
        #cell_id = str(cell_id)
        self.cells[cell_id]["row"][frame] = center[1]
        self.cells[cell_id]["col"][frame] = center[0]
        self.cells[cell_id]["length"][frame] = length
        self.cells[cell_id]["width"][frame] = width
        self.cells[cell_id]["angle"][frame] = angle
        #return center, length, width, angle
    
    def blank_cell_params(self, frame, cell_id:str):
        #cell_id = str(cell_id)
        self.cells[cell_id]["row"][frame] = 0
        self.cells[cell_id]["col"][frame] = 0
        self.cells[cell_id]["length"][frame] = 0
        self.cells[cell_id]["width"][frame] = 0
        self.cells[cell_id]["angle"][frame] = 0
        self.cells[cell_id]["state"][frame] = 0
        self.cells[cell_id]["parent"] = 0
        #return center, length, width, angle

    def get_cells_list(self):
        #return [int(k) for k in self.cells.keys()]
        return [k for k in self.cells.keys()]
    
    def get_final_decendants(self, cell):
        tree = self.make_tree()
        return get_final_decendents(tree, cell)

    def does_cell_exist(self, cell_id:str):
        return cell_id in self.cells.keys()

    def get_empty_entry(self):
        num_frames = self.metadata["max_frames"]
        cell = {}
        cell["parent"] = "0"
        cell["row"] = [0] * num_frames
        cell["col"] = [0] * num_frames
        cell["angle"] = [0] * num_frames
        cell["width"] = [0] * num_frames
        cell["length"] = [0] * num_frames
        cell["state"] = [0] * num_frames
        return cell

    def copy_cell_info_from_frame(self, cell_id:str, source_frame, target_frame):
        for key in self.cells[cell_id].keys():
            if key == "parent":
                continue
            self.cells[cell_id][key][target_frame] = self.cells[cell_id][key][source_frame]

    def create_cell_if_new(self, cell_id:str):
        if not self.does_cell_exist(cell_id):
            self.cells[str(cell_id)] = self.get_empty_entry()

    def get_cell_state(self, frame, cell_id:str):
        return self.cells[str(cell_id)]["state"][frame]
    
    def set_cell_state(self, frame, cell_id:str, state):
        self.cells[str(cell_id)]["state"][frame] = state
    
    def set_cell_properties(self, frame, cell_id:str, properties):
        for key, val in properties.items():
            try:
                self.cells[cell_id][key][frame] = val
            except IndexError as e:
                print("Failed to set frame {0} of cell {1} key {2}".format(frame, cell_id, properties))
                raise e

    #def clear_cell_params_after_from_frame(self, frame, cell_id, end_frame=None):


    
    def get_cell_properties(self, frame, cell_id:str, properties=[]):
        if properties == []:
            properties = self.cells[cell_id].keys()

        def get_params(cells, cell_id:str, key, frame):
            if type(cells[cell_id][key]) == list:
                return cells[cell_id][key][frame] 
            else:
                return cells[cell_id][key]

        return { k: get_params(self.cells, cell_id, k, frame) for k in properties}

    def extend_max_frames(self, new_max):
        for cell_id in self.cells.keys():
            for key in self.cells[cell_id].keys():
                if key == "parent":
                    continue
                old_len = len(self.cells[cell_id][key])
                diff = new_max - old_len
                self.cells[cell_id][key].extend([0] * diff)
        self.metadata["max_frames"] = new_max
    
    
    def set_parent_of(self, child:str, parent:str):
        self.cells[child]["parent"] = parent
        return self


    def get_final_frame(self, cell:str):
        frames_nonzero = [ f for f, s in enumerate(self.cells[cell]["state"]) if s > 0 ]
        if not frames_nonzero:
            return 0
        else:
            return max([ f for f, s in enumerate(self.cells[cell]["state"]) if s > 0 ])

    def guess_probable_parents(self, cell:str):
        first_appears = self.cells[cell]["state"].index(1)
        point, _, _, _, = self.get_cell_params(first_appears, cell) 
        possible_parents = []

        # what cells were alive in the previous frame 
        cell_alive_in_pre = [ c for c in self.cells.keys() 
                                if self.get_cell_state(first_appears-1, c) > 0] 

        # which cell overlaps with the new cell
        for precell in cell_alive_in_pre:
            pre_ellipse = self.get_cell_params(first_appears-1, precell)
            inside = cell_dimensions.is_point_in_ellipse(point, pre_ellipse)
            if inside:
                possible_parents += [precell]


        error = """ too many parents detected for cell {0} born frame {1} 
            candidates are {2} on the previous frame"""
        if len(possible_parents) > 1:
            raise ValueError(error.format(cell, first_appears, possible_parents))
        elif len(possible_parents) == 1:
            return possible_parents[0]
        else: 
            return "0"

    def get_cells_in_frame(self, frame, state=1):
        return [ c for c in self.get_cells_list() if self.get_cell_state(frame, c)==state]


    def check_all_probable_parents(self):
        good_parent_matches = {}
        suggested_parent_matches = {}
        wrong_parent_matches = {}

        for cell in self.cells.keys():
            probable_parent = self.guess_probable_parents(cell)
            recorded_parent = self.cells[cell]["parent"]

            if recorded_parent == probable_parent:
                good_parent_matches[cell] = probable_parent
            #elif (probable_parent != 0) and recorded_parent != probable_parent:
            elif recorded_parent != probable_parent:
                wrong_parent_matches[cell] = recorded_parent
                suggested_parent_matches[cell] = probable_parent
            #elif recorded_parent != probable_parent:
            #else:
        return good_parent_matches, suggested_parent_matches, wrong_parent_matches

    def make_tree(self):
        tree = nx.DiGraph()
        for cell in self.cells.keys():
            tree.add_edge(self.cells[cell]["parent"], cell)
        return tree
    
    def get_cell_lineage(self, cell_id:str):
        tree = self.make_tree()
        pred = cell_id
        lineage = [ cell_id ]
        ## Dumb way to get this quickly for james
        while pred != "0":
            pred = next(tree.predecessors(pred)) # get first ele[0]
            if pred == "0":
                break 
            lineage += [ pred ]
        lineage.reverse()
        return lineage

    def plot_tree(self, ax, node_colors, node_ypos):
        tree = self.make_tree()
        node_ypos["0"] = 0
        pos = frame_pos(tree, "0", node_ypos)
        nx.draw(tree, pos=pos, node_color=node_colors, edge_color='k', ax=ax, with_labels=True)
        return ax, pos

    def check_data_consistency(self):
        maxf = self.metadata["max_frames"]
        for cell in self.cells.keys():
            for key in self.cells[cell].keys():
                if key == "parent":
                    continue
                if maxf != len(self.cells[cell][key]):
                    print("cell {0} key {1} was {2} not {3}!".format(cell, key, len(self.cells[cell][key]), maxf))
    
def get_leaves(tree):
    leaves = [x for x in tree.nodes_iter() if tree.out_degree(x)==0 and tree.in_degree(x)==1]
    return leaves

#%%
def get_final_decendents(tree, cell):
    def get_children(tree, cell, decendents=[]):
        children = list(tree.successors(cell))
        if children:
            for child in children:
                yield from get_children(tree, child)
        else:
            yield cell
    return list(get_children(tree, cell))

#%%
def hierarchy_pos(G, root, vert_loc=0, width=1., xcenter = 0.5, 
                  pos = None, parent = None):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch.'''
    if pos is None:
        pos = {}

    pos[root] = (xcenter, vert_loc)
    neighbors = list(G.successors(root))
    if len(neighbors)!=0:
        dx = width/len(neighbors) 
        nextx = xcenter - width/2 - dx/2
        for neighbor in neighbors:
            nextx += dx
            pos = hierarchy_pos(G, neighbor, width = dx,
                                vert_loc=vert_loc+1, xcenter=nextx, pos=pos, 
                                parent = root)
    return pos


def frame_pos(G, root, vert_locs, width=1., xcenter = 0.5, pos = None, parent = None):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch.'''
    if pos is None:
        pos = {}
    pos[root] = (xcenter, vert_locs[root])
    neighbors = list(G.successors(root))
    if len(neighbors)!=0:
        dx = width/len(neighbors) 
        nextx = xcenter - width/2 - dx/2
        for neighbor in neighbors:
            nextx += dx
            pos = frame_pos(G, neighbor, vert_locs,
                                width = dx,
                                 xcenter=nextx, pos=pos, 
                                parent = root)
    return pos


def print_possible_parents(td):
    good, suggested, wrong = td.check_all_probable_parents()
    print("----Look Good----")
    for cell, parent in good.items():
        print("parent of {0} : {1}".format(cell, parent))

    print("----Look wrong!----")
    for cell, parent in suggested.items():
        print("parent of \t{0}\t should be \t{1}\t not \t{2}".format(cell, parent, wrong[cell]))

def set_possible_parents(td):
    good, suggested, wrong = td.check_all_probable_parents()

    for cell, parent in suggested.items():
        print("Setting {0} as the parent of {1}".format(parent, cell))
        td = td.set_parent_of(cell, parent)
    return td


def set_and_check_parent(td, par, chi):
    print("Setting {0} as the parent of {1}".format(par, chi))
    tdn = td.set_parent_of(chi, par)
    check_par = tdn.cells[chi]["parent"]
    print("Confirming {0} as the parent of {1}".format(check_par, chi))
    return tdn

def test_tree_lineage():
    path = "data/bio_film_data/data_local_cache/sp8_movies/zoom_1x_30_22/delru_1/cell_track.json"
    td = TrackData(path)
    print(td.get_cell_lineage(7))


def test_graph_data():
    #path = "data/bio_film_data/data/test_movie/cell_track.json"
    path = "data/bio_film_data/data_local_cache/sp8_movies/del_fast_slow/time_lapse_sequence/fast_img_2_106/cell_track.json"

    td = TrackData(path)
    print("9s parent is", td.cells["9"]["parent"])
    G = td.make_tree()
    print(G.adj)
    import matplotlib.pylab as plt
    fig, ax = plt.subplots(1,1)
    #pos=nx.graphviz_layout(G, prog='dot')
    td.plot_tree(ax)
    #nx.draw(G, pos=hierarchy_pos(G, 0), nodecolor='r', edge_color='b', ax=ax, with_labels=True, arrows=True)
    plt.show()
    # path = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/sp8_movies/del_fast_slow/time_lapse_sequence/fast_img_2_106/cell_track.json"
    # td = TrackData(path)
    # td.extend_max_frames(388)
    # td.save(path)

def convert_angles_to_radians(td_path):
    import numpy as np
    td = TrackData(td_path)
    for cell_id in td.cells.keys():
        degs = td.cells[cell_id]["angle"] 
        rads = [ cell_dimensions.limit_angle(np.deg2rad(d)) for d in degs]
        td.cells[cell_id]["angle"] = rads
        print(degs)
        print(rads)
        print("-----------")
    td.save(td_path)



def main_ui():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', "--list_possible_parents", action='store_true', default=False )
    parser.add_argument("--set_auto_suggested_parents", action='store_true', default=False )
    parser.add_argument("--check_consistency", action='store_true', default=False )
    parser.add_argument("--trackdata", "-t", )
    parser.add_argument("--set_parent", type=str)
    parser.add_argument("--set_child", type=str)
    ####
    parser.add_argument("--set_cell_state", type=str)
    parser.add_argument("--cell", type=str)
    parser.add_argument("--from_frame", type=int)
    arguments = parser.parse_args()

    td = TrackData(arguments.trackdata)
    
    if arguments.list_possible_parents:
        print_possible_parents(td)

    if arguments.set_parent and arguments.set_child:
        tdn = set_and_check_parent(td, arguments.set_parent, arguments.set_child)
        tdn.save(arguments.trackdata)
    
    if arguments.set_auto_suggested_parents:
        tdn = set_possible_parents(td)
        tdn.save(arguments.trackdata)
    
    if arguments.check_consistency:
        td.check_data_consistency()

    if arguments.set_cell_state and arguments.from_frame and arguments.cell:
        try:
            statenum = int(arguments.set_cell_state)
            state = td.metadata["states"][str(statenum)]
        except ValueError:
            state = arguments.set_cell_state 
            print("SS", list(td.states.items())) #metadata["states"].items()))
            statenum = td.states[state]
            print("SS")

        for f in range(int(arguments.from_frame), td.metadata["max_frames"]):
            current_state = td.get_cell_state(f, arguments.cell)
            if current_state > 0:
                td.set_cell_state(f, arguments.cell, statenum)
        td.save(arguments.trackdata)



if __name__ == "__main__": 
    #test_graph_data()
    #test_tree_lineage()
    # import sys
    # convert_angles_to_radians(sys.argv[1])
    main_ui()