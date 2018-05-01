import numpy as np
import matplotlib

# Random colour map
cmrand = matplotlib.colors.ListedColormap(np.random.rand(2**10, 3))

_hot_green = {'green':   ((0., 0.0416, 0.0416),
                       (0.365079, 1.000000, 1.000000),
                       (1.0, 1.0, 1.0)),
             'red': ((0., 0., 0.),
                       (0.365079, 0.000000, 0.000000),
                       (0.746032, 1.000000, 1.000000),
                       (1.0, 1.0, 1.0)),
             'blue':  ((0., 0., 0.),
                       (0.746032, 0.000000, 0.000000),
                       (1.0, 1.0, 1.0))}

_hot_blue = {'blue':   ((0., 0.0416, 0.0416),
                       (0.365079, 1.000000, 1.000000),
                       (1.0, 1.0, 1.0)),
             'red': ((0., 0., 0.),
                       (0.365079, 0.000000, 0.000000),
                       (0.746032, 1.000000, 1.000000),
                       (1.0, 1.0, 1.0)),
             'green':  ((0., 0., 0.),
                       (0.746032, 0.000000, 0.000000),
                       (1.0, 1.0, 1.0))}
# like hot, but with green instead of red
hotg = matplotlib.colors.LinearSegmentedColormap ("hotg", _hot_green )
hotb = matplotlib.colors.LinearSegmentedColormap ("hotb", _hot_blue )
