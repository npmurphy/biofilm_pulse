import datetime
import os.path
import shutil
import sys

import matplotlib.pyplot as plt
import matplotlib.widgets as mplw
from matplotlib import path as mplpath
import numpy as np
import scipy.io
import skimage.measure
import skimage.morphology
import tifffile

from lib import file_finder
from lib import tiff


class Editor():

    def __init__(self, filepath, editorsize, maskname, channel, remove_chan_in_path=False, vmax=0.25):

        try:
            print(filepath)
            self.bg_img = tifffile.imread(filepath)
            if channel >= 0:
                self.bg_img = self.bg_img[:, :, channel]
            self.easypath = "/".join(os.path.dirname(filepath).split(os.path.sep)[-2:])
            matpath = os.path.splitext(filepath)[0] + ".mat"
            if remove_chan_in_path:
                matpath = matpath.replace("_cr.", ".")
            self.maskpath = file_finder.get_labeled_path(matpath, maskname)
            self.maskname = maskname
            self.data = scipy.io.loadmat(self.maskpath)
            self.segmentation = self.data["image"]
        except FileExistsError as e:
            print(e)
            sys.exit(2)
        self.number_of_features = len(np.unique(self.segmentation)) - 1
        self.backup_segmentation = self.segmentation.copy()
        self.img_size = self.bg_img.shape

        self.fig = plt.figure()

        self.add_action = "add"
        #self.loop_action = "draw"
        # keymap.all_axes ['a']
        # keymap.back ['left', 'c', 'backspace']
        # keymap.forward ['right', 'v']
        # keymap.fullscreen ['f', 'ctrl+f']
        # keymap.grid ['g']
        # keymap.home ['h', 'r', 'home']
        # keymap.pan ['p']
        # keymap.quit ['ctrl+w', 'cmd+w']
        # keymap.save ['s', 'ctrl+s']
        # keymap.xscale ['k', 'L']
        # keymap.yscale ['l']
        # keymap.zoom ['o']
        plt.rcParams['keymap.save'] = ['ctrl+s'] # free up s
        plt.rcParams['keymap.fullscreen'] = ['ctrl+f'] # free up f
        plt.rcParams['keymap.home'] = [''] # free up h

        self.brush_size = 1
        self.brush_color = 1
        self.ax_img = plt.subplot(1, 1, 1)
        self.ax_img.set_title(self.make_title())
        imgcmap = "bone"
        #imgcmap = "viridis"
        self.art_img = self.ax_img.imshow(self.bg_img,
                                          cmap=plt.get_cmap(imgcmap),
                                          vmin=0, vmax=vmax*(np.iinfo(self.bg_img.dtype).max),
                                          interpolation="nearest")

        self.art_hlt = self.ax_img.scatter([], [], s=80, facecolors='none', edgecolors='r')
        self.art_hlt.set_visible(False)

        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg = self.ax_img.imshow(self.msk_seg, cmap=plt.get_cmap("Reds_r"), alpha=0.4, interpolation="nearest")

        self.lasso = mplw.LassoSelector(self.ax_img, onselect=self.onselect)
        self.lasso.set_active(True)
        self.rectangle = mplw.RectangleSelector(self.ax_img, onselect=self.onrectselect)
        self.rectangle.set_active(False)
        #self.lasso.disconnect_events()

    def make_title(self):
        return "{0} {1} BRUSH:{2} {3}".format(self.easypath, self.maskname, self.brush_size, self.add_action)

    def highlight(self):
        if self.art_hlt.get_visible():
            print("was visible, hiding")
            self.art_hlt.set_visible(False)
        else:
            print("was not visible showing")
            lab, _ = scipy.ndimage.measurements.label(self.segmentation)
            rr = []
            cc = []
            for r in skimage.measure.regionprops(lab):
                if r.area < 10:
                    rr += [r.centroid[1]]
                    cc += [r.centroid[0]]
            print(rr, cc)
            self.art_hlt.remove()
            self.art_hlt = self.ax_img.scatter(rr, cc, s=80, facecolors='none', edgecolors='r')
            self.art_hlt.set_visible(True)
            self.fig.canvas.draw_idle()

    def remove_pixels(self):
        skimage.morphology.remove_small_objects(self.segmentation, min_size=10, in_place=True)
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()

    """
        On lasso select
    """
    def onrectselect(self, start, release):
        print(' startposition : (%f, %f)' % (start.xdata, start.ydata))
        print(' endposition   : (%f, %f)' % (release.xdata, release.ydata))
        xs = np.round(np.array([ start.xdata, start.xdata, release.xdata, release.xdata])).astype(int)
        ys = np.round(np.array([ start.ydata, release.ydata, release.ydata, start.ydata])).astype(int)
        print(xs, ys)
        rr, cc = skimage.draw.polygon(ys, xs, self.segmentation.shape)
        print(rr, cc)
        if self.add_action == "add":
            self.segmentation[rr, cc] = True
            print("adding")
        elif self.add_action == "remove":
            self.segmentation[rr,cc] = False
            print("removing")
        
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        print("rectangle went well")
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()

    def onselect(self, verts):
        path = mplpath.Path(verts)
        positive = path.vertices
        #print()
        positive[positive < 0] = 0.0
        path = np.round(positive).astype(np.uint32)
        rr, cc = path[:, 1], path[:, 0]
        rr[rr >= self.img_size[0]] = self.img_size[0] - 1
        cc[cc >= self.img_size[1]] = self.img_size[1] - 1

        #lrr, lcc = skimage.draw.line()

        #get the zone extents
        mxc, mnc = np.max(cc) + self.brush_size, np.min(cc) - self.brush_size
        mxr, mnr = np.max(rr) + self.brush_size, np.min(rr) - self.brush_size
        mxr, mxc = min(self.img_size[0]-1, mxr), min(self.img_size[1]-1, mxc)
        mnr, mnc = max(0, mnr), max(0, mnc)
        slcc = mxc - mnc
        slrr = mxr - mnr

        #draw the lines
        drew = np.zeros((slrr+1, slcc+1), dtype=bool)
        drew[rr-mnr, cc-mnc] = True
        brush = skimage.morphology.disk(self.brush_size - 1, dtype=bool)
        drew = skimage.morphology.binary_dilation(drew, selem=brush)

        drew = scipy.ndimage.morphology.binary_fill_holes(drew.astype(int)).astype(bool)

        if self.add_action == "add":
            delta = self.segmentation[mnr:mxr+1, mnc:mxc+1] | drew
            #self.segmentation[mnr:mxr+1, mnc:mxc+1] = delta
            #self.msk_seg.mask[mnr:mxr+1, mnc:mxc+1] = ~delta
            #self.segmentation = self.segmentation | ndrew
        elif self.add_action == "remove":
            delta = self.segmentation[mnr:mxr+1, mnc:mxc+1] & (~drew)
        
        self.segmentation[mnr:mxr+1, mnc:mxc+1] = delta
        # failing to speed up masked array updating
        #self.msk_seg[mnr:mxr+1, mnc:mxc+1] = delta # this unmasks all the square
        #ndr, ndc = np.where(~delta) 
        #self.msk_seg.mask[mnr+ndr, mnc+ndc] = True #np.ma.masked  # now remask 
        #self.msk_seg.mask[np.where(delta)] = False #np.masked 
        #mnr:mxr+1, mnc:mxc+1] = ~delta
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)

        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()
        # self.canvas.draw()


    def clear_segmentation(self):
        self.segmentation[:, :] = 0.0
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()
        #self.fig.canvas.draw()
    
    def save_segmentation(self, path):
        ndata = {#"train_x": self.data_x
                #,
                "image": self.segmentation.astype(bool)
                #, "train_i": self.data_i
                }
        self.data.update(ndata)
        ext = '.{:%Y-%m-%d_%H-%M}'.format(datetime.datetime.now())
        shutil.move(self.maskpath, self.maskpath + ext)
        scipy.io.savemat(self.maskpath, self.data)


    def on_key_press(self, event):
        print("type", event.key)
        #if event.key == 'control':
        #    self.lasso.set_active(True)
            #print("lasso about to add", self.lasso.cids)
            #self.lasso.connect_default_events()
            #print("lasso added add", self.lasso.cids)
            #self.fig.canvas.mpl_disconnect(self.click_catcher)
        if event.key == 'r':
            self.lasso.set_active(~self.lasso.get_active())
            self.rectangle.set_active(~self.rectangle.get_active())
            #self.rectangle.set_active(True)
        elif event.key == "h":
            self.highlight()
        elif event.key == "d":
            self.remove_pixels()
        elif event.key == 'shift':
            print("toggle action")
            old = self.add_action
            if self.add_action == "remove":
                self.add_action = "add"
            elif self.add_action == "add":
                self.add_action = "remove"
            print("new action", self.add_action)
            self.ax_img.set_title(self.make_title())
            self.fig.canvas.draw_idle()
            #self.fig.canvas.draw()
       # elif event.key == 'z':
       #     # self.add_pnt_listn = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
       #     old = self.loop_action
       #     if self.loop_action == "fill":
       #         self.loop_action = "draw"
       #     elif self.loop_action == "draw":
       #         self.loop_action = "fill"
       #     print("new action", self.loop_action)
       #     self.ax_img.set_title(self.ax_img.get_title().replace(old.upper(), self.loop_action.upper() ))
       #     self.fig.canvas.draw()
        elif event.key == "f":
            self.segmentation =  scipy.ndimage.morphology.binary_fill_holes(self.segmentation)#.astype(bool)).astype(np.float)
            self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
            self.art_seg.set_data(self.msk_seg)
            self.fig.canvas.draw_idle()
            #self.fig.canvas.draw()
        elif event.key == "s":
            self.art_seg.set_visible(not self.art_seg.get_visible())
            self.fig.canvas.draw_idle()
            #self.fig.canvas.draw()
        elif event.key == "i":
            self.art_img.set_visible(not self.art_img.get_visible())
            self.fig.canvas.draw_idle()
        elif event.key == 'w':
            print("Saving image")
            self.save_segmentation("path")
        elif event.key == 'x':
            print("clear segmentation")
            self.clear_segmentation()
        elif event.key in "1234567890":
            if event.key == "0":
                event.key = "10"
            self.brush_size = int(event.key)
            self.ax_img.set_title(self.make_title())
            self.ax_img.set_navigate(True)

            self.fig.canvas.draw_idle()
        else:
            print("Pressing {0} does nothing yet".format(event.key))

    #def on_key_release(self, event):
        #print("release:", event.key)
        ##if event.key == "control":
        ##    self.lasso.set_active(False)
        # elif event.key == 'r':
        #     self.lasso.set_active(False)
        #     self.rectangle.set_active(False)
            #print("Lasso Pre disconnect", self.lasso.cids)
            #self.lasso.disconnect_events()
            #self.click_catcher = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
            #print("Lasso post disconnect", self.lasso.cids)
