"""
docstring
"""
import argparse
import re
from glob import glob

import matplotlib
import matplotlib.axes
import matplotlib.collections
import matplotlib.pyplot as plt
import numpy as np
import skimage.draw
import skimage.exposure
import skimage.io
import skimage.morphology
import skimage.segmentation
import tifffile

from lib.cell_tracking import cell_editor
from lib.cell_tracking.track_db import TrackDB
from lib.util.tiff import get_shape


# matplotlib.use('TKAgg')
# matplotlib.use('GTKAgg')
matplotlib.use("Qt5Agg")

# show three images with current in the middle.
# load the three images
# show overlaps of the images in red green.
# draw the cell, editable.
# draw the other cells as matshow


class State:
    def __init__(
        self,
        filepattern,
        track_path,
        image_start=1,
        cell_start: int = 1,
        viewmethod="gauss",  # straight",
        vmax=1.0,
        image_range=(None, None),
    ):
        self.filepattern = filepattern
        self.parse_re = re.compile(re.sub(r"{\d?:\d+d}", r"(\d+)", self.filepattern))
        self.image_range = self._get_image_range(image_range)

        self.red_chan = "ch00"
        self.green_chan = "ch01"
        self.blue_chan = "ch02"

        self.color_mode = "trackstatus"

        self.cell_interactor_style = {
            "edgecolor": "white",
            "facecolor": "none",
            "linewidth": 1,
        }

        self.trackdata = TrackDB(track_path)  # , max(self.image_range))

        print(self.filepattern.format(self.image_range[0]))
        init_shape = get_shape(self.filepattern.format(self.image_range[0]))
        self.vmaxs = vmax
        self.cells = self.trackdata.get_cell_list()
        self.current_cell_id = int(cell_start)
        self.current_image = image_start
        self.view_methods = {"gauss": (2, lambda x: skimage.filters.gaussian(x, 1.1))}
        dim, self.view_method = self.view_methods[viewmethod]
        if dim == 3:
            self.img_size = init_shape + (dim,)
        else:
            self.img_size = init_shape

        #######################
        ## Setting up GUI
        #######################
        self.fig = plt.figure()
        self.cmrand = matplotlib.colors.ListedColormap(np.random.rand(10000, 3))
        # self.rand_colors = np.random.rand(1000, 3)

        plt.rcParams["keymap.save"] = ["ctrl+s"]  # free up s
        plt.rcParams["keymap.fullscreen"] = ["ctrl+f"]  # free up f
        plt.rcParams["keymap.home"] = [""]  # free up a and r
        plt.rcParams["keymap.back"] = ["backspace"]
        plt.rcParams["keymap.grid"] = [""]  # g

        self.number_of_steps = 2

        self.ax_images = [
            self.fig.add_axes(
                [(i / self.number_of_steps), 0.5, (1 / self.number_of_steps), 0.45]
            )
            for i in range(self.number_of_steps)
        ]
        shift = (1 / self.number_of_steps) * 0.5
        self.ax_overlaps = [
            self.fig.add_axes(
                [shift + (i / self.number_of_steps), 0.0, 1 / self.number_of_steps, 0.5]
            )
            for i in range(self.number_of_steps - 1)
        ]

        # self.ax_img.set_title(self.make_title())
        self.bg_images = [np.zeros(init_shape, dtype=np.uint16)] * self.number_of_steps
        self.overlap_images = [np.zeros((*init_shape, 3), dtype=np.uint16)] * (
            self.number_of_steps - 1
        )

        # imgcmap = "bone"
        # imgcmap = "viridis"
        imgcmap = "hot"

        self.art_images = [
            ax.imshow(
                bg,
                cmap=plt.get_cmap(imgcmap),
                vmin=0,
                vmax=0.3,
                interpolation="nearest",
            )
            for ax, bg in zip(self.ax_images, self.bg_images)
        ]

        self.art_overlaps = [
            ax.imshow(
                bg,
                cmap=plt.get_cmap(imgcmap),
                vmin=0,
                vmax=0.3,
                interpolation="nearest",
            )
            for ax, bg in zip(self.ax_overlaps, self.overlap_images)
        ]

        x_axis = self.ax_images[0].get_shared_x_axes()
        y_axis = self.ax_images[0].get_shared_y_axes()
        [x_axis.join(self.ax_images[0], a) for a in self.ax_images[1:]]
        [y_axis.join(self.ax_images[0], a) for a in self.ax_images[1:]]
        [x_axis.join(self.ax_images[0], a) for a in self.ax_overlaps]
        [y_axis.join(self.ax_images[0], a) for a in self.ax_overlaps]

        self.main_bg_ellipses = [None] * self.number_of_steps
        self.main_ov_ellipses = [None] * (self.number_of_steps - 1)
        self.ui_selectors = []

        self.move_ui_to_image(self.current_image)

    def _get_image_range(self, image_range):
        if image_range == (None, None):
            tmppattern_st = self.filepattern.split("{")[0]
            tmppattern_ed = self.filepattern.split("}")[1]

            def parse_number(filepath):
                parsed = self.parse_re.match(filepath).groups()
                return int(parsed[0])

            return sorted(
                [parse_number(f) for f in glob(tmppattern_st + "*" + tmppattern_ed)]
            )
        return list(image_range[0], image_range[1])

    def move_ui_to_image(self, imagen):
        self.move_to_image(imagen)
        self.move_to_cell_all_axes(self.current_cell_id)

        self.update_ui()

    def make_title(self, status):
        vals = (self.current_image, status, self.current_cell_id, len(self.cells))
        return "Image:{0} Cell#{2} **{1}**".format(*vals)

    def move_to_image(self, number):
        if number not in self.image_range:
            print(
                "{0} is not in the list of images {1}".format(number, self.image_range)
            )
            return None

        self.current_image = number
        self.bg_images = [
            self.view_method(
                tifffile.imread(self.filepattern.format(number).format("r"))
            )
            for number in range(
                self.current_image, self.current_image + self.number_of_steps
            )
        ]

        for i in range(len(self.bg_images)):
            self.art_images[i].set_data(self.bg_images[i])
            self.art_images[i].set_clim(vmax=self.bg_images[i].max() * self.vmaxs)
            # self.ax_images[i].set_title(self.make_title())
        self.fig.canvas.draw_idle()
        return True

    def go_to_next_unapproved(self):
        index = self.cells.index(self.current_cell_id)
        for i in range(index + 1, len(self.cells)):
            next_cell = self.cells[i]
            print("checking cell", next_cell)
            try:
                cell_status = self.trackdata.get_cell_properties(
                    self.current_image + 1, next_cell
                )["trackstatus"]
            except:
                print("It doesnt exist in the next frame", next_cell)
                continue
            if cell_status == "auto":
                print("Its, good, lets look at ", next_cell)
                self.move_to_cell_all_axes(next_cell)
                break
            else:
                print("Its got no status or is null skipping", next_cell)
                continue
        print("No cells left")

    def move_to_cell_all_axes(self, cell):
        frame = self.current_image
        self.current_cell_id = cell

        def get_cell(f, c):
            try:
                return self.trackdata.get_cell_properties(f, c)
            except:
                return None

        current_cells = [get_cell(frame + i, cell) for i in range(self.number_of_steps)]

        for i, ax in enumerate(self.ax_images):
            try:
                self.main_bg_ellipses[i].remove()
            except AttributeError:
                pass
            cp = current_cells[i]
            if cp is not None:
                ax.set_title(self.make_title(cp["trackstatus"]))
                ellipse_data = self.trackdata.cell_properties_to_params(cp)
                self.main_bg_ellipses[i] = cell_editor.CellInteractor(
                    ax, *ellipse_data, **self.cell_interactor_style
                )

        def make_overlap_images(im1, im2, cel1, cel2):
            dy = cel1["row"] - cel2["row"]
            dx = cel1["col"] - cel2["col"]
            rol1 = np.roll(im2, int(dy), axis=0)
            rol2 = np.roll(rol1, int(dx), axis=1)
            joined = np.dstack([im1, rol2, np.zeros_like(im1)])
            max_v = np.max(joined)
            imb = skimage.exposure.rescale_intensity(
                joined, in_range=(0, max_v), out_range=(0, 255)
            ).astype(np.uint8)
            return imb

        current_cells_pairs = zip(current_cells[:-1], current_cells[1:])
        current_image_pairs = zip(self.bg_images[0:-1], self.bg_images[1:])
        self.overlap_images = [
            make_overlap_images(*images, *cells)
            for (images, cells) in zip(current_image_pairs, current_cells_pairs)
        ]
        for i in range(len(self.overlap_images)):
            self.art_overlaps[i].set_data(self.overlap_images[i])

        z_width = 50
        for a in self.ax_images + self.ax_overlaps:
            a.set_xlim(
                current_cells[0]["col"] - z_width, current_cells[0]["col"] + z_width
            )
            a.set_ylim(
                current_cells[0]["row"] + z_width, current_cells[0]["row"] - z_width
            )

        self.fig.canvas.draw_idle()

    def update_ui(self):

        self.fig.canvas.draw_idle()

    def save_segmentation(self):
        self.trackdata.save()

    # def set_cell_state(self, cell_state):
    #     state_name = self.trackdata.metadata.states[cell_state]
    #     self.trackdata.set_cell_state(
    #         self.current_image, self.current_cell_id, state_name
    #     )

    def set_track_status(self, cell_id, frame, judgement):
        print(judgement, cell_id, frame)
        self.trackdata.set_cell_properties(
            frame, cell_id, {"trackstatus": judgement}
        )
        self.save_segmentation()

    def on_key_press(self, event):
        event_dict = {
            "t": lambda: self.set_track_status(
                self.current_cell_id, self.current_image + 1, "approved"
            ),
            "x": lambda: self.set_track_status(
                self.current_cell_id, self.current_image + 1, "disapprove"
            ),
            "w": self.save_segmentation,
            "pagedown": lambda: self.move_ui_to_image(self.current_image + 1),
            "d": lambda: self.move_ui_to_image(self.current_image + 1),
            "pageup": lambda: self.move_ui_to_image(self.current_image - 1),
            "a": lambda: self.move_ui_to_image(self.current_image - 1),
            "right": self.go_to_next_unapproved,
        }
        # print("type", event.key)
        try:
            action = event_dict[event.key]
            action()
        except KeyError:
            print("Pressing {0} does nothing yet".format(event.key))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=str, required=True)
    parser.add_argument("--trackdata", type=str, required=True)
    parser.add_argument("-c", "--start_cell", type=str, default="1")
    parser.add_argument("-s", "--start_image", type=int, default=1)
    parser.add_argument("--view", type=str, default="gauss")
    parser.add_argument("--vmax", type=float, default=1.0)
    pa = parser.parse_args()

    state = State(
        pa.images, pa.trackdata, pa.start_image, pa.start_cell, pa.view, pa.vmax
    )

    state.fig.canvas.mpl_connect("key_press_event", state.on_key_press)
    plt.show()
