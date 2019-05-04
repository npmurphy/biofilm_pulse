
# coding: utf-8

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

import skimage
from scipy import ndimage
from skimage.morphology import disk
#from skimage.util import img_as_float
#from skimage.filters import gabor_kernel
import skimage.feature
import numpy as np
import scipy.ndimage
import os.path
import scipy.io
from lib.common import read_lsm


# In[ ]:


# In[ ]:


# In[ ]:


# ### Current Method

# The input image is normalised by subtracting the mean and dividing by the standard deviation. 
# This is the standard score and tells us how many standard deviations away from the mean each pixel is. 
# I dont know if this is a good idea, I use this because the Gabor filter example code used it. 

# In[ ]:


# In[ ]:


# In[ ]:

def new_rough_segment(im, gaussian=5):
    gauss_blur = scipy.ndimage.filters.gaussian_filter(im, gaussian)
    ot = skimage.filters.threshold_otsu(gauss_blur)
    return gauss_blur>ot


# In[ ]:


# In[ ]:


# We will use this mask now as the outline for watershed segmentation.
# We will try to find a lot of local maxima to start the watershed from. 
# The idea is to really over segment the image so it will be easier to remove the agar. 

# In[ ]:


# As the gradient for the watershed segmentation we use a guassian smoothing of the image itself. 

# In[ ]:


# To remove the agar that has been included in the segmentation, we erode the image using a disk of radius 15 pixels.
# This removes all trace of the segments that are agar, but leaves the bigger bio-film segments. 

# We see which segments surrive the errosion and keep those segments to make the bio-film mask. 

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# We merge all the segments then fill in any holes. 
# We then remove all blobs that are less than 5% of the image total area. 
# 

# Finally we just erode the mask with a disk or diameter 5. 
# This just reduces ammount to biofilm--air interface that is included in the segmentation. 

# In[ ]:

def basic_segment(im, gaussian=5):
    msk = new_rough_segment(im)

    gim = skimage.filters.gaussian(im, gaussian)
    pk = skimage.feature.peak_local_max(gim*msk, indices=False, min_distance=20, num_peaks=5000)
    lb, n = ndimage.label(pk)
    
    wsh = skimage.morphology.watershed(-gim, lb, mask=msk)
    erwh = skimage.morphology.erosion(wsh.astype(np.bool), disk(25))
    wshm = wsh.copy()
    erod_lab = np.unique(erwh.astype(np.bool)*wsh)
    orig_lab = np.unique(wsh)

    for l in orig_lab:
        if l not in erod_lab:
            wshm[wsh==l] = 0
    wshm = wshm.astype(bool)
    wshm = ndimage.binary_fill_holes(wshm)
    skimage.morphology.remove_small_objects(wshm, int(np.size(wshm)*0.01),
                in_place=True)
    #wshm = skimage.morphology.erosion(wshm, selem=disk(5))
    return wshm


def smooth_segmentation(mask):
    mask_smooth = scipy.ndimage.morphology.binary_fill_holes(mask)
    mask_smooth = skimage.morphology.binary_opening(mask_smooth, selem=skimage.morphology.disk(9)).astype(mask.dtype)
    n = np.prod(mask.shape)
    m = int(0.1 * n)
    mask_smooth = skimage.morphology.remove_small_objects(mask_smooth.astype(bool),min_size=m)
    return mask_smooth
# ### Segment All the images 

# In[ ]:

def get_cached_data(fn, key):
    if os.path.splitext(fn)[1] == '.tiff':
        fn = fn.replace(".tiff", ".mat")
    try:
        return scipy.io.loadmat(fn)[key]
    except (FileNotFoundError, KeyError) as e :
        raise e  


# In[ ]:

def set_cached_data(fn, data, key):
    if os.path.splitext(fn)[1] == '.tiff':
        fnm = fn.replace(".tiff", ".mat")
    else: 
        fnm = fn 
    if os.path.exists(fnm):
        #print("this exists: ", fnm)
        loaded = scipy.io.loadmat(fnm)
    else :
        loaded = {}
    loaded[key] = data
    scipy.io.savemat(fnm, loaded, do_compression=True)


# In[ ]:

def get_image_mask(fn, force_recompute=0):
    try: 
        if force_recompute:
            1/0
        return get_cached_data(fn, 'mask').astype(np.bool)
    except (FileNotFoundError, KeyError,ZeroDivisionError,OSError) as e:
        mask = basic_segment(read_lsm(fn)[:,:,0])
        set_cached_data(fn, mask, 'mask')
        return mask 


# In[ ]:


# In[ ]:

