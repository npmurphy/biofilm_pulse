import sqlalchemy as sqa
import sqlalchemy.orm as sqaorm
from sqlalchemy.ext.declarative import declarative_base
import networkx as nx

Base = declarative_base()


class Schnitz(Base):
    __tablename__ = "schnitz"
    id = sqa.Column(sqa.Integer, primary_key=True)
    row = sqa.Column(sqa.Float)
    col = sqa.Column(sqa.Float)
    length = sqa.Column(sqa.Float)
    width = sqa.Column(sqa.Float)
    angle = sqa.Column(sqa.Float)
    frame = sqa.Column(sqa.Integer)
    state = sqa.Column(sqa.String(12), default="there")
    status = sqa.Column(sqa.String(12), default="auto")
    trackstatus = sqa.Column(sqa.String(12), default="auto")
    cell_id = sqa.Column(sqa.Integer, sqa.ForeignKey("cell.id"))

    def __repr__(self):
        return "Cell {cell_id} - Schz {id} in frame {frame} : [({col}, {row}), {length}, {width}, {angle}]".format(
            **self.__dict__
        )


class Cell(Base):
    __tablename__ = "cell"

    id = sqa.Column(sqa.Integer, primary_key=True)
    parent = sqa.Column(sqa.Integer, sqa.ForeignKey("cell.id"))
    status = sqa.Column(sqa.String(12), default="auto")

    def __repr__(self):
        return "Cell {id} child of {parent} status: {status}".format(**self.__dict__)


class MetaData(Base):
    __tablename__ = "metadata"
    id = sqa.Column(sqa.Integer, primary_key=True)
    key = sqa.Column(sqa.String)
    values = sqa.Column(sqa.String)

    def __repr__(self):
        return "{{ {0}: {1}}}".format(self.key, self.value)


class TrackDB(object):
    _default_states = {
        1: "there",
        2: "divided",
        3: "disapeared",
        4: "sporulating",
        5: "spore",
    }

    _default_state = _default_states[1]
    _default_status = "auto"

    def __init__(self, path):
        if path and path[0] == "/":
            path = "/" + path  # it wants an extra slash for files?
        engine = sqa.create_engine("sqlite://" + path)
        Base.metadata.create_all(engine)
        Session = sqaorm.sessionmaker(bind=engine)
        self.session = Session()
        self.metadata = {"states": self._default_states} 
        self.states = {v: int(k) for k, v in self.metadata["states"].items()}

    def save(self):
        # ext = ".{:%Y-%m-%d_%H-%M}".format(datetime.datetime.now())
        # try:
        #     shutil.copy(path, path + ext)
        # except FileNotFoundError as e:
        #     pass
        self.session.commit()
        print("ran DB commit")

    def _get_schnitz_obj(self, frame, cell_id):
        return self._get_schnitz_query(frame, cell_id).one()

    def _get_schnitz_query(self, frame, cell_id):
        sch = self.session.query(Schnitz).filter(
            Schnitz.cell_id == cell_id, Schnitz.frame == frame
        )
        return sch

    def create_cell(self, cell_id, params=None):
        if params is None:
            params = {}
        cp = params.copy()
        cp.update({"id": cell_id})
        c = Cell(**cp)
        self.session.add(c)
        #self.session.commit()
    
    def create_cell_if_new(self, cell_id, params=None):
        cell = self.session.query(Cell).filter(Cell.id == cell_id).all()
        if cell:
            return None
        self.create_cell(cell_id, params)

    def get_cell_params(self, frame, cell_id):
        s = self._get_schnitz_obj(frame, cell_id)
        return (s.col, s.row), s.length, s.width, s.angle

    def set_cell_params(self, frame, cell_id, cell_props):
        center, length, width, angle = cell_props
        cell = {}
        cell["row"] = center[1]
        cell["col"] = center[0]
        cell["length"] = length
        cell["width"] = width
        cell["angle"] = angle
        self.set_cell_properties(frame, cell_id, cell)

    def add_new_ellipses_to_frame(self, ellipse_list, frame):
        cell_id = self.get_max_cell_id() 
        for ellipse in ellipse_list:
            cell_id += 1
            self.create_cell_if_new(cell_id, {"status":"auto"})
            self.session.flush()
            self.set_cell_params(frame, cell_id, ellipse)
            self.set_cell_status(frame, cell_id, "auto")
        


    def blank_cell_params(self, frame, cell_id):
        self.delete_schnitz(frame, cell_id)

    def delete_schnitz(self, frame, cell_id):
        self._get_schnitz_query(frame, cell_id).delete()

    def get_cell_list(self):
        all_cells = [c.id for c in self.session.query(Cell).all()]
        return all_cells
    
    def get_max_cell_id(self):
        return max(self.get_cell_list())

    def does_cell_exist(self, cell_id):
        cell = self.session.query(Cell).filter(Cell.id == cell_id).all()
        if cell:
            return True
        else:
            return False

    def get_cell_state(self, frame, cell_id):
        sch_list = self._get_schnitz_query(frame, cell_id).all()
        if not sch_list: 
            return 0
        s = sch_list[0]
        return s.state

    def set_cell_state(self, frame, cell_id, state):
        s = self._get_schnitz_obj(frame, cell_id)
        s.state = state
        #self.session.commit()
    
    def get_cell_status(self, frame, cell_id):
        s = self._get_schnitz_obj(frame, cell_id)
        return s.status
    
    def set_cell_status(self, frame, cell_id, status):
        s = self._get_schnitz_obj(frame, cell_id)
        s.status = status
        #self.session.commit()
    
    def get_cell_trackstatus(self, frame, cell_id):
        s = self._get_schnitz_obj(frame, cell_id)
        return s.trackstatus
    
    def set_cell_trackstatus(self, frame, cell_id, status):
        s = self._get_schnitz_obj(frame, cell_id)
        s.trackstatus = status

    def set_cell_properties(self, frame, cell_id, properties):
        try:
            _ = self.session.query(Cell).filter(Cell.id == cell_id).one()
        except sqaorm.exc.NoResultFound as e:
            raise ValueError("Cell {0} does not exist yet".format(cell_id)) from e

        new_params = {"frame": frame, "cell_id": cell_id}
        schnitz_props = [k for k in Schnitz.__dict__ if "__" not in k]
        schnitz_part = {k: v for k, v in properties.items() if k in schnitz_props}
        new_params.update(schnitz_part)
        schnitz_q = self._get_schnitz_query(frame, cell_id)
        s_l = len(schnitz_q.all())
        if s_l == 0:
            schnitz = Schnitz(**new_params)
            self.session.add(schnitz)
            self.session.flush()
        elif s_l == 1:
            schnitz_q.update(new_params)
            self.session.flush()
        else:
            raise ValueError(
                "{0} Scnitz in frame {1} as cell {2}".format(s_l, frame, cell_id)
            )

    def get_cell_properties(self, frame, cell_id, properties=None):
        schnitz = self._get_schnitz_obj(frame, cell_id).__dict__.copy()
        schnitz.pop("_sa_instance_state", None)
        if properties is None:
            return schnitz
        return { k: schnitz[k] for k in properties}

    def extend_max_frames(self, new_max):
        # dont_need this
        return None
    
    def get_max_frames(self):
        schnitz = self.session.query(Schnitz).all()
        return max([s.frame for s in schnitz])

    def get_parent_of(self, child):
        return (self.session.query(Cell).filter(Cell.id == child).one()).parent

    def set_parent_of(self, child, parent):
        cell = (self.session.query(Cell).filter(Cell.id == child)).one()
        putative_parent = (self.session.query(Cell).filter(Cell.id == parent)).one()
        cell.parent = putative_parent.id
        #self.session.commit()
        return cell

    def split_cell_from_point(
        self, parent, frame_start, frame_end=None, new_cell=None, new_cell_params={}
    ):

        if frame_end is None:
            frame_end = self.get_final_frame(parent)
        (
            self.session.query(Schnitz)
            .filter(
                Schnitz.cell_id == parent,
                Schnitz.frame >= frame_start,
                Schnitz.frame <= frame_end,
            )
            .update({"cell_id": new_cell})
        )
        if not self.does_cell_exist(new_cell):
            self.create_cell(new_cell, new_cell_params)

    def get_first_and_final_frame(self, cell):
        schnitz = self.session.query(Schnitz).filter(Schnitz.cell_id == cell)
        frames = [s.frame for s in schnitz]
        if not frames:
            return -1, -1

        minf = min(frames)
        maxf = max(frames)
        return minf, maxf

    def get_final_frame(self, cell):
        _, maxf = self.get_first_and_final_frame(cell)
        return maxf

    def get_cells_in_frame(self, frame, states=["there"]):
        if states is None:
            listr = [ s[0] for s in self.session.query(Schnitz.state).distinct()]
            states = listr
        schnitz = self.session.query(Schnitz).filter(
            Schnitz.frame == frame, Schnitz.state.in_(states)
        )
        return [s.cell_id for s in schnitz]

    def _get_cell_family_edges(self):
        cells = self.session.query(Cell).all()

        def parent(c):
            if c.parent is None:
                return 0
            return c.parent

        return [(parent(c), c.id) for c in cells]

    def make_tree(self):
        tree = nx.DiGraph()
        edges = self._get_cell_family_edges()
        for parent, child in edges:
            tree.add_edge(parent, child)
        return tree

    def get_cell_lineage(self, cell_id):
        ## TODO do this in sql ?
        tree = self.make_tree()
        pred = cell_id
        lineage = [cell_id]
        while pred != 0:
            pred = next(tree.predecessors(pred))  # get first ele[0]
            if pred == 0:
                break
            lineage += [pred]
        lineage.reverse()
        return lineage
    
    def get_final_decendants(self, cell):
        tree = self.make_tree()
        return get_final_decendents(tree, cell)

    # def what_was_cell_called_at_frame(self, frame, cell):
    #     lineage = self.get_cell_lineage(cell)
    #     print(lineage)
    #     for c in self.get_cell_lineage(cell):
    #         print(frame, c)
    #         if self.get_cell_state(frame, c):
    #             return cell

    def plot_tree(self, ax, node_colors, node_ypos):
        tree = self.make_tree()
        node_ypos[0] = 0
        pos = frame_pos(tree, 0, node_ypos)
        nx.draw(
            tree,
            pos=pos,
            node_color=node_colors,
            edge_color="k",
            ax=ax,
            with_labels=True,
        )
        return ax, pos


def frame_pos(G, root, vert_locs, width=1.0, xcenter=0.5, pos=None, parent=None):
    """If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch."""
    if pos is None:
        pos = {}
    pos[root] = (xcenter, vert_locs[root])
    neighbors = list(G.successors(root))
    if len(neighbors) != 0:
        dx = width / len(neighbors)
        nextx = xcenter - width / 2 - dx / 2
        for neighbor in neighbors:
            nextx += dx
            pos = frame_pos(
                G, neighbor, vert_locs, width=dx, xcenter=nextx, pos=pos, parent=root
            )
    return pos
    """
    
    def plot_tree(self, ax, node_colors, node_ypos):
    
    """


def parse_time(time_str):
    import re

    "Turns 3h20m, or 4m, into a float of that duration in mins"
    hour_g = re.search("(\d+)h", time_str)
    mins_g = re.search("(\d+)m", time_str)
    hour = 0 if hour_g is None else hour_g.groups()[0]
    mins = 0 if mins_g is None else mins_g.groups()[0]
    return int(hour) * 60 + int(mins)


def get_leaves(tree):
    leaves = [
        x for x in tree.nodes if tree.out_degree(x) == 0 and tree.in_degree(x) == 1
    ]
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
def hierarchy_pos(G, root, vert_loc=0, width=1.0, xcenter=0.5, pos=None, parent=None):
    """If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch."""
    if pos is None:
        pos = {}

    pos[root] = (xcenter, vert_loc)
    neighbors = list(G.successors(root))
    if len(neighbors) != 0:
        dx = width / len(neighbors)
        nextx = xcenter - width / 2 - dx / 2
        for neighbor in neighbors:
            nextx += dx
            pos = hierarchy_pos(
                G,
                neighbor,
                width=dx,
                vert_loc=vert_loc + 1,
                xcenter=nextx,
                pos=pos,
                parent=root,
            )
    return pos


def frame_pos(G, root, vert_locs, width=1.0, xcenter=0.5, pos=None, parent=None):
    """If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch."""
    if pos is None:
        pos = {}
    pos[root] = (xcenter, vert_locs[root])
    neighbors = list(G.successors(root))
    if len(neighbors) != 0:
        dx = width / len(neighbors)
        nextx = xcenter - width / 2 - dx / 2
        for neighbor in neighbors:
            nextx += dx
            pos = frame_pos(
                G, neighbor, vert_locs, width=dx, xcenter=nextx, pos=pos, parent=root
            )
    return pos


# def print_possible_parents(td):
#     good, suggested, wrong = td.check_all_probable_parents()
#     print("----Look Good----")
#     for cell, parent in good.items():
#         print("parent of {0} : {1}".format(cell, parent))

#     print("----Look wrong!----")
#     for cell, parent in suggested.items():
#         print("parent of \t{0}\t should be \t{1}\t not \t{2}".format(cell, parent, wrong[cell]))

# def set_possible_parents(td):
#     good, suggested, wrong = td.check_all_probable_parents()

#     for cell, parent in suggested.items():
#         if parent == "0":  # dont set to the root.
#             continue
#         print("Setting {0} as the parent of {1}".format(parent, cell))
#         td = td.set_parent_of(cell, parent)
#     return td


def set_and_check_parent(td, par, chi):
    print("Setting {0} as the parent of {1}".format(par, chi))
    tdn = td.set_parent_of(chi, par)
    check_par = tdn.cells[chi]["parent"]
    print("Confirming {0} as the parent of {1}".format(check_par, chi))
    return tdn


# def test_tree_lineage():
#     path = "data/bio_film_data/data_local_cache/sp8_movies/zoom_1x_30_22/delru_1/cell_track.json"
#     td = TrackData(path)
#     print(td.get_cell_lineage(7))


# def test_graph_data():
#     #path = "data/bio_film_data/data/test_movie/cell_track.json"
#     path = "data/bio_film_data/data_local_cache/sp8_movies/del_fast_slow/time_lapse_sequence/fast_img_2_106/cell_track.json"

#     td = TrackData(path)
#     print("9s parent is", td.cells["9"]["parent"])
#     G = td.make_tree()
#     print(G.adj)
#     import matplotlib.pylab as plt
#     fig, ax = plt.subplots(1,1)
#     #pos=nx.graphviz_layout(G, prog='dot')
#     td.plot_tree(ax)
#     #nx.draw(G, pos=hierarchy_pos(G, 0), nodecolor='r', edge_color='b', ax=ax, with_labels=True, arrows=True)
#     plt.show()
#     # path = "/Users/npm33/stochastic/data/bio_film_data/data_local_cache/sp8_movies/del_fast_slow/time_lapse_sequence/fast_img_2_106/cell_track.json"
#     # td = TrackData(path)
#     # td.extend_max_frames(388)
#     # td.save(path)


def get_tree_points(td):
    # get the number of leaves.
    # set as width.
    # for each leaf:
    #     add lines from birth to death.

    # for td.cells
    return None


def plot_lineage_tree(ax, td):
    tree_points = get_tree_points(td)
    ax.plot(tree_points, color="blue")
    return ax


def view_lineage_tree(td):
    fig, ax = plt.subplots(1, 1)
    ax = plot_lineage_tree(ax, td)
    plt.show()


def load_json(json_path, sql_path):
    from lib.cell_tracking.track_data import TrackData

    td = TrackData(json_path)
    
    cell_db = TrackDB(sql_path)

    def parent(cell):
        p = td.cells[cell]["parent"]
        if p == "0":
            return None
        return int(p)

    def stater(state_num):
        if state_num == 1:
            return "there"
        return td._default_states[state_num]

    for cell in td.get_cells_list():
        cell_db.create_cell(int(cell), {"parent": td.cells[cell]["parent"], "status":"migrated"})
        print(int(cell), {"parent": parent(cell), "status":"migrated"})
        try: 
            first_f, final_f = td.get_first_and_final_frame(str(cell))
            for f in range(first_f, final_f + 1):
                cell_p = td.get_cell_properties(f, str(cell))
                cell_p["status"] = "migrated"
                cell_p["state"] = stater(cell_p["state"])
                cell_db.set_cell_properties(f, int(cell), cell_p)
                print(cell_p)
        except ValueError as e:
            print(e)
            pass

        cell_db.save()


# if __name__ == "__main__":
#     jsonpath = '/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies//BF10_timelapse/Column_2/cell_track.json'
#     sql_path = "/tmp/bf_image.sqllite"
#     load_json(jsonpath, sql_path)
