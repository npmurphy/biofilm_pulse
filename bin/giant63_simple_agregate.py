#import filename_parser
import pandas as pd
import lib.filedb as filedb
import argparse
import os.path
from glob import glob



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument('-db', '--filedb')
    parser.add_argument('--bad_db')
    parser.add_argument('-o', '--output', default="output.h5")
    parser.add_argument('-a', '--append', action="store_true", default=False)
    parser.add_argument('--remove_from_path', default="")
    parser.add_argument('--data') # "spores or "cells"


    pa = parser.parse_args()
    
    file_df = filedb.get_filedb(pa.filedb)
    if pa.bad_db:  
        bad_df = filedb.get_filedb(pa.bad_db)
    else:
        bad_df = None

    print(bad_df)

    if len(pa.files) == 1 and "*" in pa.files[0]:
        pa.files = glob(pa.files[0], recursive=True)
    pa.files = [ f for f in pa.files if f[-4:] == ".tsv"]

    def read_tsv(path):
        try: 
            df = pd.read_csv(path, sep="\t")
            #basename = os.path.splitext(os.path.basename(path))[0]
            dirname = os.path.dirname(path)
            basename = os.path.basename(dirname)
            dirname = os.path.dirname(dirname)
            lookuppath = dirname.replace(pa.remove_from_path, "")

            file_id = filedb.exists_in_db(file_df, {"name": basename, "dirname": lookuppath})
            if file_id < 0: 
                is_bad = filedb.exists_in_db(bad_df, {"name": basename, "dirname": lookuppath})
                if is_bad >= 0:
                    return None
                else:
                    raise Exception("Couldnt find", basename, lookuppath)
            df["global_file_id"] = file_id
            return df
        except KeyError as e:
            print(path)
            raise e
    if pa.append:
        mode = "a"
    else :
        mode = "w"
    total = pd.concat([ read_tsv(f) for f in pa.files], ignore_index=False)
    total.to_hdf(pa.output, pa.data, mode=mode) #, complib="bzip2", complevel=5)