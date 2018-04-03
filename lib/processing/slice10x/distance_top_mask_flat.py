
# coding: utf-8

# In[ ]:


# In[ ]:


# In[ ]:

import scipy.ndimage as ndimage
import numpy as np
import skimage.measure
from lib.resolutions import PX_TO_UM_LSM780_10x
#from . import get_image_mask, get_cached_data, set_cached_data


# In[ ]:


# In[ ]:


# We demonstrate the 10x data processing phase with an example image.

# In[ ]:


# First we segment the image using our Gabor segmentation method.

# In[ ]:


# In[ ]:

def get_top_mask(mask):
    top = mask.astype(bool).copy() 
    for c in range(top.shape[1]):
        rs = np.where(top[:, c] == True)[0]
        if len(rs) != 0:
            r = rs[-1]
            top[r:,c] = True
    top = ndimage.binary_fill_holes(top)
    return top


# We want to look at fluoresence from the top of the biofilm. To do this we use euclidian distance from the top. 
# The method measures how far each True pixel is from the nearest False pixel, the edges do not count.
# We block off the bottom of the biofilm. 

# In[ ]:


# In[ ]:

def get_distance_map(mask):
    top = get_top_mask(mask)
    top_dist = np.zeros_like(top, dtype=np.float64)
    ltop, _ = ndimage.label(top)
    props = skimage.measure.regionprops(ltop)
    start_stop_pairs = [ (p.bbox[1], p.bbox[3]) for p in props] 
    for start, stop in start_stop_pairs:
        h = ndimage.distance_transform_edt(top[:, start:stop])
        top_dist[:, start:stop] = h

    distmap = top_dist * mask.astype(bool)
    return distmap


# In some cases parts of the biofilm do not touch the edge of the image. 
# In this case we split each section up into sub-images and measure the distance from the edge individually. 

# In[ ]:


# In[ ]:


# We then multiply with the mask to give us a map of the euclidian distance of each pixel in the biofilm from the top. 

# In[ ]:


# In[ ]:


# def get_distance_map_cached(fn, segmenter=get_image_mask, force_recompute=0):
#     try: 
#         if force_recompute:
#             1/0
#         return get_cached_data(fn, 'distmap')       
#     except (FileNotFoundError, KeyError,ZeroDivisionError) as e:
#         mask = segmenter(fn)
#         dist = get_distance_map(mask)
#         set_cached_data(fn, dist, 'distmap')
#         return dist 


# In[ ]:


# ## Get relatively flat bits of the biofilm top edge. 

# In[ ]:

def get_flat_areas(top, minimum_pixel_width=100, sensitivity=3 ):
    struc = skimage.morphology.disk(1)
    erode = skimage.filters.edges.binary_erosion(top, structure=struc, border_value=1)
    edge = top - erode
    sv = skimage.filters.sobel_v(edge)
    verticals = np.sum(sv,axis=0) >= sensitivity
    verticals = verticals | (np.sum(edge, axis=0) > 2 )

    l, n = ndimage.label(np.invert(verticals))
    lr = skimage.morphology.remove_small_objects(l, min_size=minimum_pixel_width)
    lr = ndimage.morphology.binary_erosion(lr, structure=np.ones(int(40/PX_TO_UM),)) ## reduce influence of activation 
    # near the edge of flat bits by removing 40um
    lre, n = ndimage.label(lr)
    flat_areas = np.tile(lre, top.shape[0])
    return flat_areas.reshape(top.shape)


# In[ ]:


# First get the edge pixels by eroding the mask and subtracting. 

# In[ ]:


# Then do a Sobel transform which is the slope of the line. 
# We do a seperate vertical and horizontal Sobel transform. 
# We then sum the columns of the images. 
# In the horizontal sobel we dont get much signal, I guess positive and negative slopes cancelled out. 
# In the vertical sobel we get nice spikes when the biofilms bends in a different column so the postive and negative do not cancel out.
# 
# We also sum the edge image and remove places where the sum indicates there was some folding over of the biofilm. 
# We add this because there were cases were the horizontal sobel said it was flat but there was a folding of the biofilm. 

# In[ ]:


# To find the zones that big enough we use some the labeling functions. 
# First we label all the areas that were marked as flat. 
# Then we remove all labels that are less than a particular size.
# Currently that is 100 pixels wide (~70\mu m). 

# In[ ]:


# In[ ]:

