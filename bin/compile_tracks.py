import argparse
from lib.cell_tracking.compile_cell_tracks import compile 
from lib.cell_tracking.track_data import TrackData


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_pattern', type=str, required=True)
    parser.add_argument('--trackdata', type=str, required=True)
    #parser.add_argument('--cells', nargs="+", type=int, default=[])
    parser.add_argument("--start_frame", type=int)
    parser.add_argument("--end_frame", type=int)
    parser.add_argument('--out_file', type=str, required=True) 
    parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])
    pa = parser.parse_args()
        
    trackdata = TrackData(pa.trackdata)
    print("channels ", pa.channels)
    compile(pa.image_pattern, trackdata, pa.out_file, pa.channels, pa.start_frame, pa.end_frame)



if __name__ == "__main__":
    main()
