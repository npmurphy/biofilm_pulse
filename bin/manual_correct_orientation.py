import numpy as np
import matplotlib.pyplot as plt
from lib.common import read_lsm
import tifffile 
import os.path
from glob import glob
import argparse
import gc
import skimage.transform

class State():
    def __init__(self, path, files):
        if files is None:
            self.path = path
            #self.files = glob(os.path.join(path,"*.tiff"))
            self.files = glob(os.path.join(path,"*.lsm"))
        else :
            self.files = files
        #self.zmax, self.xmax, self.ymax  = tifffile.imread(self.files[0]).shape
        
        self.fig, self.axes = plt.subplots(1, 1)
        self.current = 0 
        self.image_handle = self.axes.imshow(np.zeros((10,10), dtype=np.uint16), cmap=plt.cm.hot) #, vmin = 0, vmax=self.max_val)None
        self.shift_image(0)


    def on_key_press(self, event):
        print('press', event.key)
        filename = self.files[self.current]
        if event.key == 'f':
            print("flip: {0}".format(self.files[self.current]))
            im = tifffile.imread(filename)
            mktime = os.stat(filename).st_mtime
            tifffile.imsave(filename, np.rot90(im, 2))
            os.utime(filename, (mktime, mktime))
            del im 
            self.shift_image(0)
        elif event.key == '<':
            print("rotate left: {0}".format(self.files[self.current]))
            im = tifffile.imread(filename)
            mktime = os.stat(filename).st_mtime
            tifffile.imsave(filename, np.rot90(im, 1))
            del im 
            os.utime(filename, (mktime, mktime))
            self.shift_image(0)
        elif event.key == '>':
            print("rotate right: {0}".format(self.files[self.current]))
            im = tifffile.imread(filename)
            mktime = os.stat(filename).st_mtime
            tifffile.imsave(filename, np.rot90(im, 3))
            del im 
            os.utime(filename, (mktime, mktime))
            self.shift_image(0)
        elif event.key == 'n':
            print("gimp {0}".format(self.files[self.current]))
        elif event.key=='left':
            self.shift_image(-1)
            #self.time = self.time - 1
        elif event.key=='right':
            self.shift_image(1)
            #self.time = self.time + 1
        #self.update_plots()
        if event.key in [ 'x']:
            print("deleteing: {0}".format(filename))
            os.remove(filename)
        self.fig.canvas.draw()


    def my_imshow(self, array):
        shrink = skimage.transform.pyramid_reduce(array, downscale=5)
        self.image_handle.set_data(shrink[:,:,0])
        #self.axes[1].imshow(array[:,:,1], cmap=common.hotg) #, vmin = 0, vmax=self.max_val)
        self.axes.set_title(os.path.basename(self.files[self.current]))
        gc.collect()

    def shift_image(self, shift):
        if self.current == len(self.files)-1 and shift >0:
            print("end")
        elif self.current == 0 and shift < 0:
            print("start")
        else:
            self.current += shift
            self.my_imshow(read_lsm(self.files[self.current]))



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory' )
    parser.add_argument('-f', '--files', nargs="+" )
    pa = parser.parse_args()

    if pa.directory:
        state = State(pa.directory, None)
    elif pa.files:
        state = State(None, pa.files)


    state.fig.canvas.mpl_connect('key_press_event', state.on_key_press)

    plt.show()
