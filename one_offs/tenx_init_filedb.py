import argparse
import os
import os.path
from lib.filename_parser import parse_10_filename
import filedb
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', '--filedb', type=str)
    parser.add_argument("-l", "--image_locations", type=str)
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument('-b', "--basedir", type=str)
    pa = parser.parse_args()

    db = filedb.get_filedb(pa.filedb)

    strain_lookup = {
        "sigb" : "JLB021",
        "2xqp" : "JLB095",
        "delru" : "JLB088",
        "delqp" : "JLB039",
        "delsigb" : "JLB098",
        "rfponly" : "JLB035",
        "wt" : "JLB001"
    }

    with open(pa.image_locations) as jp:
        loc_dict = json.load(jp)

    for path in pa.files:
        print(path)
        file_base = os.path.splitext(os.path.basename(path))[0]
        dirname = os.path.dirname(path)
        dirname = dirname.replace(pa.basedir, "")
        if dirname[0] == "/":
            dirname = dirname[1:]
        elif dirname[-1] == "/":
            dirname = dirname[:-1]

        file_info = parse_10_filename(path) 
        strain_num = strain_lookup[file_info["strain"].replace("_", "")]
        fn_extra = {
            "name": file_base,
            "path": "", 
            "dirname": dirname,
            "strain": strain_num.lower()
        }
        file_info.update(fn_extra)
        rebuild_path = pa.basedir + dirname +"/" + file_base + ".tiff" # kind of a check
        file_info["location"] = loc_dict[rebuild_path] # replace with human checked.
        filedb.add_if_new(db, file_info)

        filedb.save_db(db, pa.filedb)


if __name__ == "__main__":
    main()

