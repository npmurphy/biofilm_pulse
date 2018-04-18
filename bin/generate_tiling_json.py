
import json
import argparse

base_column = { "movie_name" : "",  
                "grid_rows" : 1, 
                "grid_cols" : 1, 
                "image_rows" : 1024, 
                "image_cols" : 1024, 
                "channels" : [ "00", "01" ],
                "positions" : {} 
}

base_position = { "x_offset": 0, 
                  "y_offset": 0, 
                  "directories": [] }

def make_position(base_dir, start, end, col):
    pos = base_position.copy()
    pos["directories"] = [ {"dirname": "{0}/Position{1:03}".format(base_dir, col),
                            "frame_start": start,
                            "frame_end": end }]
    return pos

def make_column_json(base_dir, starting_from_the_top, start, end, col_info):
    col_id, colnums = col_info
    this_column = base_column.copy()
    this_column["movie_name"] = "Column_{0}".format(col_id)
    this_column["grid_cols"] = len(colnums)
    
    order = list(range(len(colnums)))
    if not starting_from_the_top:
        order = reversed(order)
    positions = { "(0,{0})".format(i): make_position(base_dir, start, end, c) for i, c in zip(order, colnums) }
    this_column["positions"] = positions
    return this_column


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--start_frame", type=int)
    parser.add_argument("--end_frame", type=int)
    parser.add_argument("--starting_from_the_top", action="store_true", default=False)
    parser.add_argument("--description")
    args = parser.parse_args()

    split_description = args.description.split("\n")
    column_info = []
    for col in split_description:
        col_num, position_str = col.split(":")
        position_nums = [int(l.strip()) for l in position_str.strip().split(" ")]
        column_info += [make_column_json(args.base_dir,
                                         args.starting_from_the_top, 
                                         args.start_frame,
                                         args.end_frame,
                                         (int(col_num), position_nums))]
    
    with open(args.output, "w") as jo:
        json.dump(column_info, jo)



if __name__ == '__main__':
    main()