#!/usr/bin/env python3
import argparse

import numpy as np
import skimage.io

def load_image(path, ignore_missing):
    try: 
        return skimage.io.imread(path) 
    except FileNotFoundError as e:
        if ignore_missing: 
            print("Continuing without ", path)
            return None

def get_first_image_size_dtype(list_of_images):
    for l in list_of_images: 
        if l is not None:
            i_rows, i_cols = l.shape
            i_dtype = l.dtype
            return (i_rows, i_cols), i_dtype 

def replace_nones_with_empty(putative_image, size, dtype):
    if putative_image is None:
        return np.zeros(size, dtype=dtype)
    else:
        return putative_image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+') 
    parser.add_argument('--ignore_missing_files', action="store_true", default=False)
    parser.add_argument('--output_name', type=str, default=True)
    args = parser.parse_args()

    horizontal = True

    loaded = [load_image(f, args.ignore_missing_files) for f in args.files]
    i_size, i_dtype = get_first_image_size_dtype(loaded)
    loaded = [ replace_nones_with_empty(l, i_size, i_dtype) for l in loaded]

    if horizontal: 
        joiner = np.hstack
    
    new_image = joiner(loaded)

    skimage.io.imsave(args.output_name, new_image)


if __name__ == "__main__":
    main()
