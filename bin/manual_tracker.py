import argparse
#import os.path
import re
from glob import glob

import sys
print(sys.path)

import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
#import matplotlib.widgets as mplw
import numpy as np
#import scipy.io
#import scipy.ndimage.morphology
import skimage.draw
import skimage.exposure
import skimage.io
import skimage.morphology
import skimage.segmentation
import tifffile

from lib.cell_tracking import cell_editor
from lib.cell_tracking import cell_tracker
from lib.util.tiff import get_shape
import lib.cell_tracking.track_data as track_data
from lib.cell_tracking.track_data import TrackData
import lib.cell_tracking.compile_cell_tracks as compiledtracks 

from lib.cell_tracking import auto_match

import scipy.ndimage

matplotlib.use('TKAgg')

#TODO add state (spore etc) notification to ellipse
#TODO hide segmentation button (s)
#TODO add cell lable

######
# Bugs:
# TODO  deleting a cell causes the image moving to stop working.
# TODO sometimes a cell's parent is a string.  

class State():

    def __init__(self, filepattern, track_path, compiled_path, image_start=1, cell_start:str="1", 
                 viewmethod="straight", vmax=1.0, image_range=(None,None)):
        self.filepattern = filepattern
        self.parse_re = re.compile(re.sub(r"{\d?:\d+d}", r"(\d+)", self.filepattern))
        print(self.parse_re)
        self.image_range = self._get_image_range(image_range)
        print(self.image_range)

        self.red_chan = "ch00"
        self.green_chan = "ch01"
        self.blue_chan = "ch02"
        #self.red_chan = "_r"

        self.cell_interactor_style = { "edgecolor":"white", "facecolor":"none", "linewidth":1}
       
        self.trackdata_path = track_path
        self.compiled_path = compiled_path
        
        self.trackdata = TrackData(track_path, max(self.image_range))
        self.compileddata = compiledtracks.load_compiled_data(self.compiled_path, fail_silently=True)
        if self.compileddata is not None:
            self.compileddata["gr"] = self.compileddata["green"]/self.compileddata["red"]

        #TODO When we make the gui the axes is set to be the inital img_size
        # If I set the data using set_data, the axis do not update. 
        # Trying to plot things like numbers on that makes the background image be scaled over the initial 
        # size while the plots go to the initial place. to avoid that I am 
        # getting an inital size an settign it to be the image size. :()
        init_shape = get_shape(self.filepattern.format(self.image_range[0]))
        self.vmaxs = vmax
        self.cells = self.trackdata.cells.keys()
        self.current_cell_id = cell_start
        self.current_image = image_start
        self.current_path = ""
        self.view_methods = {"straight": (2, lambda x: x),
                             #"laphat": (3, lambda x: laphat_segment.laphat_segment_v1_view(x, cell_width_pixels=9)),
                             "3color": (3, self.bit16_to_bit8),
                             "laphat": (3, self.custom_laphat),
                             "hat": (2, self.just_gauss_hat),
                             "gauss" : (2, lambda x : skimage.filters.gaussian(x, 1.1)),
                             "gamma" : (3, self.gamma),
                              }
        dim, self.view_method = self.view_methods[viewmethod]
        if dim == 3:
            self.img_size = init_shape + (dim,)
        else:
            self.img_size = init_shape

        #######################
        ## Setting up GUI
        #######################
        self.fig = plt.figure()
        self.gridspec = gridspec.GridSpec(3, 2, height_ratios=[1, 0.1, 0.1], width_ratios=[0.6, 0.4])
        self.cmrand = matplotlib.colors.ListedColormap(np.random.rand(10000, 3))
        #self.rand_colors = np.random.rand(1000, 3)

        plt.rcParams['keymap.save'] = ['ctrl+s'] # free up s
        plt.rcParams['keymap.fullscreen'] = ['ctrl+f'] # free up f
        plt.rcParams['keymap.home'] = [''] # free up a and r
        plt.rcParams['keymap.back'] = ['backspace']
        plt.rcParams['keymap.grid'] = [''] # g 
 
        self.ax_img = plt.subplot(self.gridspec[0,0])
        self.ax_img.set_title(self.make_title())
        self.ax_img.name = "cell_viewer"
        self.bg_img = np.zeros(init_shape, dtype=np.uint16)
        self.text_labels = []
        
        #imgcmap = "bone"
        #imgcmap = "viridis"
        imgcmap = "hot"
        
        if len(self.bg_img.shape) == 2:
            self.art_img = self.ax_img.imshow(self.bg_img, cmap=plt.get_cmap(imgcmap), vmin=0, vmax=0.3, interpolation="nearest")
        elif len(self.bg_img.shape) == 3:
            self.art_img = self.ax_img.imshow(self.bg_img, vmin=0, interpolation="nearest")

        self.interactive_cell = None 
        self.non_edit_cells = []

        self.ui_selectors = []
        self.ui_selectors.append(self.fig.canvas.mpl_connect('button_press_event', self.select_cell_id_from_tree))

        self.ax_tree = plt.subplot(self.gridspec[0,1])
        self.ax_tree.name = "cell_picker"
        self.node_locs = {}

        self.ax_cell_compiled_trace = plt.subplot(self.gridspec[1,0:2])
        self.ax_cell_compiled_trace.set_xlim(0, self.trackdata.metadata["max_frames"])
        self.ax_cell_compiled_trace.name = "compiled_trace"
        self.compiled_plots = {}
        #self.art_cell_id_select = self.ax_cell_id_select.scatter(self.cells, np.ones_like(self.cells), c=self.cells, cmap=self.cmrand)
        
        self.ui_selectors.append(self.fig.canvas.mpl_connect('button_press_event', self.select_cell))
        self.ui_selectors.append(self.fig.canvas.mpl_connect('button_press_event', self.select_frame))
        
        self.ax_cell_trace = plt.subplot(self.gridspec[2,0:2], sharex=self.ax_cell_compiled_trace)
        self.comp_bar = None
        self.trace_bar = None
        self.cell_trace_plots = []
        self.cur_image_art = self.ax_cell_trace.axvspan(self.current_image-0.5, self.current_image+0.5, color="grey", alpha=0.4) 
        self.ax_cell_trace.legend()
        self.ax_cell_trace.name = "cell_trace"
                
        self.read_numbers = None
        self.read_in = ""

        self.move_ui_to_image(self.current_image)
        
    def _get_image_range(self, image_range):
        if image_range == (None, None):
            tmppattern_st = self.filepattern.split("{")[0]
            tmppattern_ed = self.filepattern.split("}")[1]

            def parse_number(filepath):
                parsed = self.parse_re.match(filepath).groups()
                return int(parsed[0])
            
            return sorted([parse_number(f) for f in glob(tmppattern_st + "*" + tmppattern_ed)])
        else:
            return list(image_range[0], image_range[1])

    
    # def select_cell_id_from_id_axis(self, event):
    #     if (not event.inaxes.name == "cell_picker"):
    #         return None
    #     x = event.xdata
    #     cell = int(np.round(x))
    #     print("selected cell", cell)
    #     if cell == 0:
    #         return True
    #     self.move_to_cell(cell)
    
    def select_cell_id_from_tree(self, event):
        if (not event.inaxes.name == "cell_picker"):
            return None
        mind = 1e18
        minc = 0
        for c, (x,y) in self.node_locs.items():
            d = np.sqrt(((x - event.xdata)**2 + (y - event.ydata)**2))
            if d < mind:
                mind = d
                minc = c
        if mind < 1:
            self.move_to_cell(str(minc))

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
    # def _get_cell_index(self, cellid):
    #     return np.where(self.cells == cellid)[0][0]


    def move_ui_to_image(self, imagen):
        self.move_to_image(imagen)
        self.move_to_cell(self.current_cell_id)

        self.update_ui()

    def make_title(self):
        vals = (self.current_image,
                "", 
                self.current_cell_id,
                len(self.cells))
        return "Image:{0} {1} Cell#{2}: of {3}".format(*vals)

    def show_non_edit_cells(self, frame):
        # get the list of existing patches. 
        for (cell, label) in self.non_edit_cells:
            cell.remove()
            #label.remove()
        self.non_edit_cells = []
        for cell_id in self.cells:
            if (cell_id != self.current_cell_id) and (self.trackdata.get_cell_state(frame, cell_id) != 0):
                cell_params = self.trackdata.get_cell_params(frame, cell_id)
                cell = cell_editor.get_cell(*cell_params, facecolor="none", edgecolor=self.cmrand(int(cell_id)), linewidth=2 )
                #text = 
                self.non_edit_cells += [(cell, cell_id)]
                self.ax_img.add_patch(cell)
        # add a number

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
    
    def bit16_to_bit8(self, im):
        def try_read(fid, ch):
            try:
                imc = skimage.io.imread(self.filepattern.format(self.current_image).replace(self.red_chan, ch))
            except FileNotFoundError as e:
                imc = np.zeros_like(im)
            return imc 

        if len(im.shape) != 3:
            ## assume red already read in in im.
            im = np.dstack([im] + [try_read(self.filepattern, c) for c in [self.green_chan, self.blue_chan]])
        # red_max = 2800
        # grn_max = 2800
        red_max = 0.08
        grn_max = 0.05

        def modify(im):
            img = skimage.filters.gaussian(im, sigma=1.1)
            print(img.max())
            return img
        imr = skimage.exposure.rescale_intensity(modify(im[:,:,0]), in_range=(0, red_max), out_range=(0,255)).astype(np.uint8)
        img = skimage.exposure.rescale_intensity(modify(im[:,:,1]), in_range=(0, grn_max), out_range=(0,255)).astype(np.uint8)
        imb = skimage.exposure.rescale_intensity(modify(im[:,:,2]), in_range=(0, 6897), out_range=(0,255)).astype(np.uint8)
        imx = np.dstack([imr, img, imb]) #np.zeros_like(imr)])
        return imx

    def custom_laphat(self, img):
        cell_width_pixels = 7.5
        img_gauss = skimage.filters.gaussian(img[:,:], 1.1)
        img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
        cell_disc = skimage.morphology.disk(cell_width_pixels/2)
        img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
        img_lap = skimage.filters.laplace(img_gauss, ksize=10)
        img_lap[img_lap < 0] = 0 
        img_lap = img_lap * (1.0 / img_lap.max()) 
        img_hat = img_hat * (1.0 / img_hat.max()) 
        return np.dstack([img_lap, img_hat, img_gauss_01**2])
    
    def just_gauss_hat(self, img):
        cell_width_pixels = 7.5
        img_gauss = skimage.filters.gaussian(img[:,:], 1.1)
        img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
        cell_disc = skimage.morphology.disk(cell_width_pixels/2)
        img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
        return img_hat

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
            return None

        self.current_image = number
        self.current_path = self.filepattern.format(number)
        # This is a kind of hack to load 3 color images as seperate files
        #print("about to read the image")
        #print(self.current_path)
        #if self.current_path.find("{") >= 0:
        #    print("it had a brace")
        #    self.current_path = self.filepattern.format(number, "r")
        img = tifffile.imread(self.current_path.format("r"))
        self.bg_img = self.view_method(img)

    def guess_next_cell_location(self, direction=+1):
        #jet_pattern = self.filepattern + ".mat"
        self.trackdata = auto_match.guess_next_cell_gui(self.trackdata, 
                                                        self.current_cell_id,
                                                        self.current_image, 
                                                        "",
                                                        self.filepattern,
                                                        direction=direction)
        #print("guessed someting ")                                                
        self.move_ui_to_image(self.current_image)

    
    def plot_cell_compiled_trace(self, frame, cell):
        #all_frames = np.arange(0, self.trackdata.metadata["max_frames"])
        #if self.comp_bar is not None: self.comp_bar.remove()
        self.comp_bar = self.ax_cell_compiled_trace.axvspan(frame-0.5, frame+0.5, color="grey", alpha=0.4) 
        
        plots = [("red", "red", ), ("green", "green")] # ("gr", "blue") ]
        #plots = [("g_by_r", "blue") ]
        leaves = self.trackdata.get_final_decendants(cell)
        leaf = leaves[0]
        lineage = self.trackdata.get_cell_lineage(leaf)
        if self.compileddata is None :
            pass
            # if len(self.compiled_plots) < len(plots):
            #     self.compiled_plots = { k, [None]*len(plots) 
        else: 
            for i, (ch, cl) in enumerate(plots):
                lin_frames, lin_data = compiledtracks.get_channel_of_cell(self.compileddata, lineage, ch)  
                print("cell lineage", lineage)
                print("cell frames", lin_frames)
                #print("GOT frames", lin_frames)
                if len(lin_frames) == 0:
                    print("nothing to print here")
                    self.ax_cell_compiled_trace.clear()
                    break
                print("it didnt stop")
                # aframes = lin_frames[~ignore_points]
                # adata = lin_data[~ignore_points]
                lin_smooth = scipy.ndimage.gaussian_filter1d(lin_data, sigma=5, mode="mirror")
                frames, data = compiledtracks.get_channel_of_cell(self.compileddata, cell, ch)
                #ignore_points = (np.isnan(data) | np.isinf(data))
                #sdata = [ s for f, s in zip(lin_frames, lin_smooth) if f in aframes]
                #print(len(frames), len(sdata))
                if (ch not in self.compiled_plots.keys()) or self.compiled_plots[ch] is None:
                    lin_line,  = self.ax_cell_compiled_trace.plot(lin_frames, lin_smooth, color=cl, linestyle=":")
                    line,  = self.ax_cell_compiled_trace.plot(frames, data, color=cl)
                    self.ax_cell_compiled_trace.set_ylim(bottom=0, top=np.nanmax(lin_data))
                    #self.ax_cell_compiled_trace.set_ylim(bottom=0, top=4)
                    self.ax_cell_compiled_trace.set_xlim(left=0, right=self.trackdata.metadata["max_frames"])
                    self.compiled_plots[ch] = line
                    self.compiled_plots[ch + "lin"] = lin_line
                else:
                    self.compiled_plots[ch].set_data(frames, data)
                    self.compiled_plots[ch+"lin"].set_data(lin_frames, lin_data)
                    self.ax_cell_compiled_trace.set_ylim(bottom=0, top=np.nanmax(lin_data))
                    self.ax_cell_compiled_trace.set_xlim(left=0, right=self.trackdata.metadata["max_frames"])


    def plot_cell_path(self, frame, cell):
        if self.trace_bar is not None: self.trace_bar.remove()
        self.trace_bar = self.ax_cell_trace.axvspan(frame-0.5, frame+0.5, color="grey", alpha=0.4) 

        if cell not in self.trackdata.cells.keys():
            #self.ax_cell_trace.clear()
            for p in self.cell_trace_plots: 
                p.remove()
            self.cell_trace_plots = [ None for _ in self.cell_trace_plots ]
            return None
        #all_frames = np.arange(0, self.trackdata.metadata["max_frames"])
        something = np.array(self.trackdata.cells[cell]["state"]) > 0
        frames, = np.where(something)
        states = np.array(self.trackdata.cells[cell]["state"])
        lengths = np.array(self.trackdata.cells[cell]["length"])
        widths = np.array(self.trackdata.cells[cell]["width"])

        plots = [ (frames, lengths[something], "None"), (frames, widths[something], "None") ] 
        
        statesymb = [ (2, "$⚭$"), (3, "$☠$"), (4, "$☉$"), (5, "$🟟$")]

        for state, symb in statesymb:
            loc, = np.where(states==state)
            loc, lengths[loc]
            plots.append((loc, lengths[loc], symb))
        
        if len(self.cell_trace_plots) < len(plots):
            self.cell_trace_plots = [None]*len(plots)
            
        for i, (x, y, m) in enumerate(plots): 
            if self.cell_trace_plots[i] is None:
                line, = self.ax_cell_trace.plot(x, y, markersize=10, marker=m)#, fontname='Symbola', )
                self.cell_trace_plots[i] = line
            else: 
                self.cell_trace_plots[i].set_data(x, y)


        
    def move_to_cell(self, cell):
        number = self.current_image 
        self.current_cell_id = cell
        self.ax_img.set_title(self.make_title())
        if cell not in self.trackdata.cells.keys():
            self.trackdata.cells[cell] = self.trackdata.get_empty_entry()
        if self.trackdata.get_cell_state(number, cell) != 0 :
            ellipse_data = self.trackdata.get_cell_params(number, cell)
            if self.interactive_cell is None:
                self.interactive_cell = cell_editor.CellInteractor(self.ax_img, *ellipse_data, 
                                                                   **self.cell_interactor_style)
            else:
                self.interactive_cell.set_cell_props(*ellipse_data)
        else:
            if self.interactive_cell is not None:
                self.interactive_cell.remove()
                self.interactive_cell = None 
                self.fig.canvas.draw_idle()
        self.plot_cell_compiled_trace(self.current_image, cell)
        # self.ax_cell_compiled_trace.relim()
        # self.ax_cell_compiled_trace.autoscale_view(True,True,True)
        self.plot_cell_path(self.current_image, cell)
        self.show_non_edit_cells(self.current_image)
        self.fig.canvas.draw_idle()
        #     self.ax_cell_id_select.name = "cell_picker"
        #     self.cur_image_art.remove() 

    def update_ui(self):
        self.art_img.set_data(self.bg_img)
        self.art_img.set_clim(vmax=self.bg_img.max()*self.vmaxs)
        self.ax_img.set_title(self.make_title())
        ## update tree
        self.update_tree(recalculate_parents=False)#False)
        self.fig.canvas.draw_idle()
        # for ot in self.text_labels:
        #     print("removing old labels")
        #     ot.remove()
        #     regionp = skimage.measure.regionprops(self.all_cells)
        #     self.text_labels = [self.ax_img.text(r.centroid[1], r.centroid[0], str(r.label)) for r in regionp]
        #     if len(self.cells) == 0:
        #         cellwzero = np.arange(0, 10)# np.insert(self.cells, 0, [0]) 
        #     else:
        #         cellwzero = np.arange(0, self.cells.max() + 10)# np.insert(self.cells, 0, [0]) 
        #     self.art_cell_id_select = self.ax_cell_id_select.scatter(cellwzero, np.ones_like(cellwzero), c=cellwzero, cmap=self.cmrand)

    def update_tree(self, recalculate_parents=False):
        if len(self.trackdata.cells.keys()) <= 1: 
            return None
        if recalculate_parents:
            self.trackdata = track_data.set_possible_parents(self.trackdata)
        self.ax_tree.clear()
        cell_colors  = [(0,0,0,1)] + [ self.cmrand(int(i)) for i in self.cells ]
        cell_finals = { i: self.trackdata.get_final_frame(i) for i in self.cells }
        self.ax_tree, self.node_locs = self.trackdata.plot_tree(self.ax_tree, cell_colors, cell_finals)
        self.ax_tree.set_ylim(self.trackdata.metadata["max_frames"]+5, -2)
        self.ax_tree.tick_params(axis='y',which='minor') 
        self.fig.canvas.draw_idle()

    def select_cell(self, event):
        if event.inaxes.name == "cell_viewer":
            if self.interactive_cell is not None:
                hits_edit, props = self.interactive_cell.ellipse.contains(event)
                if hits_edit:
                    return None
            for patch, cid in self.non_edit_cells:
                hit, props = patch.contains(event)
                if hit:
                    self.move_to_cell(cid)
    
    def select_frame(self, event):
        print(event)
        if (event.inaxes.name == "cell_trace") or (event.inaxes.name == "compiled_trace"):
            select = int(np.round(event.xdata))
            print("Selecting frame", select)
            self.move_ui_to_image(select)

    def make_current_cell_like_previous_frame(self):
        prev_frame = self.current_image - 1
        if self.trackdata.get_cell_state(prev_frame, self.current_cell_id) != 0 :
            self.trackdata.copy_cell_info_from_frame(self.current_cell_id, prev_frame, self.current_image)
            ellipse_data = self.trackdata.get_cell_params(self.current_image, self.current_cell_id)
            if self.interactive_cell is None:
                self.interactive_cell = cell_editor.CellInteractor(self.ax_img, *ellipse_data, **self.cell_interactor_style)
            self.interactive_cell.set_cell_props(*ellipse_data)
        else:
            print("Cell ", self.current_cell_id, " is not present in frame", self.current_image)
        self.fig.canvas.draw_idle()


    def update_track_data(self):
        """ this updates the track data with currently edited cell"""
        if self.interactive_cell is not None:
            print("updating the data structure")
            print(self.trackdata.get_cell_params(self.current_image, self.current_cell_id))
            properties = self.interactive_cell.get_position_props()
            print(properties)
            self.trackdata.set_cell_properties(self.current_image, self.current_cell_id, properties)
            print(self.trackdata.get_cell_params(self.current_image, self.current_cell_id))


    def save_segmentation(self):
        self.update_track_data()
        self.trackdata.save(self.trackdata_path)

    def add_new_cell_to_frame(self, cell_id:str):
        print("Adding cell {0}".format(cell_id))
        self.trackdata.create_cell_if_new(cell_id)
        self.current_cell_id = cell_id
        self.cells = [ c for c in self.trackdata.get_cells_list()]
        # TODO update the cell selector
        if self.trackdata.get_cell_state(self.current_image, cell_id) != 0:
            print("cell already exists in this frame")
            return None
        else: 
            # Try to put the cell in the middle of the screen.
            x0, x1 = self.ax_img.get_xlim()
            y0, y1 = self.ax_img.get_ylim()
            xpos = x0 + (x1 - x0)/2
            ypos = y1 + (y0 - y1)/2
            temp_properties = {"row": ypos, "col":xpos, "length": 22, "width": 6, "angle": 0, "state":1}
            self.trackdata.set_cell_properties(self.current_image, cell_id, temp_properties)
            self.move_to_cell(cell_id)
        self.update_track_data()
        self.fig.canvas.draw_idle()

    def set_cell_state(self, state):
        self.trackdata.set_cell_state(self.current_image, self.current_cell_id, int(state))

    def track_cell(self):
        print("tracking")
        print("initial frame{0}".format(self.current_image), self.trackdata.get_cell_properties(self.current_image, self.current_cell_id)) 
        print("next frame{0}".format(self.current_image+1), self.trackdata.get_cell_properties(self.current_image+1, self.current_cell_id)) 
        ntd = cell_tracker.gui_interpolate(self.trackdata, self.current_cell_id, self.current_image)
        self.trackdata = ntd
        print("tracked")
        print("after frame{0}".format(self.current_image), self.trackdata.get_cell_properties(self.current_image, self.current_cell_id))
        print("next frame{0}".format(self.current_image+1), self.trackdata.get_cell_properties(self.current_image+1, self.current_cell_id))
        self.move_ui_to_image(self.current_image)
        #self.move_ui_frame(self.current_image)
    
    def delete_cell_in_frame(self, cell, frame):
        self.trackdata.blank_cell_params(frame, cell)
        self.move_ui_to_image(frame)


    def on_key_press(self, event):
        #print("type", event.key)
        if event.key == "t":
            self.track_cell()            
        elif event.key == "z":# used to be a
            self.add_new_cell_to_frame(self.current_cell_id)
        # elif event.key == "t":
        #     self.update_tree(True)
        elif event.key == "A":
            print("add cell number:")
            self.read_numbers = self.add_new_cell_to_frame
            self.read_in = ""
        elif (self.read_numbers is not None):
            if event.key in "1234567890":
                self.read_in += event.key
            elif event.key == "enter":
                print("Got number: {0}".format(self.read_in))
                self.read_numbers(self.read_in)
                self.read_numbers = None
                self.read_in = ""
            elif event.key == "esc":
                self.read_numbers = None
                self.read_in = ""
                print("not adding number any more.")
        elif event.key == "c":
            self.make_current_cell_like_previous_frame()
        elif event.key == "X":
            self.delete_cell_in_frame(self.current_cell_id, self.current_image)
        elif event.key == "S":
            print("set cell_state:", self.trackdata.metadata["states"]) 
            self.read_numbers = self.set_cell_state
            self.read_in = ""
            if event.key == "esc":
                self.read_numbers = None
                self.read_in = ""
                print("not going to change state")
        elif event.key == "i":
            self.art_img.set_visible(not self.art_img.get_visible())
            self.fig.canvas.draw_idle()
        elif event.key == 'pagedown' or event.key == "d":
            self.move_ui_to_image(self.current_image + 1)
        elif event.key == 'pageup' or event.key == "a":
            self.move_ui_to_image(self.current_image - 1)
        elif event.key.lower() == 'w':
            print("Saving frame {0}".format(self.current_image))
            self.save_segmentation()
        elif event.key == "g":
            self.guess_next_cell_location(direction=+1)
        elif event.key == "f":
            self.guess_next_cell_location(direction=-1)
        else:
            print("Pressing {0} does nothing yet".format(event.key))



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--images', type=str, required=True)
    parser.add_argument('--trackdata', type=str, required=True)
    parser.add_argument('--compileddata', type=str, required=False)
    parser.add_argument('-c', '--start_cell', type=str, default="1")
    parser.add_argument('-s', '--start_image', type=int, default=1)
    parser.add_argument("--view", type=str, default="straight")
    parser.add_argument("--vmax", type=float, default=1.0 )
    #parser.add_argument('-s', '--segfile', type=str)
    pa = parser.parse_args()

    state = State(pa.images, pa.trackdata, pa.compileddata, pa.start_image, pa.start_cell, pa.view, pa.vmax) #, pa.segfile)

    state.fig.canvas.mpl_connect('key_press_event', state.on_key_press)
    plt.show()
