
# coding: utf-8

# In[ ]:


# In[ ]:

import skimage.transform
import scipy.ndimage
from numpy import ndarray
import skimage.morphology
import numpy as np


# In[ ]:


# In[ ]:


# In[ ]:


# The proceedure to get an outline of the 63x images of the bio-film is as follows. 
# \begin{compactitem}
# \item Pyramid reduce the image down in size by a factor of 4, this speeds up the processing and blurs some details around the edges to make them smooth. 
# \item Median filter the image with a circle of width 5 pixels. 
# \item threshold the image with the value $ \min(\mathcal{I}) + (\max(\mathcal{I}) - \min(\mathcal{I})) * 0.07$. 
#   Is a magic number it doesnt seem to have much effect so could be improveable. 
# \item We then close up the holes in the mask. 
# \item We erode the image with circle of diameter 12 pixels to avoid the absolute edges. 
# \item We expand out the mask to normal size then remove all unconected components that are less than $1\over 3$ the area of the image. 
# \end{compactitem}

# In[ ]:

def get_biofilm_mask(img):
    mask = skimage.transform.pyramid_reduce(img, downscale=4)
    mask = scipy.ndimage.filters.median_filter(mask,footprint=skimage.morphology.disk(5))
    minf = ndarray.min(mask)
    maxf = ndarray.max(mask)
    threshold = ((maxf - minf) * 0.07 ) + minf
    mask = mask>threshold # biofilm is true
    mask = scipy.ndimage.morphology.binary_fill_holes(mask) # fill holes
    mask = skimage.transform.pyramid_expand(mask, upscale=4).astype(np.bool) # blow back up to big

    orig_size = img.shape
    new_size = mask.shape
    #print("old", orig_size)
    #print("new", new_size)
    row_shift = int(np.round((orig_size[0] - new_size[0])/2))
    col_shift = int(np.round((orig_size[1] - new_size[1])/2))
    new_mask = np.zeros(orig_size, dtype=mask.dtype)
    # TODO this might cause problems. when the new image is bigger, it works great. 
    # Need to check other cases though
    #if row_shift < 0 or col_shift < 0:
    new_mask[:, :] = mask[0:orig_size[0], 0:orig_size[1]]
    # else:
    #     #new_mask[0:new_size[0], 0:new_size[1]] = mask[:, :] #[0:new_img.shape[0], 0:new_img.shape[1]]
    #     new_mask[0:orig_size[0], 0:orig_size[1]] = mask[:orig_size[0], :] #[0:new_img.shape[0], 0:new_img.shape[1]]

    mask = skimage.morphology.erosion(new_mask, selem=skimage.morphology.disk(6)) # erode biofilm
    mask, _ = scipy.ndimage.label(mask)
    skimage.morphology.remove_small_objects(mask, np.size(mask)//3, in_place=True)
    return mask.astype(bool)


# In[ ]:


# In[ ]:

def fill_biofilm_mask(mask, direction):
    mask = np.vstack([np.ones(mask.shape[1],mask.dtype), mask, np.ones(mask.shape[1],mask.dtype)])
    if direction == "bottom":
        mask = np.hstack([np.zeros((mask.shape[0], 1),mask.dtype), mask, np.ones((mask.shape[0],1),mask.dtype)])
    elif direction == "top":
        mask = np.hstack([np.ones((mask.shape[0], 1),mask.dtype), mask, np.zeros((mask.shape[0],1),mask.dtype)])
    else:
        raise ValueError( direction + " is neither 'top' nor 'bottom' ")
    mask = scipy.ndimage.binary_fill_holes(mask)[1:-1,1:-1]
    return mask

def get_biofilm_mask_filled(ima, direction):
    return fill_biofilm_mask(get_biofilm_mask(ima), direction)


# In[ ]:

def get_biofilm_mask_filled_bottom(ima):
    return get_biofilm_mask_filled(ima, "bottom")

def get_biofilm_mask_filled_top(ima):
    return get_biofilm_mask_filled(ima, "top")


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

