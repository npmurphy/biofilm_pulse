import pandas as pd

#'sect_date', 'image_date',
file_db_columns = ("file_id", 'path', 'name', 'dirname',
                   'time', 'location', 'strain')
index_col = file_db_columns[0]

def get_filedb(path):
    try:
        filedb = pd.read_csv(path, sep="\t", skip_blank_lines=True, index_col=index_col) #, parse_dates=True)#, dtype=datatypes)
    except OSError as e:
        print(e)
        print("Making a new FileDB")
        filedb = pd.DataFrame(columns=file_db_columns)
        filedb = filedb.set_index(index_col)
        filedb["time"] = filedb["time"].astype(int)
    return filedb


def exists_in_db(db, file_info):
    records_same_name = (db["name"] == file_info["name"]) & \
                        (db["dirname"] == file_info["dirname"])
    if sum(records_same_name) == 0:
        return -1
    elif sum(records_same_name) == 1:
        print((db[records_same_name]).index.tolist())
        return (db[records_same_name].index[0])
    elif sum(records_same_name) > 1:
        print("ERROR : ", db[records_same_name])
        raise Exception("too many files with the same name and dir")


def add_if_new(db, file_info):
    previous_entry = exists_in_db(db, file_info)
    if previous_entry < 0:
        n = len(db)
        db.loc[n] = pd.Series(file_info)
        file_info[index_col] = n
        return True, file_info, db
    else:
        file_info[index_col] = previous_entry
        return False, file_info, db


def save_db(db, filename):
    db.to_csv(filename, sep="\t")

