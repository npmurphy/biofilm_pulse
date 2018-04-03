
# coding: utf-8

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:

import numpy as np
from numpy import ma


# ### Files 

# In[ ]:


# # To detect where the agar is (447/455). 

# We take 5, 100 pixel wide row slices from the 1/2, 1/5, 2/5, 3/5, 4/5 points in the image. The idea is to get a more "typical" sample of the image in cross section. Getting a few thin slices is supposed to avoid lumps or regional blobs that might confuse the algorithm. Having 5 dillutes the effect of any blobs there are. 

# In[ ]:

def get_sample_rows(shape, n, slice_width):
    mask = np.zeros(shape,dtype=bool)
    pts = [ i * im.shape[0]//(n+1) for i in range(1,n+1)]
    s = slice_width//2
    for pt in pts: 
        mask[pt-s:pt+s,:] = True 
    return pts, mask


# In[ ]:


# We then get the average of the columns with data only from these rows, this gives us a 1d signal.
# We then get the first derivitave of this. The idea being that the agar zone is more up and down and so will give us a larger sum than the non agar part of the image. 
# We compare the sum of squares of the leftmost 200 pixel columns and rightmost 200 pixel columns to make our decision. 

# With these settings:
#     
# get_number_of_turn(read_lsm(fn), num_slice=5, slice_width=100, edge_width=200) 
# 
# 447 455

# In[ ]:

def get_slope_and_sum(img, lmask, width):
    sub = ma.masked_where(lmask==False, img)
    mimsec = ma.mean(sub, axis=0)
    mslop = np.diff(mimsec, n=1)
    scale =  mslop**2 # * (mimsec[:-1]/np.max(mimsec))
    leftsum = np.sum(scale[:width])
    rightsum = np.sum(scale[-width:])
    rot = 3 if leftsum < rightsum else 1 
    # 3 is 3, 90 degree turns in the counter-clockwise direction, a right turn 
    # 1 is 1, 90 degree turns in the counter-clockwise direction, a left turn 
    return rot, leftsum, rightsum, mimsec, mslop


# In[ ]:


# In[ ]:


# In[ ]:


# # Check How much it got right.

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# ## Preparing images

# In[ ]:

if __name__ == "__main__":
    import tifffile    
    import os.path
    cols = 3 # 3*2
    rows = 6

    for start in range(0,len(files)+1, cols*rows):
        print(start)
        fig, ax = subplots(rows,cols*2)
        fig.set_size_inches(ax.shape[1]*3, ax.shape[0]*3)

        for i, (n, fn) in enumerate(lfiles[start:start+(cols*rows)]):
            im = read_lsm(fn)
            print(n, fn, end="\r")
            j = i % rows
            o = 2 * (i//rows)
            r = 2 * (i//rows) +1

            rot = get_number_of_turns(im)
            oim = np.rot90(im, k=rot)
            
            new_name = os.path.basename(fn).replace("lsm", "tiff")
            new_dir = "hdisk/slice10x_analysis/images"
            tifffile.imsave(os.path.join(new_dir, new_name), oim)
            #print(n,i, j, o, r), 
            ax[j, o].imshow(im[:,:,0])
            oim = orient_image(im)
            ax[j, r].imshow(oim[:,:,0])
            #ax[j, r].annotate(st, xy=(0.8, 0.9), xycoords="axes fraction", color=c, fontsize=20)
            ax[j, r].set_title(n)
        fig.savefig("/tmp/check_orient/{0}.png".format(start), dpi=100 )
        fig.clear()
        pylab.close(fig)


# In[ ]:


# In[ ]:


# In[ ]:


# ## Make an answer map

# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# ## Compare all images

# In[ ]:


# ### Failed improvements. 

# Classic is 447 455
# 
# get_number_of_turns_classic(read_lsm(fn), num_slice=7, slice_width=80, edge_width=300)
# 442 455
# 
# get_number_of_turns(read_lsm(fn), num_slice=7, slice_width=60, edge_width=300)
# 425 455

# In[ ]:

