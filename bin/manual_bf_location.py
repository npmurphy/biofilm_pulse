import numpy as np
import matplotlib.pyplot as plt
from lib.common import read_lsm
import os.path
from glob import glob
import argparse
import json
import skimage.transform
import skimage.exposure

class State():
    def __init__(self, path, files, jsonpath):
        if files is None:
            self.path = path
            print(self.path)
            self.files = glob(os.path.join(path,"*.tiff"))
        else:
            self.files = files
        plt.rcParams['keymap.save'] = ['ctrl+s'] # free up s
        self.jsonpath = jsonpath 
        self.fig, self.axes = plt.subplots(1, 1)
        try:
            with open(jsonpath) as jp:
                self.file_dict = json.load(jp)
        except FileNotFoundError as e:
            self.file_dict = {}
        self.current = 0 
        self.image_handle = self.axes.imshow(np.zeros((2048,2048,3))) #, vmin = 0, vmax=self.max_val)None
        self.shift_image(0)
        self.fig.canvas.draw()


    def on_key_press(self, event):
        print('press', event.key)
        if event.key == 'q':
            self.file_dict[self.files[self.current]] = "center"
            self.shift_image(0) 
        elif event.key == 'w':
            self.file_dict[self.files[self.current]] = "middle"
            self.shift_image(0) 
        elif event.key == 'e':
            self.file_dict[self.files[self.current]] = "edge"
            self.shift_image(0) 
        elif event.key == 'right':
            self.shift_image(1)
        elif event.key == 'left':
            self.shift_image(-1)
        elif event.key == 's':
            with open(self.jsonpath, "w") as jp:
                json.dump(self.file_dict, jp)
                print("saving")
        self.fig.canvas.draw()


    def my_imshow(self, array):
        #shrink = skimage.transform.pyramid_reduce(array, downscale=5)
        #self.image_handle.set_data(shrink[:,:,0])
        floated = array.astype(np.float)
        scaled = skimage.exposure.rescale_intensity(floated,
                                                     in_range='image',
                                                     out_range=(0,1))
        self.image_handle.set_data(scaled) 
        try: 
            loc = self.file_dict[self.files[self.current]]
        except KeyError:
            loc = "N"
        self.axes.set_title(os.path.basename(self.files[self.current]) + " " +loc)
        self.fig.canvas.draw()

    def shift_image(self, shift):
        print(self.files)
        if self.current == len(self.files)-1 and shift >0:
            print("end")
        elif self.current == 0 and shift < 0:
            print("start")
        else:
            self.current += shift
            self.my_imshow(read_lsm(self.files[self.current]))
        self.fig.canvas.draw()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory' )
    parser.add_argument('-f', '--files', nargs="+" )
    parser.add_argument('-o', '--output', type=str)
    pa = parser.parse_args()

    jsp = pa.output 

    if pa.directory:
        state = State(pa.directory, None, jsp)
    elif pa.files:
        state = State(None, pa.files, jsp)

    state.fig.canvas.mpl_connect('key_press_event', state.on_key_press)

    plt.show()
