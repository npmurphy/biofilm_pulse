import skimage.io
import os.path
import os
import numpy as np
import argparse
import json
import warnings
from ast import literal_eval as make_tuple


def find_number_of_frames_in_movie(movie_info, location):
    numb_frames = 0 
    for d_info in movie_info["positions"][location]["directories"]:
        numb_frames += (d_info["frame_end"]+1) - d_info["frame_start"]
    return numb_frames 

def get_source_images(base_path, movie_pos_info, channel, max_frame_numbers):
    #print(movie_pos_info)
    frame_numbs = [None] * max_frame_numbers 
    index = 0 
    #print("index", 0)
    for dir_dict in movie_pos_info["directories"]:
        #print("n index", index)
        moviedir = dir_dict["dirname"]
        start, end = dir_dict["frame_start"], dir_dict["frame_end"]
        format_num = str(len(str(end)))
        format_str = "_t{0:0" + format_num + "}_z0_ch{1}.tif"
        file_name = os.path.join(base_path, moviedir, os.path.basename(moviedir) + format_str)
        #print(start, end)
        for f in range(start, end+1):
            #print("f, i ", f, f + index)
            if moviedir == "Empty":
                continue
            frame_numbs[index + f] = file_name.format(f, channel)
        index += end +1
    return frame_numbs


def make_a_movie(movie_construct, base_path):
    m_rows = movie_construct["grid_rows"] * movie_construct["image_rows"]
    m_cols = movie_construct["grid_cols"] * movie_construct["image_cols"]
    block_rows = movie_construct["image_rows"] 
    block_cols = movie_construct["image_cols"] 
    name = movie_construct["movie_name"]
    channels = movie_construct["channels"] 
    
    outputdir = os.path.join(base_path, name)
    try:
        os.mkdir(outputdir)
    except FileExistsError as e:
        pass

    max_frame_numbers = max([ find_number_of_frames_in_movie(movie_construct, pl) for pl in  movie_construct["positions"].keys()])
    print(max_frame_numbers)


    frames_chans = [None]*len(channels)
    for c, chan in enumerate(channels):
        frames_chans[c] = {pos_k: get_source_images(base_path, pos_info, chan, max_frame_numbers)
                            for pos_k, pos_info in movie_construct["positions"].items()}

    for ch, frames in zip(channels, frames_chans):
        for f in range(max_frame_numbers):
            print(f, end=",", flush=True)
            #print("frame", end=",")
            big_image = np.zeros((m_rows, m_cols), dtype=np.uint16)
            for (pos_r, pos_c) in movie_construct["positions"].keys():
                #print("POS", pos_r, pos_c)
                #pim_r = (movie_construct["grid_rows"] - 1) - pos_r
                pim_r = pos_r
                pim_c = pos_c
                filename = frames[(pos_r, pos_c)][f]
                if filename is None:
                    continue
                x_offset = movie_construct["positions"][(pos_r, pos_c)]["x_offset"]
                y_offset = movie_construct["positions"][(pos_r, pos_c)]["y_offset"]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    idv_image = skimage.io.imread(filename)
                #print("image row ", pim_r ,  "width", block_rows, "offset", y_offset)
                tim_rs = 0
                ### TODO THIS IS A MESS, I was really tired and its done badly. 
                #tim_re = block_cols 
                bim_rs = (pim_r * block_rows) + y_offset
                bim_re = min(bim_rs + block_rows, big_image.shape[0]) #+ y_offset
                if bim_rs < 0:
                    tim_rs = abs(bim_rs)
                    #tim_re = tim_re - tim_rs
                    bim_rs = bim_rs + tim_rs
                    bim_re = bim_rs + (block_rows - tim_rs)
                bim_cs = max(0, (pim_c * block_cols) + x_offset)
                bim_ce = min(bim_cs + block_cols, big_image.shape[1])
                # print("---------")
                # print("B_row_start", bim_rs, "B_row_end", bim_re, bim_cs,bim_ce)
                # print("I_row_start", tim_rs)#"B_row_end", bim_re, bim_cs,bim_ce)
                # print(big_image.shape)
                # print(idv_image.shape)
                big_image[bim_rs:bim_re, bim_cs:bim_ce] = idv_image[tim_rs:, :bim_ce-bim_cs]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                skimage.io.imsave(os.path.join(outputdir, name+"_t{0:03}_ch{1}.tif".format(f, ch) ), big_image)


def unstring_keys(movie_data):
    positions = movie_data["positions"]
    new_positions = { make_tuple(k): v for k, v in positions.items() }
    #print("new", new_positions.keys())
    movie_data["positions"] = new_positions
    return movie_data

def load_instructions(path):
    with open(path, 'r') as instructions:
      movie_info = json.load(instructions)
    movie_info = [ unstring_keys(mi) for mi in movie_info]
    return movie_info

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instructions', type=str, help='path to a json description')
    parser.add_argument('--movie_name', type=str, help='exact movie to make')
    arguments = parser.parse_args()

    instructions_path = arguments.instructions
    base_path = os.path.dirname(instructions_path)
    movie_info = load_instructions(instructions_path)

    for i in movie_info: 
        if arguments.movie_name is not None:
            if i["movie_name"] != arguments.movie_name:
                continue
        make_a_movie(i, base_path)


if __name__ == '__main__':
    main()
