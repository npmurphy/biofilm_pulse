import pandas as pd
import filedb 
import argparse
import os.path
from glob import glob

def load_file_data(filepath, ignore_path_section, data, file_df):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    dirname = os.path.dirname(filepath)
    lookuppath = os.path.dirname(filepath)#.split(os.sep)
    lookuppath = lookuppath.replace(ignore_path_section, "")
    if lookuppath[0] == "/":
        lookuppath = lookuppath[1:]
    file_id = filedb.exists_in_db(file_df, {"name": basename, "dirname": lookuppath})
    print("found in DB", file_id)
    # if search_param != "":
    #     search_path = os.path.join(dirname, basename + "_" + data + "-masked_" + search_param + ".tsv")
    # else:
    search_path = os.path.join(dirname, basename + ".tsv")
    fi = pd.read_csv(search_path, sep="\t")
    fi["file_id"] = file_id
    return fi


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument('--basepathtoignore', type=str, default="")
    parser.add_argument('-db', '--filedb')
    parser.add_argument('--data', type=str, default="distmap")
    #parser.add_argument('--param', type=str, default="")# freq0.5_width1.0")
    parser.add_argument('--outfile', type=str, default="summary")

    pa = parser.parse_args()
    if pa.files is None:
        print(parser.usage())

    file_df = filedb.get_filedb(pa.filedb)
    if len(pa.files) == 1 and "*" in pa.files[0]:
        pa.files = glob(pa.files[0])

    dfs = [load_file_data(filepath, pa.basepathtoignore, pa.data, file_df) for filepath in pa.files]
    outfilename = "_".join([pa.outfile, pa.data]) + ".h5"
    concat = pd.concat(dfs, ignore_index=True)
    concat.to_hdf(outfilename, key="data")
