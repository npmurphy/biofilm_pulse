import argparse
import shutil
import glob
import os.path

from lib.file_finder import get_paths

def rename_subfiles(f, pa):
    basename, dirbase = get_paths(f)
    related_file = dirbase + "_cy.tiff"
    new_file = dirbase + "_cg.tiff"
    shutil.move(related_file, new_file)
    print(related_file, " -> ", new_file)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') #, help="this expects LSM files")
    pa = parser.parse_args()

    for f in pa.files:
        print(f)
        rename_subfiles(f, pa)


if __name__ == '__main__':
    main()