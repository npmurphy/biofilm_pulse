"""
This is an example to show how to build cross-GUI applications using
matplotlib event handling to interact with objects on the canvas

"""
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.patches import Ellipse
from matplotlib.mlab import dist_point_to_segment

try:
    from .cell_dimensions import get_lines_from_ellipse
    from .cell_dimensions import get_ellipse_props_from_lines
    from .cell_dimensions import mplellipse_to_props
    from .cell_dimensions import props_to_mplellipse
    from .cell_dimensions import set_mplellipse_props 
    from .cell_dimensions import get_nearest_point_on_min_axis
    from .cell_dimensions import rotate_lines_using_maj_line
except SystemError as e:
    from cell_dimensions import get_lines_from_ellipse
    from cell_dimensions import get_ellipse_props_from_lines
    from cell_dimensions import mplellipse_to_props
    from cell_dimensions import props_to_mplellipse
    from cell_dimensions import set_mplellipse_props 
    from cell_dimensions import get_nearest_point_on_min_axis
    from cell_dimensions import rotate_lines_using_maj_line

def get_cell(xy, length, width, angle, **kargs):
    return Ellipse(**props_to_mplellipse(xy, length, width, angle), **kargs)

class CellInteractor(object):
    """
    An ellipse editor.

    Key-bindings

    """

    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, ax, pos, length, width, ang, **kwargs):

        # if ellipse.figure is None:
        #     raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ellipse = Ellipse(**props_to_mplellipse(pos, length, width, ang), **kwargs)
        self.ax = ax
        self.canvas = self.ax.figure.canvas
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.add_patch(self.ellipse)
        #self.canvas = self.ellipse.figure.canvas

        xy_maj, xy_min = get_lines_from_ellipse(*mplellipse_to_props(self.ellipse))
        self.line_maj = Line2D(*xy_maj, marker='o', markerfacecolor='r', animated=True)
        self.line_min = Line2D(*xy_min, marker='o', markerfacecolor='y', animated=True)
        self.ax.add_line(self.line_maj)
        self.ax.add_line(self.line_min)

        #cid = self.ellipse.add_callback(self.poly_changed)
        self._ind = None  # the active vert

        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)

    def draw_callback(self, event):
        print("draw call")
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.ellipse)
        self.ax.draw_artist(self.line_maj)
        self.ax.draw_artist(self.line_min)
        self.canvas.blit(self.ax.bbox)


    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        xy_maj = self.line_maj.get_xydata()
        xy_min = self.line_min.get_xydata()
        xys = np.vstack([xy_maj, xy_min[1,:]])
        # row 0 is the center, row 1 is the maj axis, row 2 is the minor

        xyt = self.line_maj.get_transform().transform(xys)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        # row 0 is the center, row 1 is the maj axis, row 2 is the minor
        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if event.button != 1:
            return
        self._ind = None
        self.canvas.draw()

    def remove(self):
        self.ellipse.remove()
        print("should be removing the axis")
        self.line_maj.remove()
        self.line_min.remove()
        self.canvas.draw()

    def get_position_props(self):
        props = {}
        (col, row), length, width, angle = mplellipse_to_props(self.ellipse)
        props["row"] = row
        props["col"] = col
        props["width"] = width
        props["length"] = length
        props["angle"] = angle 
        return props

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes:
            return
        # if event.key == 't':
        #     self.showverts = not self.showverts
        #     self.line.set_visible(self.showverts)
        #     if not self.showverts:
        #         self._ind = None
        # elif event.key == 'd':
        #     ind = self.get_ind_under_point(event)
        #     if ind is not None:
        #         self.poly.xy = [tup for i, tup in enumerate(self.poly.xy) if i != ind]
        #         self.line.set_data(zip(*self.poly.xy))
        # elif event.key == 'i':
        #     xys = self.poly.get_transform().transform(self.poly.xy)
        #     p = event.x, event.y  # display coords
        #     for i in range(len(xys) - 1):
        #         s0 = xys[i]
        #         s1 = xys[i + 1]
        #         d = dist_point_to_segment(p, s0, s1)
        #         if d <= self.epsilon:
        #             self.poly.xy = np.array(
        #                 list(self.poly.xy[:i]) +
        #                 [(event.xdata, event.ydata)] +
        #                 list(self.poly.xy[i:]))
        #             self.line.set_data(zip(*self.poly.xy))
        #             break

        self.canvas.draw()

    def set_cell_props(self, center, length, width, angle):
        new_ellipse_props = center, length, width, angle
        self.ellipse = set_mplellipse_props(self.ellipse, *new_ellipse_props)
        maj_line, min_line = get_lines_from_ellipse(*new_ellipse_props)
        self.ellipse = set_mplellipse_props(self.ellipse, *new_ellipse_props)
        self.line_maj.set_xdata(maj_line[0])
        self.line_maj.set_ydata(maj_line[1])
        self.line_min.set_xdata(min_line[0])
        self.line_min.set_ydata(min_line[1])


    def motion_notify_callback(self, event):
        'on mouse movement'
        # if not self.showverts:
        #     return
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        
        #print(mplellipse_to_props(self.ellipse))
        maj_line, min_line = get_lines_from_ellipse(*mplellipse_to_props(self.ellipse))
        x0, y0 = self.ellipse.center
        if self._ind == 0: # center
            dx = event.xdata - x0
            dy = event.ydata - y0
            new_maj = ((event.xdata, maj_line[0][1] + dx), (event.ydata, maj_line[1][1] + dy))
            new_min = ((event.xdata, min_line[0][1] + dx), (event.ydata, min_line[1][1] + dy))
            new_ellipse_props = get_ellipse_props_from_lines(new_maj, new_min)
            self.ellipse = set_mplellipse_props(self.ellipse, *new_ellipse_props)
            self.line_maj.set_xdata(new_maj[0])
            self.line_maj.set_ydata(new_maj[1])
            self.line_min.set_xdata(new_min[0])
            self.line_min.set_ydata(new_min[1])
        elif self._ind == 1: # Major line 
            new_maj = ((x0, event.xdata), (y0, event.ydata ))
            _, new_min = rotate_lines_using_maj_line(maj_line, min_line, new_maj)
            new_ellipse_props = get_ellipse_props_from_lines(new_maj, new_min)
            #print("mod:", new_ellipse_props)
            self.ellipse = set_mplellipse_props(self.ellipse, *new_ellipse_props)
            emaj_line, emin_line = get_lines_from_ellipse(*mplellipse_to_props(self.ellipse))
            self.line_maj.set_xdata(new_maj[0])
            self.line_maj.set_ydata(new_maj[1])
            self.line_min.set_xdata(new_min[0])
            self.line_min.set_ydata(new_min[1])
        elif self._ind == 2: #minor line
            pellipse = mplellipse_to_props(self.ellipse)
            xi, yi = get_nearest_point_on_min_axis(pellipse, (event.xdata, event.ydata))
            new_min = ((x0, xi), (y0, yi))
            new_ellipse_props = get_ellipse_props_from_lines(maj_line, new_min)
            self.ellipse = set_mplellipse_props(self.ellipse, *new_ellipse_props)
            self.line_min.set_xdata(new_min[0])
            self.line_min.set_ydata(new_min[1])

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.ellipse)
        self.ax.draw_artist(self.line_maj)
        self.ax.draw_artist(self.line_min)
        self.canvas.blit(self.ax.bbox)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    pos = (2,3)
    ang = np.pi/2
    length = 5
    width = 2

    fig, ax = plt.subplots()
    ax.set_aspect('equal', 'datalim')

    p = CellInteractor(ax, pos, length, width, ang, alpha=0.3)

    ax.set_title('Click and drag a point to move it')
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 6)

    plt.show()
