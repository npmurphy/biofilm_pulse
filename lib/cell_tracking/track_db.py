import sqlalchemy as sqa
import sqlalchemy.orm as sqaorm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class MyBase(Base):
#     def __eq__(self, other):
#         classes_match = isinstance(other, self.__class__)
#         a, b = self.__dict__.copy(), other.__dict__.copy()
#         # compare based on equality our attributes, ignoring SQLAlchemy internal stuff
#         a.pop("_sa_instance_state", None)
#         b.pop("_sa_instance_state", None)
#         attrs_match = a == b
#         return classes_match and attrs_match


class Schnitz(Base):
    __tablename__ = "schnitz"
    id = sqa.Column(sqa.Integer, primary_key=True)
    row = sqa.Column(sqa.Float)
    col = sqa.Column(sqa.Float)
    length = sqa.Column(sqa.Float)
    width = sqa.Column(sqa.Float)
    angle = sqa.Column(sqa.Float)
    frame = sqa.Column(sqa.Integer)
    state = sqa.Column(sqa.String(12), default="growing")
    status = sqa.Column(sqa.String(12), default="auto")
    cell_id = sqa.Column(sqa.Integer, sqa.ForeignKey("cell.id"))

    #cell = sqaorm.relationship("CellInFrame", back_populates="schnitzes")

    def __eq__(self, other):
        classes_match = isinstance(other, self.__class__)
        a, b = self.__dict__.copy(), other.__dict__.copy()
        # compare based on equality our attributes, ignoring SQLAlchemy internal stuff
        a.pop("_sa_instance_state", None)
        b.pop("_sa_instance_state", None)
        attrs_match = a == b
        return classes_match and attrs_match

    def __repr__(self):
        return "Cell {cell_id} - Schz {id} in frame {frame} : [({col}, {row}), {length}, {width}, {angle}]".format(**self.__dict__)

class Cell(Base):
    __tablename__ = "cell"

    id = sqa.Column(sqa.Integer, primary_key=True)
    parent = sqa.Column(sqa.Integer, sqa.ForeignKey("cell.id"))
    status = sqa.Column(sqa.String(12), default="auto")

    def __eq__(self, other):
        classes_match = isinstance(other, self.__class__)
        a, b = self.__dict__.copy(), other.__dict__.copy()
        # compare based on equality our attributes, ignoring SQLAlchemy internal stuff
        a.pop("_sa_instance_state", None)
        b.pop("_sa_instance_state", None)
        attrs_match = a == b
        return classes_match and attrs_match

    def __repr__(self):
        return "Cell {id} child of {parent} status: {status}".format(**self.__dict__)

# class CellInFrame(Base):
#     __tablename__ = "cellinframe"

#     id = sqa.Column(sqa.Integer, primary_key=True)
#     #frame = sqa.Column(sqa.Integer)
#     cell_id = sqa.Column(sqa.Integer, sqa.ForeignKey("cell.id"))
#     schnitz_id = sqa.Column(sqa.Integer, sqa.ForeignKey("schnitz.id"), unique=True)
#     status = sqa.Column(sqa.String(12), default="auto")
    
#     schnitzes = sqaorm.relationship("Schnitz", back_populates="cell")

#     def __eq__(self, other):
#         classes_match = isinstance(other, self.__class__)
#         a, b = self.__dict__.copy(), other.__dict__.copy()
#         # compare based on equality our attributes, ignoring SQLAlchemy internal stuff
#         a.pop("_sa_instance_state", None)
#         b.pop("_sa_instance_state", None)
#         attrs_match = a == b
#         return classes_match and attrs_match

#     def __repr__(self):
#         return "Cell {0} is schnitz {1}".format(self.cell_id, self.schnitz_id)


class MetaData(Base):
    __tablename__ = "metadata"
    id = sqa.Column(sqa.Integer, primary_key=True)
    key = sqa.Column(sqa.String)
    values = sqa.Column(sqa.String)

    def __repr__(self):
        return "{{ {0}: {1}}}".format(self.key, self.value)


# class State(Base):
#     __tablename__ = "states"
#     id = sqa.Column(sqa.Integer, primary_key=True)
#     # key = sqa.Column(sqa.String)
#     name = sqa.Column(sqa.String)

#     def __repr__(self):
#         return "{{ {0}: {1}}}".format(self.id, self.value)


# class CellAccess(object):
#     def __init__(self, session):
#         self.session = session

#     def __getitem__(self, key):
#         return self.__getattribute__(key)


class TrackDB(object):
    _default_states = {
        0: "NE",
        1: "growing",
        2: "divided",
        3: "disapeared",
        4: "sporulating",
        5: "spore",
    }

    _default_state = "there"
    _default_status = "auto"

    def __init__(self, path):
        if path and path[0] == "/":
            path = "/" + path  # it wants an extra slash for files?
        engine = sqa.create_engine("sqlite://" + path)
        Base.metadata.create_all(engine)
        Session = sqaorm.sessionmaker(bind=engine)
        self.session = Session()
        #self.cells = CellAccess(self.session)
        # TODO add metadata if its new
        # TODO add states if its new
        # TODO add states table if new

    def save(self, path):
        # ext = ".{:%Y-%m-%d_%H-%M}".format(datetime.datetime.now())
        # try:
        #     shutil.copy(path, path + ext)
        # except FileNotFoundError as e:
        #     pass
        self.session.commit()
    
    def _get_schnitz_obj(self, frame, cell_id):
        return self._get_schnitz_query(frame, cell_id).one()
    
    def _get_schnitz_query(self, frame, cell_id):
        sch = (self.session.query(Schnitz)
                           .filter(Schnitz.cell_id==cell_id, Schnitz.frame==frame)
                           )
        return sch

    # def _set_or_create(self, model, defaults=None, **kwargs):

    #     instance = session.query(model).filter_by(**kwargs).first()
    #     if instance:
    #         return instance
    #     else:
    #         params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
    #         if defaults:
    #             params.update(defaults)
    #         instance = model(**params)
    #         return instance

    def get_cell_params(self, frame, cell_id):
        s = self._get_schnitz_obj(frame, cell_id)
        return (s.col, s.row), s.length, s.width, s.angle

    # def set_cell_params(self, frame, cell_id, cell_props):

    def get_cell_list(self):
        all_cells = [ c.id for c in self.session.query(Cell).all()]
        return all_cells

    def get_cell_state(self, frame, cell_id):
        s = self._get_schnitz_obj(frame, cell_id)
        return s.state
    
    def set_cell_state(self, frame, cell_id, state):
        s = self._get_schnitz_obj(frame, cell_id)
        s.state = state
        self.session.commit()

    def set_cell_properties(self, frame, cell_id, properties):
        try:
            _ = (self.session.query(Cell)
                                    .filter(Cell.id==cell_id)
                                    .one())
        except sqaorm.exc.NoResultFound as e:
            raise ValueError("Cell {0} does not exist yet".format(cell_id)) from e

        schnitz_props = [k for k in Schnitz.__dict__ if "__" not in k]
        schnitz_part = {k: v for k, v in properties.items() if k in schnitz_props}
        schnitz_part.update({"frame": frame, "cell_id": cell_id})
        
        schnitz_q = self._get_schnitz_query(frame, cell_id)
        s_l = len(schnitz_q.all())
        if s_l == 0:
            schnitz = Schnitz(**schnitz_part)
            self.session.add(schnitz)
            self.session.flush()
        elif s_l == 1:
            schnitz_q.update(schnitz_part)
            self.session.flush()
        else :
            raise ValueError("{0} Scnitz in frame {1} as cell {2}".format(s_l, frame, cell_id))

        # try:
        #     print("trying")
        #     schnitz_exists = self._get_schnitz_query(frame, cell_id).one()
        #     #print(len(schnitz_exists.all()))
        #     schnitz_exists.update(schnitz_part)
        # except sqaorm.exc.NoResultFound:
        #     print("failed")
        # finally:
        self.session.flush()

"""
def main():
    engine = sqa.create_engine(
        "sqlite:////home/nmurphy/work/projects/bf_pulse/cell_track.sqllite", echo=True
    )
    Base.metadata.create_all(engine)
    Session = sqaorm.sessionmaker(bind=engine)
    session = Session()
    schnitz1 = Schnitz(x=43.2, y=323.2, length=33.2, width=22.3, angle=221.0)
    session.add(schnitz1)
    session.flush()
    session.commit()
    session.close()
"""


"""
def load_json():
    from lib.cell_tracking.track_data import TrackData

    td = TrackData(json_path)
    # for i in range(td.metadata["max_frame"]):
    #    for
    for cell in td.get_all_cells_list():
        first, final = td.get_first_and_final_frame(cell)
        for f in range(first, final + 1):
            cell_p = td.get_cell_property_list(f, cell)
            schnitz = Schnitz(**cell_p)
            session.add(schnitz)
            Cell({"frame": f, "schintz": new_id, "cell": int(cell)})
"""

if __name__ == "__main__":
    main()
