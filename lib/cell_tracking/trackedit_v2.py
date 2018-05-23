import argparse
import datetime
import os.path
import shutil
from glob import glob

import matplotlib
matplotlib.use('TKAgg')

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.widgets as mplw
import numpy as np
import parse
import scipy.io
import scipy.ndimage.morphology
import skimage.draw
import skimage.io
import skimage.morphology
import skimage.segmentation
import skimage.exposure
import tifffile
from matplotlib import path as mplpath
import pandas as pd
import compile_cell_tracks

from lib.cmaps import cmrand
from lib.util.tiff import get_shape
from lib.cell_segmenter import laphat_segment_v1 as laphat_segment

import re

print(re.sub(r"{\d?:\d+d}", "(\d+)", "img_{0:03d}.tif"))

class State():

    def __init__(self, filepattern, segpattern, image_start=1, cell_start=1, viewmethod="straight", vmax=1.0, image_range=(None,None)):
        self.filepattern = filepattern
        self.segpattern = segpattern
        print(re.sub(r"{\d?:\d+d}", "(\d+)", self.filepattern))
        self.parse_re = re.compile(re.sub(r"{\d?:\d+d}", "(\d+)", self.filepattern))
        # print(filepattern)
        # print(filepattern.format(2))
        if image_range == (None, None):
            tmppattern_st = filepattern.split("{")[0]
            tmppattern_ed = filepattern.split("}")[1]

            def parse_number(filepath):
                #print(self.filepattern.replace("03", ""))
                #parsed = parse.parse(self.filepattern.replace(":03", ""), filepath) ## fucking useless lib cant deal with format strings
                print(filepath)
                parsed = self.parse_re.match(filepath).groups()
                #parsed = parse.parse(self.filepattern.replace(":03", ""), filepath) ## fucking useless lib cant deal with format strings
                return int(parsed[0])
            print(glob(tmppattern_st + "*" + tmppattern_ed))
            self.image_range = sorted([parse_number(f) for f in glob(tmppattern_st + "*" + tmppattern_ed)])
        else:
            self.image_range = list(image_range[0], image_range[1])
        print("Image range is {0}".format(self.image_range))
        
        #self.maskname = "cells" #maskname
        #TODO When we make the gui the axes is set to be the inital img_size
        # If I set the data using set_data, the axis do not update. 
        # Trying to plot things like numbers on that makes the background image be scaled over the initial 
        # size while the plots go to the initial place. to avoid that I am 
        # getting an inital size an settign it to be the image size. :()
        init_shape = get_shape(self.filepattern.format(self.image_range[0]))
        self.vmaxs = vmax
        self.all_cells = np.empty((10, 10), np.dtype("uint16"))
        self.segmentation = np.empty((10, 10), np.dtype("uint16"))
        self.cells = np.empty(0, np.dtype("uint16"))
        self.current_cell_id = cell_start
        self.current_image = image_start
        self.current_path = ""
        self.maskpath = ""
        self.view_methods = {"straight": (2, lambda x: x),
                             #"laphat": (3, lambda x: laphat_segment.laphat_segment_v1_view(x, cell_width_pixels=9)),
                             "laphat": (3, self.custom_laphat),
                             "exager": (3, self.custom_laphat),
                             "gauss" : (2, lambda x : skimage.filters.gaussian(x, 2)),
                             "gamma" : (3, self.gamma),
                              }
        dim, self.view_method = self.view_methods[viewmethod]
        if dim == 3:
            self.img_size = init_shape + (dim,)
        else:
            self.img_size = init_shape


        self.fig = plt.figure()
        self.gridspec = gridspec.GridSpec(3, 1, height_ratios=[1, 0.05, 0.1])
        self.cmrand = matplotlib.colors.ListedColormap(np.random.rand(100000, 3))

        self.add_color = 1

        plt.rcParams['keymap.save'] = ['ctrl+s'] # free up s
        plt.rcParams['keymap.fullscreen'] = ['ctrl+f'] # free up f
        plt.rcParams['keymap.home'] = [''] # free up a and r
        plt.rcParams['keymap.back'] = ['backspace']
 
        self.brush = 1
        #self.ax_img = plt.subplot(1, 1, 1)
        self.ax_img = plt.subplot(self.gridspec[0])
        self.ax_img.set_title(self.make_title())
        self.ax_img.name = "cell_viewer"
        #imgcmap = "bone"
        self.bg_img = np.zeros(init_shape)
        self.segmentation = np.zeros(init_shape) 
        self.other_segmentation = np.zeros(init_shape)
        self.msk_otr = np.ma.masked_equal(self.other_segmentation, 0)
        self.msk_seg = np.ma.masked_where(self.segmentation == 0, np.ones(init_shape, dtype=np.bool))
        self.text_labels = []
        imgcmap = "viridis"
        
        if len(self.bg_img.shape) == 2:
            self.art_img = self.ax_img.imshow(self.bg_img, cmap=plt.get_cmap(imgcmap), vmin=0, vmax=0.3, interpolation="nearest")
        elif len(self.bg_img.shape) == 3:
            self.art_img = self.ax_img.imshow(self.bg_img, vmin=0, interpolation="nearest")
        self.art_seg = self.ax_img.imshow(self.msk_seg, cmap=plt.get_cmap("Reds_r"), alpha=0.5, interpolation="nearest")
        self.art_otr = self.ax_img.imshow(self.msk_otr, cmap=self.cmrand, alpha=0.6, interpolation="nearest")

        self.lasso = mplw.LassoSelector(self.ax_img, onselect=self.onselect)
        self.lasso.set_active(True)
        self.cell_clicker = self.fig.canvas.mpl_connect('button_press_event', self.select_cell)

        self.ax_cell_id_select = plt.subplot(self.gridspec[1])
        self.art_cell_id_select = self.ax_cell_id_select.scatter(self.cells, np.ones_like(self.cells), c=self.cells, cmap=self.cmrand)
        self.ax_cell_id_select.name = "cell_picker"
        self.art_cell_id_selector = self.fig.canvas.mpl_connect('button_press_event', self.select_cell_id_from_id_axis)
        
        self.ax_cell_trace = plt.subplot(self.gridspec[2])
        """
        try: 
            #print(self.pattern.format(1).replace('_t1.TIF', "_compile.tsv", sep="\t")
            # compile_cell_tracks.get_
            # start_of_format = os.path.basename(self.filepattern).find("{")
            # compilefile = os.path.basename(self.filepattern[:start_of_format], "_compile.tsv")
            # compilepath = os.path.join(os.path.dirname(self.filepattern), compilefile)
            #print(os.path.join("../biofilm_movie/", compilepath))
            self.traces = compile_cell_tracks.compile(self.filepattern, self.segpattern, {"rfp":0, "yfp":1})
            print(self.traces.head())
            for ci in np.unique(self.traces.cell_id):
                thiscell = self.traces[self.traces["cell_id"] == ci]
                print(ci)
                self.ax_cell_trace.plot(thiscell["timep"], thiscell["ratio"], label=str(ci))
        except Exception as e:
            print("what exception")
            print(e)
            self.traces = None
        """
        self.cur_image_art = self.ax_cell_trace.axvspan(self.current_image-0.5, self.current_image+0.5, color="grey", alpha=0.4) 
        self.ax_cell_trace.legend()
        self.ax_cell_trace.name = "cell_trace"

        self.move_ui_to_image(self.current_image)
        
    def select_cell_id_from_id_axis(self, event):
        print(event)
        if not event.inaxes.name == "cell_picker":
            return 
        selected_id = int(event.xdata)
        print("selected cell", selected_id)
        self.current_cell_id = selected_id
        if self.current_cell_id in self.cells:
            self.move_to_cell(self.current_cell_id)

    # def set_current_cell_textbox(self, text):
    #     try:
    #         number = int(text)
    #     except ValueError:
    #         self.txtbox_cell.set_color("pink")
    #         return None
        
    #     if number in self.image_range:
    #         self.txtbox_cell.set_color("white")
    #         self.move_to_cell(number)
    #     else:
    #         self.txtbox_cell.set_color("orange")
    #         self.add_cell(number)
    def _get_cell_index(self, cellid):
        return np.where(self.cells == cellid)[0][0]

    def _jump_relativly_in_cell_list(self, jump):
        current = self._get_cell_index(self.current_cell_id)
        return self.cells[current + jump]

    def move_ui_to_image(self, imagen):
        self.move_to_image(imagen)
        self.get_mask_files_and_create_if_needed()
        self.update_ui()


    # def get_mask_path(self, filep):
    #     #self.easypath = "/".join(os.path.dirname(filepattern).split(os.path.sep)[-2:])
    #     return os.path.join(os.path.dirname(filep), "segmented", os.path.basename(filep))
    #     #return os.path.splitext(filep)[0] + ".mat"
    #     #self.maskpath = dmatpath #util.file_finder.get_labeled_path(matpath, maskname)


    def make_title(self):
        mode = "ADD" if self.add_color else "DEL"
        #vals = (self.easypath,
        vals = (self.current_image,
                "", #self.maskname,
                self.brush,
                mode,
                self.current_cell_id,
                len(self.cells))
        return "Image:{0} {1} BRUSH:{2} {3} Cell#{4}: of {5}".format(*vals)

    def exagerate_image(self, img):
        img_sobel = skimage.filters.sobel(img)
        img_sobel_sobel = skimage.filters.sobel(img_sobel)
        img_sobel_sobel_01 = skimage.exposure.rescale_intensity(img_sobel_sobel, out_range=(0,1))
        img_gauss_01 = skimage.exposure.rescale_intensity(img, out_range=(0, 1.0))
        cell_width = 11
        cell_disc = skimage.morphology.disk(cell_width/2)
        img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
        img_hat_01 = skimage.exposure.rescale_intensity(img_hat, out_range=(0,1.0))
        return np.dstack([img_hat_01, img_sobel_sobel_01, img])
        #return img_hat_01

    def custom_laphat(self, img):
        cell_width_pixels = 4
        img_gauss = skimage.filters.gaussian(img[:,:,0], 1.1)
        img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
        cell_disc = skimage.morphology.disk(cell_width_pixels/2)
        img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
        img_lap = skimage.filters.laplace(img_gauss, ksize=10)
        img_lap[img_lap < 0] = 0 
        img_lap = img_lap * (1.0 / img_lap.max()) 
        img_hat = img_hat * (1.0 / img_hat.max()) 
        return np.dstack([img_lap, img_hat, img_gauss_01**2])

    def gamma(self, img):
        cell_width_pixels = 3
        cell_disc = skimage.morphology.disk(cell_width_pixels/2)
        img_gauss = skimage.filters.gaussian(img[:,:,0], 1.0)
        img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
        img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
        exim = skimage.exposure.adjust_gamma(img_gauss_01, gamma=0.9)
        return np.dstack([exim, img_hat, np.zeros_like(exim)])

    def move_to_image(self, number):
        if number not in self.image_range:
            print("{0} is not in the list of images {1}".format(number, self.image_range))
            pass
        else:
            self.current_image = number
            self.current_path = self.filepattern.format(number)
            #self.maskpath = self.get_mask_path(self.current_path)
            self.maskpath = self.segpattern.format(number)
            #img_gauss = skimage.filters.gaussian(tifffile.imread(self.current_path), 1)
            img = tifffile.imread(self.current_path)
            #self.bg_img = self.exagerate_image(img_gauss)
            self.bg_img = self.view_method(img) 
            #self.bg_img = img_gauss 
            self.img_size = self.bg_img.shape[0:2]

    def get_mask_files_and_create_if_needed(self):
        try:
            #matdata = skimage.io.imread(self.maskpath)
            #matdata = skimage.io.imread(self.maskpath)
            self.all_cells = skimage.io.imread(self.maskpath)# matdata["image"]
            if len(self.all_cells.shape) > 2:
                self.all_cells = np.zeros(self.bg_img.shape[:2], dtype=np.dtype("uint16"))

        except FileNotFoundError as e:
            self.all_cells = np.zeros(self.bg_img.shape[:2], dtype=np.dtype("uint16"))
            #scipy.io.savemat(self.maskpath, {"image": self.all_cells})
            skimage.io.imsave(self.maskpath, self.all_cells)
        except KeyError as e:
            self.segmentation = np.zeros_like(self.bg_img, dtype=np.dtype("uint16"))
            #matdata["image"] = self.segmentation
            #scipy.io.savemat(self.maskpath, matdata)
            skimage.io.imsave(self.maskpath, self.segmentation)
        self.cells = np.unique(self.all_cells)[1:]
        print("Loading cell data:", self.cells)

        if len(self.cells) >= 1:
            if self.current_cell_id == 0:
                self.current_cell_id = self.cells.min()
            elif self.current_cell_id > self.cells.max():
                self.current_cell_id = self.cells.min()
            else:
                pass
        else:
            self.current_cell_id = 0
        print("getting cell indexes from ", self.cells)
        print("cell id is ", self.current_cell_id)


    def update_ui(self):
        self.segmentation = self.all_cells == self.current_cell_id
        self.other_segmentation = self.all_cells - (self.segmentation.astype(np.int) * self.current_cell_id)
        self.msk_otr = np.ma.masked_equal(self.other_segmentation, 0)
        self.msk_seg = np.ma.masked_where(self.segmentation == 0, np.ones(self.img_size, dtype=np.bool))
        self.art_img.set_data(self.bg_img)
        self.art_img.set_clim(vmax=self.bg_img.max()*self.vmaxs)
        self.art_seg.set_data(self.msk_seg)
        #self.art_seg = self.ax_img.imshow(self.msk_seg, cmap=plt.get_cmap("Reds_r"), alpha=0.4, interpolation="nearest")
        #self.art_otr = self.ax_img.imshow(self.msk_otr, cmap=self.cmrand, alpha=0.4, interpolation="nearest")
        self.art_otr.set_data(self.msk_otr)
        self.ax_img.set_title(self.make_title())
        for ot in self.text_labels:
            print("removing old labels")
            ot.remove()
        regionp = skimage.measure.regionprops(self.all_cells)
        self.text_labels = [self.ax_img.text(r.centroid[1], r.centroid[0], str(r.label)) for r in regionp]
        if len(self.cells) == 0:
            cellwzero = np.arange(0, 10)# np.insert(self.cells, 0, [0]) 
        else:
            cellwzero = np.arange(0, self.cells.max() + 10)# np.insert(self.cells, 0, [0]) 
        self.art_cell_id_select = self.ax_cell_id_select.scatter(cellwzero, np.ones_like(cellwzero), c=cellwzero, cmap=self.cmrand)
        self.ax_cell_id_select.name = "cell_picker"
        
        self.cur_image_art.remove() 
        self.cur_image_art = self.ax_cell_trace.axvspan(self.current_image-0.5, self.current_image+0.5, color="grey", alpha=0.4) 

        self.fig.canvas.draw_idle()


    def select_cell(self, event):
        if event is None:
            return None
        if ((not event.inaxes.name == "cell_viewer") or self.lasso.get_active()): # not selected
            return None
 
        print(event)
        # the click locations
        x = event.xdata
        y = event.ydata
        print("selected cell", self.all_cells[int(y), int(x)])
        cell = self.all_cells[int(y), int(x)]
        if cell == 0:
            return True
        #index = np.where(self.cells == cell)[0][0]
        self.move_to_cell(cell)

    # def select_cell_id_from_id_axis(self, event):
    #     print(event)
    #     # the click locations
    #     x = event.xdata
    #     y = event.ydata
    #     print("selected cell", self.all_cells[int(y), int(x)])
    #     cell = self.all_cells[int(y), int(x)]
    #     if cell == 0:
    #         return True
    #     #index = np.where(self.cells == cell)[0][0]
    #     self.move_to_cell(cell)

    def onselect(self, verts):
        # if (not verts.inaxes.name == "cell_viewer"):
        #     return None
        path = mplpath.Path(verts)
        positive = path.vertices
        #print()
        positive[positive < 0] = 0.0
        path = np.round(positive).astype(np.dtype("uint32"))
        rr, cc = path[:, 1], path[:, 0]
        rr[rr >= self.img_size[0]] = self.img_size[0] - 1
        cc[cc >= self.img_size[1]] = self.img_size[1] - 1

        #lrr, lcc = skimage.draw.line()

        #get the zone extents
        mxc, mnc = np.max(cc) + self.brush, np.min(cc) - self.brush
        mxr, mnr = np.max(rr) + self.brush, np.min(rr) - self.brush
        mxr, mxc = min(self.img_size[0]-1, mxr), min(self.img_size[1]-1, mxc)
        mnr, mnc = max(0, mnr), max(0, mnc)
        slcc = mxc - mnc
        slrr = mxr - mnr

        #draw the lines
        drew = np.zeros((slrr+1, slcc+1), dtype=bool)
        drew[rr-mnr, cc-mnc] = True
        brush = skimage.morphology.disk(self.brush - 1, dtype=bool)
        drew = skimage.morphology.binary_dilation(drew, selem=brush)

        drew = scipy.ndimage.morphology.binary_fill_holes(drew.astype(int)).astype(bool)

        if self.add_color == 1: # "add":
            delta = self.segmentation[mnr:mxr+1, mnc:mxc+1] | drew
            #self.segmentation[mnr:mxr+1, mnc:mxc+1] = delta
            #self.msk_seg.mask[mnr:mxr+1, mnc:mxc+1] = ~delta
            #self.segmentation = self.segmentation | ndrew
        elif self.add_color == 0: #"remove":
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


    def move_to_cell(self, num):
        cell_index = self._get_cell_index(num)
        if len(self.cells) == 0:
            self.current_cell_id = 0
            # self.ax_img.set_xlim(mnc - z, mxc + z)
            # self.ax_img.set_ylim(mxr + z, mnr - z) # we want it the right way up
            self.fig.canvas.draw_idle()
        else:
            self.current_cell_id = num #self.cells[self.current_cell_index]
            print("at cell {0}".format(self.current_cell_id))
            self.segmentation = self.all_cells == self.current_cell_id
            #self.other_segmentation = self.all_cells.astype(bool) & (~self.segmentation)
            self.other_segmentation = self.all_cells - (self.segmentation.astype(np.int) * self.current_cell_id)

            #print("Should be {0} pixels".format(np.count_nonzero(self.segmentation)))
            self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
            self.msk_otr = np.ma.masked_equal(self.other_segmentation, 0)
            self.art_seg.set_data(self.msk_seg)
            self.art_otr.set_data(self.msk_otr)
            self.ax_img.set_title(self.make_title())
            if np.count_nonzero(self.segmentation) > 0:
                rr, cc = np.where(self.segmentation == True)
                mnr, mnc = np.min(rr), np.min(cc)
                mxr, mxc = np.max(rr), np.max(cc)
                z = 70
                self.ax_img.set_xlim(mnc - z, mxc + z)
                self.ax_img.set_ylim(mxr + z, mnr - z) # we want it the right way up
            self.fig.canvas.draw_idle()
 

    def save_segmentation(self, path):
        print("saving", self.current_cell_id)
        self.all_cells[self.all_cells == self.current_cell_id] = 0#  np.where(self.segmentation)
        self.all_cells[self.segmentation] = self.current_cell_id
        #ndata = {"image": self.all_cells}
        #self.all_cells.update(ndata)
        ext = '.{:%Y-%m-%d_%H-%M}'.format(datetime.datetime.now())
        shutil.move(self.maskpath, self.maskpath + ext)
        #scipy.io.savemat(self.maskpath, ndata)# self.all_cells)
        skimage.io.imsave(self.maskpath, self.all_cells)# self.all_cells)
    
    def dilate_segmentation(self):
        self.segmentation = skimage.morphology.binary_dilation(self.segmentation)
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()

    def add_new_cell(self, num):
        print("Adding cell {0}", num)
        self.current_cell_id = num
        self.cells = np.append(self.cells, self.current_cell_id)

        self.segmentation = np.zeros_like(self.segmentation, dtype=np.bool)
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()

    def add_object(self):
        print("Adding a cell")
        if len(self.cells) == 0:
            new_cell_id = 1
        else:
            new_cell_id = self.cells.max() + 1
        self.add_new_cell(new_cell_id)
        self.fig.canvas.draw_idle()


    def clear_segmentation(self):
        self.segmentation[:, :] = 0.0
        self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
        self.art_seg.set_data(self.msk_seg)
        self.fig.canvas.draw_idle()
        #self.fig.canvas.draw()

    def on_key_press(self, event):
        print("type", event.key)
        #if event.key == 'control':
        #    self.lasso.set_active(True)
            #print("lasso about to add", self.lasso.cids)
            #self.lasso.connect_default_events()
            #print("lasso added add", self.lasso.cids)
            #self.fig.canvas.mpl_disconnect(self.click_catcher)
        if event.key == 'shift':
            if self.add_color == 1:
                self.add_color = 0
            elif self.add_color == 0:
                self.add_color = 1
            print("new action", self.add_color)
            self.ax_img.set_title(self.make_title())
            self.fig.canvas.draw_idle()
        elif event.key == "left":
            self.move_to_cell(self._jump_relativly_in_cell_list(-1))
        elif event.key == "right":
            self.move_to_cell(self._jump_relativly_in_cell_list(+1))
        elif event.key == "a":
            self.add_object()
        elif event.key == 'z':
            r, c = self.img_size
            self.ax_img.set_xlim(0, c)
            self.ax_img.set_ylim(r, 0) # we want it the right way up
            self.fig.canvas.draw_idle()
        elif event.key == "c":
            self.lasso.set_active(False)

        elif event.key == "f":
            self.segmentation = scipy.ndimage.morphology.binary_fill_holes(self.segmentation)#.astype(bool)).astype(np.float)
            self.msk_seg = np.ma.masked_equal(self.segmentation, 0)
            self.art_seg.set_data(self.msk_seg)
            self.fig.canvas.draw_idle()
        elif event.key == "s":
            self.art_seg.set_visible(not self.art_seg.get_visible())
            self.art_otr.set_visible(not self.art_otr.get_visible())
            self.fig.canvas.draw_idle()
        elif event.key == "i":
            self.art_img.set_visible(not self.art_img.get_visible())
            self.fig.canvas.draw_idle()
        elif event.key == 'x':
            print("disabled: clear segmentation")
            #self.clear_segmentation()
        elif event.key == 'd':
            print("Disabled: dilate segmentation")
            #self.dilate_segmentation()
        elif event.key == 'pagedown':
            self.move_ui_to_image(self.current_image + 1)
        elif event.key == 'pageup':
            self.move_ui_to_image(self.current_image - 1)
        elif event.key.lower() == 'w':
            print("Saving image")
            self.save_segmentation("path")
        elif event.key in "1234567890":
            if event.key == "0":
                event.key = "10"
            self.brush = int(event.key)
            self.ax_img.set_title(self.make_title())
            self.ax_img.set_navigate(True)
            self.fig.canvas.draw_idle()
        else:
            print("Pressing {0} does nothing yet".format(event.key))

    def on_key_release(self, event):
        if event.key == "c":
           #self.fig.canvas.mpl_dissconnect(self.cell_clicker)
           self.lasso.set_active(True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--images', type=str)
    parser.add_argument('--segmented', type=str)
    parser.add_argument('-c', '--start_cell', type=int, default=1)
    parser.add_argument('-s', '--start_image', type=int, default=1)
    parser.add_argument("--view", type=str, default="straight")
    parser.add_argument("--vmax", type=float, default=1.0 )
    #parser.add_argument('-s', '--segfile', type=str)
    pa = parser.parse_args()

    state = State(pa.images, pa.segmented, pa.start_image, pa.start_cell, pa.view, pa.vmax) #, pa.segfile)
    #lsmfiles = glob(os.path.join(pa.directory, "*.lsm"))

    state.fig.canvas.mpl_connect('key_press_event', state.on_key_press)
    state.fig.canvas.mpl_connect('key_release_event', state.on_key_release)
    # state.click_catcher = state.fig.canvas.mpl_connect('button_press_event', state.on_click)
    plt.show()
