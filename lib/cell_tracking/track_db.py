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
        return "Schnitz {0} (frame {6}): ({1},{2}), {3}, {4}, {5}".format(
            self.id, self.row, self.col, self.length, self.width, self.angle, self.frame
        )

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
        return "Cell {0} - {1} - {2}".format(self.cell_id, self.parent, self.status)

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
        print("gettering frame=", frame, "cell ", cell_id)
        # print(self.session.query(CellInFrame).filter_by(cell_id=cell_id).all())
        # for s in (self.session.query(CellInFrame, Schnitz)
        #                            .filter(CellInFrame.cell_id==cell_id)
        #                            .join(Schnitz) 
        #                            .filter(Schnitz.frame==frame)
        #                            .all()):
        #     print(s)
        print(self.session.query(CellInFrame)
                              .filter(CellInFrame.cell_id==cell_id)
                              .join(Schnitz) 
                              .filter(Schnitz.frame==frame)
                              .one())
        cif = (self.session.query(CellInFrame)
                           .filter(CellInFrame.cell_id==cell_id)).one()
        print(cif)
        sch = (cif.join(Schnitz) 
                  .filter(Schnitz.frame==frame)
                  .all())
        print(sch)
        # cell_inframe = (
        #     self.session.query(CellInFrame)
        #                 .filter_by(frame=frame, cell_id=cell_id)
        #                 .first()
        # )
        # sch = self.session.query(Schnitz).filter_by(id=cell_inframe.schnitz_id).first()
        return cif, s

    def get_cell_params(self, frame, cell_id):
        cif, s = self._get_schnitz_obj(frame, cell_id)
        return (s.col, s.row), s.length, s.width, s.angle

    # def set_cell_params(self, frame, cell_id, cell_props):

    def get_cells_list(self):
        all_cells = self.session.query(Cell).all().id
        print(all_cells)
        return all_cells

    def get_cell_state(self, frame, cell_id):
        cif, s = self._get_schnitz_obj(frame, cell_id)
        return cif.state
    
    def set_cell_state(self, frame, cell_id, state):
        cif, s = self._get_schnitz_obj(frame, cell_id)
        cif.state = state
        self.session.commit()

    def set_cell_properties(self, frame, cell_id, properties):
        cell_exists = (
            self.session.query(CellInFrame)
            .filter_by(frame=frame, cell_id=cell_id)
            .first()
        )

        schnitz_props = [k for k in Schnitz.__dict__ if "__" not in k]
        cell_props = {k: v for k, v in properties.items() if k in schnitz_props}

        if cell_exists:
            schnitz = (
                self.session.query(Schnitz).filter_by(id=cell_exists.schnitz_id)
            ).update(cell_props)
        else:
            schnitz = Schnitz(**cell_props)
            self.session.add(schnitz)
            self.session.flush()
            self.session.refresh(schnitz)  # need this to get the new pk
            c = CellInFrame(
                **{
                    "frame": frame,
                    "schnitz_id": schnitz.id,
                    "cell_id": cell_id,
                }
            )
            self.session.add(c)
            self.session.flush()

        if "state" in properties:
            self.set_cell_state(frame, cell_id, properties["state"])

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
