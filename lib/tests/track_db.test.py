import os.path
import tempfile
import unittest

from lib.cell_tracking import track_db
from lib.cell_tracking.track_data import TrackData
from lib.cell_tracking.track_db import TrackDB
        
import pandas as pd
import io

SCHNITZ_TABLE = """
id|row|col|length|width|angle|frame|state|status|cell_id
11|1.0|2.0|3.0|4.0|0.5|1|there|auto|1.0
12|2.0|4.0|6.0|8.0|1.0|2|there|auto|1.0
13|3.0|6.0|9.0|12.0|1.5|3|dividing|auto|1.0
24|4.0|8.0|12.0|16.0|2.0|4|dividing|auto|3.0
25|5.0|10.0|15.0|20.0|2.5|5|dividing|auto|3.0
26|6.0|12.0|18.0|24.0|3.0|6|dividing|auto|3.0
27|7.0|14.0|21.0|28.0|3.5|7|dividing|auto|3.0
"""
# CELLSINFRAME_TABLE = """
# id	cell_id	schnitz_id	status
# 1	1	11	checked
# 2	1	12	checked
# 3	1	13	checked
# 4	3	24	checked
# 5	3	25	checked
# 6	3	26	checked
# 7	3	27	checked
# """

CELL_TABLE = """
id|parent|status
1||checked
3|1.0|auto
"""

class TrackDataDB(unittest.TestCase):
    def __init_():
        self.test_db = None
        self.test_path = ""

    def create_test_db2(path):
        db = TrackDB(path)
        tables = [("schnitz", SCHNITZ_TABLE),
                  #("cellinframe", CELLSINFRAME_TABLE),
                  ("cell", CELL_TABLE)]
        for name, table in tables:
            tab = pd.read_csv(io.StringIO(table), sep="\t",index_col="id")
            tab.to_sql(name=name, con=db.session.bind, if_exists = 'append')    
        return db

    # def create_test_db(path):
    #     # cell_1 is on frame 1, 2, 3, schnitzes 11, 12, 13
    #     db = TrackDB(path)
    #     state = "there"

    #     c = track_db.Cell(id=1, parent=None, status="checked")
    #     db.session.add(c)
    #     for f in range(1, 4):
    #         if f == 3:
    #             state="dividing"
    #         i = track_db.CellInFrame(cell_id=1, 
    #                                  schnitz_id=10+f, 
    #                                  status="checked")
    #         db.session.add(i)
    #         s = track_db.Schnitz(id=10+f, 
    #             row= 1.0*f,
    #             col= 2.0*f,
    #             length= 3.0*f,
    #             width= 4.0*f,
    #             angle= 0.5*f,
    #             frame=f,
    #             state=state,
    #             status= "auto")
    #         db.session.add(s)
        
    #     c = track_db.Cell(id=3, parent=1, status="auto")
    #     db.session.add(c)
    #     for f in range(4, 8):
    #         if f == 7:
    #             state="dividing"
    #         i = track_db.CellInFrame(
    #                                  cell_id=3, 
    #                                  schnitz_id=20+f, 
    #                                  status="checked")
    #         db.session.add(i)
    #         s = track_db.Schnitz(id=20+f, 
    #             row= 1.0*f,
    #             col= 2.0*f,
    #             length= 3.0*f,
    #             width= 4.0*f,
    #             angle= 0.5*f,
    #             frame=f, 
    #             state=state,
    #             status= "auto")
    #         db.session.add(s)
    #     db.session.commit()
    #     return db

    def setUp(self):
        self.test_path = tempfile.NamedTemporaryFile().name
        self.test_db = TrackDataDB.create_test_db2(self.test_path)


    # def test_dump_out_text(self):
    #     #df = pd.read_sql(self.test_db.session.query(track_db.Schnitz), self.test_db.session.bind)
    #     df = pd.read_sql_table("schnitz", self.test_db.session.bind).set_index("id")
    #     df.to_csv("/tmp/scnitz.tsv", sep="\t") #, index_col="id")
        
    #     df = pd.read_sql_table("cellinframe", self.test_db.session.bind).set_index("id")
    #     df.to_csv("/tmp/cellinframe.tsv", sep="\t") #, index_col="id")

    #     df = pd.read_sql_table("cell", self.test_db.session.bind).set_index("id")
    #     df.to_csv("/tmp/cells.tsv", sep="\t") #, index_col="id")
    # @classmethod
    # def setUpClass(cls):
    #     super(TrackDataDB, cls).setUpClass()
    #     cls.test_path = tempfile.NamedTemporaryFile().name
    #     cls.test_db = TrackDataDB.create_test_db(cls.test_path)
    
    def tearDown(self):
        self.test_db.session.close()
        os.remove(self.test_path)

    # @classmethod
    # def tearDownClass(cls):
    #     super(TrackDataDB, cls).tearDownClass()
    #     cls.test_db.session.close()
    #     os.remove(cls.test_path)

    def test_create_new_db(self):
        test_path = tempfile.NamedTemporaryFile().name
        pre = os.path.exists(test_path)
        _ = TrackDB(test_path)
        post = os.path.exists(test_path)
        os.remove(test_path)
        self.assertTrue((not pre) & (post))

    def test_add_to_db(self):
        test_path = ""
        td = TrackDB(test_path)
        frame = 10
        cell_id = 2
        properties = {
            "row": 10.0,
            "col": 5.0,
            "length": 1.0,
            "width": 9.0,
            "angle": 0.5,
            "state": "dividing",
        }

        c_schnitz = {
            k: properties[k] for k in ["row", "col", "length", "width", "angle"]
        }
        c_schnitz["status"] = "auto"
        c_schnitz["id"] = 1
        o_schnitz = track_db.Schnitz(**c_schnitz)

        c_cif = {
            "frame": frame,
            "cell_id": cell_id,
            "state": properties["state"],
            "schnitz_id": 1,
            "status": "auto",
            "id": 1,
        }
        o_cif = track_db.CellInFrame(**c_cif)

        td.set_cell_properties(frame, cell_id, properties)

        r_cifs = td.session.query(track_db.CellInFrame).all()
        r_schnitz = td.session.query(track_db.Schnitz).all()
        self.assertEqual(len(r_cifs), 1)
        self.assertEqual(len(r_schnitz), 1)

        self.assertEqual(o_cif, r_cifs[0])
        self.assertEqual(o_schnitz, r_schnitz[0])

    def test_get_cell_params(self):
        cell_id = 3 
        frame = 5
        cell_param = self.test_db.get_cell_params(frame, cell_id)
        c_param = ((2.0*frame, 1.0*frame), 3.0*frame, 4.0*frame, 0.5*frame)
        self.assertEqual(cell_param, c_param)

    def test_add_or_replace_in_db(self):
        ## Replace cell 3 
        cell_id = 3 
        frame = 5
        p = {
            "row": 10.0,
            "col": 5.0,
            "length": 1.0,
            "width": 9.0,
            "angle": 0.5,
            "state": "spore" }

        replaced_p = self.test_db.get_cell_params(frame, cell_id)

        self.test_db.set_cell_properties(frame, cell_id, p)
        should_be = (p["col"], p["row"]), p["length"], p["width"], p["angle"]
        newly_set = self.test_db.get_cell_params(frame, cell_id)
        self.assertNotEqual(replaced_p, newly_set)
        self.assertEqual(should_be, newly_set)

        new_state = self.test_db.get_cell_state(frame, cell_id)
        self.assertEqual(p["state"], new_state)
        
        self.test_db.set_cell_state(frame, cell_id, "airplane")
        newer_state = self.test_db.get_cell_state(frame, cell_id)
        self.assertEqual("airplane", newer_state)


    # def test_save_db(self):
    #     self.assertTrue(False)

    # def test_reopens_old_db(self):
    #     self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
