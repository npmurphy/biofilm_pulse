
import os.path

def check_dir_exists(dir_to_stick_in, path):
    dirn = os.path.dirname(path)
    tpath = os.path.join(dirn, dir_to_stick_in)
    if not os.path.exists(tpath):
        os.mkdir(tpath)

def insert_dir_in_path(dir_to_stick_in, path):
    dirn = os.path.dirname(path)
    filen = os.path.basename(path)
    return os.path.join(dirn, dir_to_stick_in, filen)


def get_labeled_path(path, label):
    pathish = path.split(".")
    ext = pathish[-1]
    body =  pathish[:-1] 
    return ".".join(body) + "_" + label + "." + ext


def get_file_dirname(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    dirname = os.path.dirname(path)
    return dirname, filename

def get_paths(path):
    dirname, basename = get_file_dirname(path)
    return basename, os.path.join(dirname, basename, basename)