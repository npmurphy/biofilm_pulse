
# coding: utf-8

# In[ ]:


# In[ ]:


# In[ ]:

import skimage.filters
import skimage.feature
import numpy as np
#from collections import Counter
import os.path 
from lib.common import read_lsm# , save_tiff
from numpy import random
from glob import glob
#import scipy.ndimage


# In[ ]:


# In[ ]:


# In[ ]:

def top_is_on_left(fn, check_top=True):
    if ("top" not in os.path.basename(fn)) and check_top :
        raise Exception("Not a 'top' image")
    else :
        im = read_lsm(fn)[:,:,0]
        w = im.shape[1]
        if sum(np.ravel(im[:,0:w//6])) <= sum(np.ravel(im[:,-w//6:-1])):
            return True
        else :
            return False


# In[ ]:

loc_order = ["_top", "_middle", "_middle_2", "_middle2", "_middle3","_middle_3", "_middle4", "_middle_4", "_middle5","_middle_5", "_base", "_base2", "_base_2"]

def get_files_in_order(top_fname):
    loc_files = [top_fname.replace("_top", l) for l in loc_order]
    files_in_ord = [l for l in loc_files if os.path.exists(l)]
    x = top_fname.find("top")
    all_pattern = glob(top_fname[:x] + "*.lsm")
    left_out = set(all_pattern).difference(files_in_ord)
    return files_in_ord, list(left_out)


# In[ ]:


# In[ ]:


# The 63x images are taken as two or three images accross the biofilm. 
# We stitch the images together to get a single image accross the biofilm. 

# In[ ]:


# In[ ]:


# In[ ]:

# its h_window because it is really half the size of the window
def point_window(point, h_window):
    #print(point)
    #print(h_window)
    return [slice(point[0] - h_window, point[0] + h_window, None ),
            slice(point[1] - h_window, point[1] + h_window, None )]


# To align two images, Image 1 with Image 2 we use [Normalised Cross-Correlation](http://en.wikipedia.org/wiki/Cross-correlation).
# This is a method where a template region of Image 2 is "slid" over Image 1 and at each point the simularity of the template with an equal area of Image 1. 

# We then computer the similarity (cross correlation) of the template with each region in the right hand side of Image 1. 
# Where the two images are different, we get a 0, where they are the same we get a 1.0. 
# For the above image we get the following for each of the regions. 

# ## Trying a new method using most common offest. 

# In[ ]:

def get_likeley_template_spots(image, num_pts, half_tmplt_size, max_overlap_px):
    interesting = skimage.feature.canny(image)
    interesting[:max_overlap_px,:] = False
    interesting[-max_overlap_px:,:] = False
    rr, cc = np.where(interesting)
    leftedge_idx = [ i for i, c in enumerate(cc) if (c<max_overlap_px) and (c > half_tmplt_size) ]
    #print(leftedge_idx)
    selection = random.choice(leftedge_idx, size=num_pts)
    template_center_list = [ (rr[i], cc[i]) for i in selection] 
    return template_center_list


# In[ ]:


# In[ ]:

def join_images_with_offset(im1, im2, offset):
    sr, sc = offset

    im2_srt_row_in_im1space = 0 + sr
    im2_end_row_in_im1space = im2.shape[0] + sr
    
    im1_srt_row_in_im2space = 0 - sr
    im1_end_row_in_im2space = im1.shape[0] - sr
    
    im1_srt_row_in_im1space = max(0, im2_srt_row_in_im1space)
    im1_end_row_in_im1space = min(im1.shape[0], im2_end_row_in_im1space)
    
    im2_srt_row_in_im2space = max(0, im1_srt_row_in_im2space)
    im2_end_row_in_im2space = min(im2.shape[0], im1_end_row_in_im2space)
    
    imn_rows = im1_end_row_in_im1space - im1_srt_row_in_im1space
    if len(im1.shape) == len(im2.shape) == 3:
        imn = np.zeros( ( imn_rows, sc + im2.shape[1], im2.shape[2]), im1.dtype)
        imn[:,:im1.shape[1],:] = im1[im1_srt_row_in_im1space:im1_end_row_in_im1space, :,:] 
        imn[:,sc:,:] = im2[im2_srt_row_in_im2space:im2_end_row_in_im2space, :,:]
    elif len(im1.shape) == len(im2.shape) == 2:
        imn = np.zeros( ( imn_rows, sc + im2.shape[1]), int)
        imn[:,:im1.shape[1]] = im1[im1_srt_row_in_im1space:im1_end_row_in_im1space, :] 
        imn[:,sc:] = im2[im2_srt_row_in_im2space:im2_end_row_in_im2space, :]
    else:
        raise Exception("more than 3 dimensions")

    return imn


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

# def join_images(srch_img, tmplt_img):
#     overlap = int(4.5 / 0.05) # 4.5 um in pixels
#     half_temp_size = 25 
#     number_of_templates = 20
#     number_of_candidates = 10
#     tps = get_likeley_template_spots(tmplt_img[:,:,0], number_of_templates, half_temp_size, overlap)
#     offset_counts = get_row_col_shift_counts(srch_img[:,:,0], tmplt_img[:,:,0], tps, half_temp_size,  number_of_candidates)
#     offset_counts = remove_ones_from_count(offset_counts)
#     if len(offset_counts) == 0:
#         raise Exception("No points matched on this image:") # std ", stdv, offset_counts )
#     offset, stdv = get_weighted_mean_shift(offset_counts)

#     if stdv[0] > 300.0 or stdv[1] > 300.0:
#         print("\t \t big deviations" + str(stdv))
#         #find_minimal_overlap
#     return join_images_with_offset(srch_img, tmplt_img, offset)


# # What if there is extremly little overlap

# In[ ]:

def in_ipynb():
    try:
        cfg = get_ipython().config 
        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
            return True
        else:
            return False
    except NameError:
        return False


# In[ ]:


# In[ ]:

def get_plain_row_col_shift_map(im1i, im2i):
    #im1 = skimage.filters.sobel(im1[:,:,0])[1:-2, 1:-2]
    #im2 = skimage.filters.sobel(im2[:,:,0])[1:-2, 1:-2]
    im1 = skimage.filters.gaussian_filter(im1i[:,:,0], 1)
    im2 = skimage.filters.gaussian_filter(im2i[:,:,0], 1)
    result = np.zeros(( 60,int(im1i.shape[0]*0.8))) 
    rowshifts = list(range(-result.shape[0]//2, result.shape[0]//2)) # -20 to + 20 
    colshifts = list(range(im1.shape[1] - result.shape[1], im1.shape[1]))
    
    for i, c in enumerate(colshifts):
        for j, r in enumerate(rowshifts):
            im2_srt_row_in_im1space = 0 + r
            im2_end_row_in_im1space = im2.shape[0] + r

            im1_srt_row_in_im2space = 0 - r
            im1_end_row_in_im2space = im1.shape[0] - r

            im1_srt_row_in_im1space = max(0, im2_srt_row_in_im1space)
            im1_end_row_in_im1space = min(im1.shape[0], im2_end_row_in_im1space)

            im2_srt_row_in_im2space = max(0, im1_srt_row_in_im2space)
            im2_end_row_in_im2space = min(im2.shape[0], im1_end_row_in_im2space)

            tmlt = im1[im1_srt_row_in_im1space:im1_end_row_in_im1space, c ] - im2[im2_srt_row_in_im2space:im2_end_row_in_im2space, 0]
            result[j,i] = np.sum(tmlt**2)/tmlt.shape[0]
    #result = scipy.ndimage.median_filter(result, size=5)
    return result, rowshifts, colshifts


# In[ ]:


def find_minimal_overlap(im1, im2):
    result, rowshifts, colshifts = get_plain_row_col_shift_map(im1,im2)
    minv = np.unravel_index(np.argmin(result), result.shape)
    
    # if in_ipynb():
    #     figure(figsize(15,15))
    #     #result = 
    #     imshow(result, cmap=cm.hot)
    #     #print(result.shape)
    #     #colorbar()
    #     title(str(result[minv]) + "   " +str(ndarray.max(result)), fontsize=12)
    #     #xticks(range(len(colshifts)), [ str(c) for c in colshifts], rotation='vertical')
    #     #yticks(range(len(rowshifts)), list(map(str, rowshifts)))
    #     scatter(minv[1], minv[0], s=100, marker="o")
    #     print( rowshifts[minv[0]], colshifts[minv[1]] )
    #     #plot()
    
    return rowshifts[minv[0]], colshifts[minv[1]]
    


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# ## Quick test to see if we can just use the shift method

# ### Is there photo bleaching? 

# From the images below we see that there is a little bit of photo bleaching at the joins. 

# In[ ]:


# In[ ]:

