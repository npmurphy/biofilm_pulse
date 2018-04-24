from lib.cell_tracking.track_data import TrackData
from lib.cell_tracking.auto_match import guess_lineages


def main_ui():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--trackdata", "-t", )
    parser.add_argument("--image_pattern", "-i", )
    arguments = parser.parse_args()

    td = TrackData(arguments.trackdata)

    td = guess_lineages(td, arguments.image_pattern)

    td.save(arguments.trackdata)
    


if __name__ == "__main__": 
    main_ui()
    


