import numpy as np
#import skimage.io
# import skimage.draw
# import os.path
#import matplotlib
import tifffile
#import matplotlib.pyplot as plt
# import scipy.ndimage as nd
# from scipy import ndarray
        




# def save_tiff(filename, im, **args):
#     tifffile.imsave(filename, im, **args)

#from .running_mean import update_meanstd

def read_lsm_channel(channel, path):
    with tifffile.TiffFile(path) as tf:

        channel = channel.lower()
        if (channel in [ "red", "green", "blue"]):
            chan = channel[0]
        elif channel in ["r", "g", "b"]:
            chan = channel
        else:
            raise Exception("This function doenst know about {0}".format(channel))

        if not tf.is_lsm:
            rgbmap = {"r":0, "g":1, "b":2}
            return tf.asarray()[:,:,rgbmap[chan]]

        # width = (tf.pages[0]).image_width
        # height = (tf.pages[0]).image_length

        track_data = tf.asarray()
        for track_num, trackinfo in enumerate(tf.pages[0].cz_lsm_scan_info["tracks"]):
            wavelength = trackinfo['illumination_channels'][0]["wavelength"]
            if (wavelength >= 399) and (wavelength < 487) and (chan == "b"):
                return track_data[0,0,track_num, :, :] 
            elif (wavelength >= 450) and (wavelength < 548) and (chan == "g"):
                return track_data[0,0,track_num, :, :] 
            elif (wavelength >= 548) and (wavelength < 590) and (chan == "r"):
                return track_data[0,0,track_num, :, :] 

        raise Exception("Image did not have a channel with illumination matching \"{0}\"".format(channel))

def read_lsm(path):
    with tifffile.TiffFile(path) as tf:
        if not tf.is_lsm:
            return tf.asarray()

        RED, GREEN, BLUE = 0, 1, 2 
        if len(tf.pages) > 3:
            raise Exception("This image has {0} colour channels but this is only set up for up to 3 channels".format(len(tf.pages)))

        track_data = tf.asarray()
        width = (tf.pages[0]).image_width
        height = (tf.pages[0]).image_length
        result = np.zeros((height, width, 3), track_data.dtype)
        

        for track_num, trackinfo in enumerate(tf.pages[0].cz_lsm_scan_info["tracks"]):
            wavelength = trackinfo['illumination_channels'][0]["wavelength"]
            if (wavelength >= 399) and (wavelength < 488) :
                color = BLUE
            elif (wavelength >= 450) and (wavelength < 548):
                color = GREEN
            elif (wavelength >= 548) and (wavelength < 590) :
                color = RED
            print(track_data.shape)
            result[:, :, color] = track_data[0,0,track_num, :, :] 
        return result

def get_labeled_path(path, label):
    pathish = path.split(".")
    ext = pathish[-1]
    body =  pathish[:-1] 
    return ".".join(body) + "_" + label + "." + ext
    
#def read_czi(path):
    #import czifile
    #xmlstr = ElementTree.tostring(et, encoding='utf8', method='xml')
    #with czifile.CziFile(path) as tf:
#        #if not tf.is_lsm:
#        #    return tf.asarray()
#        m = tf.metadata
#        for i in m.iter():
#            print(i)
#            <Element 'Metadata' at 0x7f0d4a28a868>
#<Element 'Version' at 0x7f0d4a28a9a8>
#<Element 'Information' at 0x7f0d4a28ac28>
#<Element 'User' at 0x7f0d4a28a728>
#<Element 'DisplayName' at 0x7f0d4a28a6d8>
#<Element 'Document' at 0x7f0d4a28a598>
#<Element 'Name' at 0x7f0d4a28a9f8>
#<Element 'Description' at 0x7f0d4a28af98>
#<Element 'Comment' at 0x7f0d4a28a688>
#<Element 'UserName' at 0x7f0d4a28a548>
#<Element 'CreationDate' at
#
#
#        RED, GREEN, BLUE = 0, 1, 2 
#        if len(tf.pages) > 3:
#            raise Exception("This image has {0} colour channels but this is only set up for up to 3 channels".format(len(tf.pages)))
#
#        track_data = tf.asarray()
#        width = (tf.pages[0]).image_width
#        height = (tf.pages[0]).image_length
#        result = np.zeros((height, width, 3), track_data.dtype)
#
#        for track_num, trackinfo in enumerate(tf.pages[0].cz_lsm_scan_info["tracks"]):
#            wavelength = trackinfo['illumination_channels'][0]["wavelength"]
#            if (wavelength >= 399) and (wavelength < 488) :
#                color = BLUE
#            elif (wavelength >= 450) and (wavelength < 548):
#                color = GREEN
#            elif (wavelength >= 548) and (wavelength < 590) :
#                color = RED
#            print(track_data.shape)
#            result[:, :, color] = track_data[0,0,track_num, :, :] 
#        return result

# def get_cached_mask(mask_method, filename, storedn = "masked"):
#     import tifffile
#     dirn, fn = os.path.dirname(filename), os.path.basename(filename)
#     savename = os.path.join(dirn, storedn, fn)
#     print(savename)
#     if os.path.exists(savename):
#         tf = tifffile.imread(savename)
#         return tf.astype(bool)
#     else:
#         im = read_lsm(filename)
#         imr, img = im[:, :, 0], im[:, :, 1]
#         mask = mask_method(imr)
#         if not os.path.exists(os.path.join(dirn, storedn)):
#             os.mkdir(os.path.join(dirn, storedn))
#         save_tiff(savename, mask.astype("uint8"), compress=7)
#         return mask


# def get_cached_segmentation(segmentation_method, filename, dirname="segmented"):
#     import tifffile
#     dirn, fn = os.path.dirname(filename), os.path.basename(filename)
#     savename = os.path.join(dirn, dirname, fn)
#     if os.path.exists(savename):
#         tf = tifffile.imread(savename)
#         return tf.astype("uint16")
#     else:
#         im = read_lsm(filename)
#         imr, img = im[:, :, 0], im[:, :, 1]
#         wseg = segmentation_method(imr)
#         mx = ndarray.max(wseg)
#         if mx >= (2**16)-20:
#             print("too many_", mx)
#         if not os.path.exists(os.path.join(dirn, dirname)):
#             os.mkdir(os.path.join(dirn, dirname))
#         save_tiff(savename, wseg, compress=7)
#         return wseg


class StringIntMap:
    def __init__(self):
        self.string_to_index = {}
        self.index_to_string = {}

    @staticmethod
    def load_map_csv(path, number_name="index", string_name="string"):
        x = StringIntMap()
        with open(path, 'r') as filedb:
            lines = filedb.read().splitlines()
            titles = lines[0].split('\t')
            print(titles)
            i_index = titles.index(number_name)
            i_string = titles.index(string_name)
            print(i_index, i_string)
            for line in lines[1:]:
                lnsplt = line.strip().split('\t')
                i, st = lnsplt[i_index], lnsplt[i_string]
                print(i, st)
                x.string_to_index[st] = int(i)
                x.index_to_string[int(i)] = st
        return x


# def remove_large_objects(ar, max_size=64, connectivity=1, in_place=False):
#     """Remove connected components smaller than the specified size.

#     Parameters
#     ----------
#     ar : ndarray (arbitrary shape, int or bool type)
#         The array containing the connected components of interest. If the array
#         type is int, it is assumed that it contains already-labeled objects.
#         The ints must be non-negative.
#     min_size : int, optional (default: 64)
#         The smallest allowable connected component size.
#     connectivity : int, {1, 2, ..., ar.ndim}, optional (default: 1)
#         The connectivity defining the neighborhood of a pixel.
#     in_place : bool, optional (default: False)
#         If `True`, remove the connected components in the input array itself.
#         Otherwise, make a copy.

#     Raises
#     ------
#     TypeError
#         If the input array is of an invalid type, such as float or string.
#     ValueError
#         If the input array contains negative values.

#     Returns
#     -------
#     out : ndarray, same shape and type as input `ar`
#         The input array with small connected components removed.

#     Examples
#     --------
#     >>> from skimage import morphology
#     >>> a = np.array([[0, 0, 0, 1, 0],
#     ...               [1, 1, 1, 0, 0],
#     ...               [1, 1, 1, 0, 1]], bool)
#     >>> b = morphology.remove_small_objects(a, 6)
#     >>> b
#     array([[False, False, False, False, False],
#            [ True,  True,  True, False, False],
#            [ True,  True,  True, False, False]], dtype=bool)
#     >>> c = morphology.remove_small_objects(a, 7, connectivity=2)
#     >>> c
#     array([[False, False, False,  True, False],
#            [ True,  True,  True, False, False],
#            [ True,  True,  True, False, False]], dtype=bool)
#     >>> d = morphology.remove_small_objects(a, 6, in_place=True)
#     >>> d is a
#     True
#     """
#     # Should use `issubdtype` for bool below, but there's a bug in numpy 1.7
#     if not (ar.dtype == bool or np.issubdtype(ar.dtype, np.integer)):
#         raise TypeError("Only bool or integer image types are supported. "
#                         "Got %s." % ar.dtype)

#     if in_place:
#         out = ar
#     else:
#         out = ar.copy()

#     if max_size == 0:  # shortcut for efficiency
#         return out

#     if out.dtype == bool:
#         selem = nd.generate_binary_structure(ar.ndim, connectivity)
#         ccs = np.zeros_like(ar, dtype=np.int32)
#         nd.label(ar, selem, output=ccs)
#     else:
#         ccs = out

#     try:
#         component_sizes = np.bincount(ccs.ravel())
#     except ValueError:
#         raise ValueError("Negative value labels are not supported. Try "
#                          "relabeling the input with `scipy.ndimage.label` or "
#                          "`skimage.morphology.label`.")

#     too_small = component_sizes > max_size
#     too_small_mask = too_small[ccs]
#     out[too_small_mask] = 0

#     return out



# #import matplotlib
# #import matplotlib.pyplot as plt
# #from mpl_toolkits.axes_grid1 import AxesGrid

# def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
#     '''
#     Function to offset the "center" of a colormap. Useful for
#     data with a negative min and positive max and you want the
#     middle of the colormap's dynamic range to be at zero

#     Input
#     -----
#       cmap : The matplotlib colormap to be altered
#       start : Offset from lowest point in the colormap's range.
#           Defaults to 0.0 (no lower ofset). Should be between
#           0.0 and `midpoint`.
#       midpoint : The new center of the colormap. Defaults to 
#           0.5 (no shift). Should be between 0.0 and 1.0. In
#           general, this should be  1 - vmax/(vmax + abs(vmin))
#           For example if your data range from -15.0 to +5.0 and
#           you want the center of the colormap at 0.0, `midpoint`
#           should be set to  1 - 5/(5 + 15)) or 0.75
#       stop : Offset from highets point in the colormap's range.
#           Defaults to 1.0 (no upper ofset). Should be between
#           `midpoint` and 1.0.
#     '''
#     cdict = {
#         'red': [],
#         'green': [],
#         'blue': [],
#         'alpha': []
#     }

#     # regular index to compute the colors
#     reg_index = np.linspace(start, stop, 257)

#     # shifted index to match the data
#     shift_index = np.hstack([
#         np.linspace(0.0, midpoint, 128, endpoint=False), 
#         np.linspace(midpoint, 1.0, 129, endpoint=True)
#     ])

#     for ri, si in zip(reg_index, shift_index):
#         r, g, b, a = cmap(ri)

#         cdict['red'].append((si, r, r))
#         cdict['green'].append((si, g, g))
#         cdict['blue'].append((si, b, b))
#         cdict['alpha'].append((si, a, a))

#     newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
#     plt.register_cmap(cmap=newcmap)

#     return newcmap


# """
#     This exists because in the LSM images the colors are flipped.
#     This is intended to just keep things clear
# """
# def get_siga_sigb(image):
#     return image[:, :, 0], image[:, :, 1]


# def no_dir_or_ext(name):
#     return os.path.splitext(os.path.basename(name))[0]


# def process_filename(name):
#     stripname = os.path.splitext(os.path.basename(name))[0]
#     return stripname.split("_")


# def getcirc(r):
#     circ = np.zeros((r*2+1,r*2+1))
#     circ[skimage.draw.circle(r+1,r+1,r)] = 1
#     return circ


def intersect(X, Y):
    return filter(lambda x: x in Y, X)


def find_largest_label(labeled_image):
    maxc, maxl = 0, 1
    n = max(np.unique(labeled_image))
    for i in range(1,n+1):
        x = np.count_nonzero(labeled_image==i)
        if maxc < x :
            maxc = x
            maxl = i
    return maxl

