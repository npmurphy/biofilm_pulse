
import tifffile


def get_shape(path):
    with tifffile.TiffFile(path) as tf:
        # try :
        #     res =  tf.series[0].shape
        #     return res[0], res[1]
        # except AttributeError: 
        rows = tf.pages[0].imagelength
        cols = tf.pages[0].imagewidth
        return rows, cols

def is_rgb(path):
    with tifffile.TiffFile(path) as tf:
        return tf.pages[0].is_rgb

def get_zdepth(path):
    with tifffile.TiffFile(path) as tf:
        return tf.pages[0].image_depth

def imread(path):
    # Some images I made with tifffile and then split using tiffmakemosaic I could only 
    # open this way due the above "AttributeError""
    with tifffile.TiffFile(path) as tf:
        return tf.pages[0].asarray()