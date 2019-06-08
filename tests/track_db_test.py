import io
import os.path
import sys

sys.path += [".."]

import tempfile
import unittest

import pandas as pd

from lib.cell_tracking import track_db
from lib.cell_tracking.track_data import TrackData
from lib.cell_tracking.track_db import TrackDB
from lib.cell_tracking.track_db import Schnitz
import sqlalchemy.orm

SCHNITZ_TABLE = """
id|row|col|length|width|angle|frame|state|status|cell_id
11|1.0|2.0|3.0|4.0|0.5|1|there|auto|1.0
12|2.0|4.0|6.0|8.0|1.0|2|there|auto|1.0
13|3.0|6.0|9.0|12.0|1.5|3|dividing|auto|1.0
24|4.0|8.0|12.0|16.0|2.0|4|dividing|auto|3.0
25|5.0|10.0|15.0|20.0|2.5|5|dividing|auto|3.0
26|6.0|12.0|18.0|24.0|3.0|6|dividing|auto|3.0
27|7.0|14.0|21.0|28.0|3.5|7|dividing|auto|3.0
30|12.0|12.0|21.0|20.0|3.5|7|dividing|auto|5.0
"""

CELL_TABLE = """
id|parent|status
1||checked
3|1.0|auto
5|1.0|auto
"""


def object_to_dict(object):
    od = object.__dict__.copy()
    od.pop("_sa_instance_state", None)
    od.pop("id")
    return od


def compare_objects(theone, other):
    classes_match = isinstance(other, theone.__class__)
    a = object_to_dict(theone)
    b = object_to_dict(other)
    attrs_match = a == b
    return classes_match and attrs_match


class TrackDataDB(unittest.TestCase):
    def __init_(self):
        self.test_db = None
        self.test_path = ""

    def create_test_db2(path):
        db = TrackDB(path)
        tables = [
            ("schnitz", SCHNITZ_TABLE),
            # ("cellinframe", CELLSINFRAME_TABLE),
            ("cell", CELL_TABLE),
        ]
        for name, table in tables:
            tab = pd.read_csv(io.StringIO(table), sep="|", index_col="id")
            tab.to_sql(name=name, con=db.session.bind, if_exists="append")
        return db

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

    def test_set_cell_properties_fail(self):
        frame = 10
        cell_id = 3
        properties = {
            "row": 10.0,
            "col": 5.0,
            "length": 1.0,
            "width": 9.0,
            "angle": 0.5,
            "state": "dividing",
        }
        self.assertRaises(
            track_db.SchnitzNotFoundError,
            self.test_db.set_cell_properties,
            frame,
            cell_id,
            properties,
        )

    def test_add_cell_to_frame(self):
        frame = 10
        cell_id = 3
        properties = {
            "row": 10.0,
            "col": 5.0,
            "length": 1.0,
            "width": 9.0,
            "angle": 0.5,
            "state": "dividing",
        }
        self.assertRaises(
            track_db.SchnitzNotFoundError, self.test_db._get_schnitz_obj, frame, cell_id
        )

        self.test_db.add_cell_to_frame(frame, cell_id, properties)
        schnitz_after = self.test_db.get_cell_properties(frame, cell_id)
        properties.update({"trackstatus": None, "status": "auto"})
        schnitz_after.pop("id")
        self.assertEqual(schnitz_after, properties)

    def test_set_cell_properties_reset(self):
        # Test resetting existing cell
        frame = 6
        cell_id = 3
        properties = {
            "row": 10.0,
            "col": 5.0,
            "length": 1.0,
            "width": 9.0,
            "angle": 0.5,
            "state": "dividing",
        }
        schnitz_orig = self.test_db._get_schnitz_obj(frame, cell_id).__dict__.copy()
        schnitz_orig.pop("_sa_instance_state")

        orig_dict_mod = schnitz_orig.copy()
        orig_dict_mod.update(properties)

        self.test_db.set_cell_properties(frame, cell_id, properties)

        schnitz_after = self.test_db._get_schnitz_obj(frame, cell_id).__dict__.copy()
        schnitz_after.pop("_sa_instance_state")
        self.assertNotEqual(schnitz_after, schnitz_orig)
        self.assertEqual(schnitz_after, orig_dict_mod)

    def test_set_cell_properties_subset(self):
        # Test resetting existing cell
        frame = 6
        cell_id = 3
        properties = {"angle": 0.5, "state": "dividing"}
        schnitz_orig = self.test_db.get_cell_properties(frame, cell_id)

        orig_dict_mod = schnitz_orig.copy()
        orig_dict_mod.update(properties)

        self.test_db.set_cell_properties(frame, cell_id, properties)

        schnitz_after = self.test_db.get_cell_properties(frame, cell_id)
        self.assertNotEqual(schnitz_after, schnitz_orig)
        self.assertEqual(schnitz_after, orig_dict_mod)

    def test_get_cell_params(self):
        cell_id = 3
        frame = 5
        cell_param = self.test_db.get_cell_params(frame, cell_id)
        c_param = ((2.0 * frame, 1.0 * frame), 3.0 * frame, 4.0 * frame, 0.5 * frame)
        self.assertEqual(cell_param, c_param)

    def test_set_cell_params(self):
        cell_id = 3
        frame = 5
        p = ((5.0, 10), 1.0, 9.0, 0.5)

        original = self.test_db.get_cell_params(frame, cell_id)

        self.test_db.set_cell_params(frame, cell_id, p)
        newly_set = self.test_db.get_cell_params(frame, cell_id)

        self.assertNotEqual(original, newly_set)
        self.assertEqual(p, newly_set)

    def test_blank_cell_params(self):
        cell_id = 3
        frame = 5
        self.test_db.get_cell_params(frame, cell_id)
        self.test_db.blank_cell_params(frame, cell_id)
        self.assertRaises(
            track_db.SchnitzNotFoundError, self.test_db.get_cell_params, frame, cell_id
        )

    def test_set_cell_state(self):
        cell_id = 3
        frame = 5

        original_state = self.test_db.get_cell_state(frame, cell_id)
        self.assertEqual("dividing", original_state)

        new_state = "airplane"
        self.test_db.set_cell_state(frame, cell_id, new_state)
        set_state = self.test_db.get_cell_state(frame, cell_id)
        self.assertEqual(new_state, set_state)

    def test_get_cell_list(self):
        cell_list = self.test_db.get_cell_list()
        expected = [1, 3, 5]
        self.assertEqual(cell_list, expected)

    def test_dose_cell_exist(self):
        self.assertTrue(self.test_db.does_cell_exist(1))
        self.assertFalse(self.test_db.does_cell_exist(2))
        self.assertTrue(self.test_db.does_cell_exist(3))

    def test_get_parent_of(self):
        self.assertEqual(1, self.test_db.get_parent_of(3))

    def test_set_parent_of(self):
        before = self.test_db.get_parent_of(1)
        self.assertIsNone(before)

        # 2 doesnt exist
        self.assertRaises(
            sqlalchemy.orm.exc.NoResultFound, self.test_db.set_parent_of, 1, 2
        )

        self.test_db.set_parent_of(1, 3)
        after = self.test_db.get_parent_of(1)
        self.assertEqual(after, 3)

    def test_split_cell_from_point(self):
        cell = 3
        start_f, end_f = 4, 7

        rf, rl = self.test_db.get_first_and_final_frame(cell)
        self.assertEqual(start_f, rf)
        self.assertEqual(end_f, rl)

        self.test_db.split_cell_from_point(3, 5, new_cell=4)
        cell = 3
        start_f, end_f = 4, 4
        rf, rl = self.test_db.get_first_and_final_frame(cell)
        self.assertEqual(start_f, rf)
        self.assertEqual(end_f, rl)
        cell = 4
        start_f, end_f = 5, 7
        rf, rl = self.test_db.get_first_and_final_frame(cell)
        self.assertEqual(start_f, rf)
        self.assertEqual(end_f, rl)

    def test_get_final_frame(self):
        cell_finals = [(1, 3), (2, -1), (3, 7)]
        for cell, final_f in cell_finals:
            self.assertEqual(final_f, self.test_db.get_final_frame(cell))

    def test_get_first_and_final_frame(self):
        cell_finals = [(1, 1, 3), (2, -1, -1), (3, 4, 7)]
        for cell, first_f, final_f in cell_finals:
            rf, rl = self.test_db.get_first_and_final_frame(cell)
            self.assertEqual(first_f, rf)
            self.assertEqual(final_f, rl)

    def test_get_cells_in_frame(self):
        frame = 7
        ans = [3, 5]
        cells = self.test_db.get_cells_in_frame(frame, states=["there", "dividing"])
        self.assertEqual(ans, cells)
        cells = self.test_db.get_cells_in_frame(100, states=["there", "dividing"])
        self.assertEqual([], cells)

    def test_get_cell_family_edges(self):
        cells = [(0, 1), (1, 3), (1, 5)]
        db_cells = self.test_db._get_cell_family_edges()
        self.assertEqual(cells, db_cells)

    def test_set_cell_id(self):
        frame = 7  # has cells 3 and 5
        orig_3_schnitz_id = self.test_db._get_schnitz_obj(frame, 3).id
        orig_5_schnitz_id = self.test_db._get_schnitz_obj(frame, 5).id

        before_cells = self.test_db.get_cell_list()

        self.test_db.set_cell_id(frame, old_id=5, new_id=3)

        after_cells = self.test_db.get_cell_list()
        new_3_obj = self.test_db._get_schnitz_obj(frame, 3)
        # Check the schintz id is correct
        self.assertEqual(orig_5_schnitz_id, new_3_obj.id)

        old_3_obj = (
            self.test_db.session.query(Schnitz).filter_by(id=orig_3_schnitz_id).one()
        )

        self.assertNotIn(old_3_obj.cell_id, before_cells)
        self.assertIn(old_3_obj.cell_id, after_cells)
        self.assertTrue(old_3_obj.cell_id != 3)

        self.assertEqual(len(before_cells) + 1, len(after_cells))

    def test_cell_properties_to_params(self):
        a = self.test_db.get_cell_params(7, 3)
        p = self.test_db.get_cell_properties(7, 3)
        b = self.test_db.cell_properties_to_params(p)
        self.assertEqual(a, b)

    # def test_what_was_cell_called_at_frame(self):
    #     start_cell = 3
    #     frame = 2
    #     expected_name = 1
    #     name = self.test_db.what_was_cell_called_at_frame(frame, start_cell)
    #     self.assertEqual(name, expected_name)

    def test_save_db(self):
        cell_id = 3
        frame = 7
        p = ((5.0, 10), 1.0, 9.0, 0.5)

        original = self.test_db.get_cell_params(frame, cell_id)

        self.test_db.set_cell_params(frame, cell_id, p)
        newly_set = self.test_db.get_cell_params(frame, cell_id)
        self.assertNotEqual(original, newly_set)
        self.assertEqual(p, newly_set)

        self.test_db.save()
        self.test_db.session.close()

        # the objects are still there so this still works?
        # retry = self.test_db.get_cell_params(frame, cell_id)

        new_db = TrackDB(self.test_path)
        modified = new_db.get_cell_params(frame, cell_id)
        self.assertNotEqual(original, modified)
        self.assertEqual(p, modified)

    def test_divide_cell(self):
        # pick a cell in a frame
        d_frame = 6
        par_cell = self.test_db.get_cell_properties(d_frame, 3)
        # pick two cells in the next frame
        child_a = self.test_db.get_cell_properties(d_frame + 1, 3)
        child_b = self.test_db.get_cell_properties(d_frame + 1, 5)
        new_a, new_b = self.test_db.divide_cell(d_frame, 3, 3, 5)
        # check
        self.assertNotIn(new_a, [3])  # this should be a new cell
        self.assertNotIn(new_b, [3])
        self.assertEqual(3, self.test_db.get_parent_of(new_a))
        self.assertEqual(3, self.test_db.get_parent_of(new_b))

        par_cell.update({"state": "divided"})
        par_cell_d = self.test_db.get_cell_properties(d_frame, 3)
        self.assertEqual(par_cell, par_cell_d)


if __name__ == "__main__":
    unittest.main()
