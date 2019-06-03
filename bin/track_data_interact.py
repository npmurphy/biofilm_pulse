import lib.cell_tracking.track_data as track_data
from lib.cell_tracking.track_data import TrackData
import argparse


def main_ui():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split_cell_at_frame", action="store_true", default=False)
    parser.add_argument("--check_consistency", action="store_true", default=False)
    parser.add_argument(
        "--auto_correct_if_possible", action="store_true", default=False
    )

    parser.add_argument("--trackdata", "-t")
    parser.add_argument("--view_tree", action="store_true")
    parser.add_argument("--set_parent", type=str)
    parser.add_argument("--set_child", type=str)
    parser.add_argument("--set_cell_state", type=str)
    parser.add_argument("--cell", type=str)
    parser.add_argument("--new_cell", type=str)
    parser.add_argument("--from_frame", type=int)
    parser.add_argument("--upto_frame", type=int)
    parser.add_argument("--at_frame", type=int)
    parser.add_argument("--view_cell", type=str)
    arguments = parser.parse_args()

    td = TrackData(arguments.trackdata)

    if arguments.set_parent and arguments.set_child:
        td = track_data.set_and_check_parent(
            td, arguments.set_parent, arguments.set_child
        )
        td.save(arguments.trackdata)

    if arguments.split_cell_at_frame:
        new_cell, td = td.split_cell_from_point(
            arguments.cell,
            arguments.from_frame,
            arguments.upto_frame,
            arguments.new_cell,
        )
        print("New cell added # {0}".format(new_cell))
        td.save(arguments.trackdata)

    # if arguments.view_tree:
    #     view_lineage_tree(td)

    if arguments.check_consistency:
        td = td.check_data_consistency(arguments.auto_correct_if_possible)
        if arguments.auto_correct_if_possible:
            td.save(arguments.trackdata)

    if arguments.view_cell and arguments.at_frame:
        props = td.get_cell_properties(arguments.at_frame, arguments.view_cell)
        print("Cell {0} at frame {1}".format(arguments.view_cell, arguments.at_frame))
        for k, v in props.items():
            print("    {0}:\t{1}".format(k, v))

    if arguments.set_cell_state and arguments.from_frame and arguments.cell:
        try:
            statenum = int(arguments.set_cell_state)
            state = td.metadata["states"][statenum]
        except ValueError:
            state = arguments.set_cell_state
            # print("SS", list(td.states.items())) #metadata["states"].items()))
            statenum = td.states[state]
            # print("SS")

        for f in range(int(arguments.from_frame), td.metadata["max_frames"]):
            current_state = td.get_cell_state(f, arguments.cell)
            if current_state > 0:
                td.set_cell_state(f, arguments.cell, statenum)
        td.save(arguments.trackdata)


if __name__ == "__main__":
    main_ui()
