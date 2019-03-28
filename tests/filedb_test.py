import unittest
from lib import filedb
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal

file_zero = {"name": "file_zero.txt",
             "dirname": "/home/sean",
             "path": "doesnt/matter",
             #"sec_date": datetime.datetime.now(),
             #'"image_date": np.nan,
             "time": 48,
             "location": "center",
             "strain": "jlb101"}

file_one = file_zero.copy()
file_one["name"] = "file_one.tiff"
file_one["location"] = "3"

file_two = file_zero.copy()
file_two["name"] = "file_2"
file_two["path"] = "big"

file_zeroB = file_zero.copy()
file_zeroB["location"] = "1"

file_info_list = [file_zero, file_one, file_zeroB, file_two]
test_path = "/tmp/test.tsv"


class TestStringMethods(unittest.TestCase):
    def test_create_empty_db(self):
        try:
            os.remove(test_path)
        except FileNotFoundError:
            pass
        self.assertFalse(os.path.exists(test_path))
        db = filedb.get_filedb(test_path)
        self.assertTrue(len(db) == 0)
        self.assertTrue(all([(c in db.columns)
                             for c in filedb.file_db_columns[1:]])) # index file_id
        self.assertTrue(len(db.columns) == len(filedb.file_db_columns)-1)

    def test_exists_in_db(self):
        try:
            os.remove(test_path)
        except FileNotFoundError:
            pass
        db = filedb.get_filedb(test_path)
        db.loc[0] = pd.Series(file_zero)
        self.assertTrue(-1 == filedb.exists_in_db(db, file_two))
        self.assertTrue(0 == filedb.exists_in_db(db, file_zeroB))

    def test_add_if_new(self):
        try:
            os.remove(test_path)
        except FileNotFoundError:
            pass
        db = filedb.get_filedb(test_path)

        def get_stepwise_results(db, f):
            (b, fi, db) = filedb.add_if_new(db, f)
            return (b, fi, db.copy())
        results = [get_stepwise_results(db, f) for f in file_info_list]
        summary = [(b, fi["file_id"], len(db)) for (b, fi, db) in results]
        expected = [(True, 0, 1), (True, 1, 2), (False, 0, 2), (True, 2, 3)]
        self.assertTrue(all([sr == ex for sr, ex in zip(summary, expected)]))

    def test_save_and_reload(self):
        try:
            os.remove(test_path)
        except FileNotFoundError:
            pass
        db = filedb.get_filedb(test_path)
        for f in file_info_list:
            b, fi, db = filedb.add_if_new(db, f)

        filedb.save_db(db, test_path)
        db2 = filedb.get_filedb(test_path)
        assert_frame_equal(db.sort_index(axis=1), db2.sort_index(axis=1), check_names=True)


if __name__ == '__main__':
    unittest.main()
