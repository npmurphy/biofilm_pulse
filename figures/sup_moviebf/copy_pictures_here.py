import skimage.io
import os.path
import numpy as np

this_dir = os.path.dirname(__file__)
biofilm_edge_photo = os.path.join(this_dir, "../../proc_data/bf_live_photos/BF_movie12/DSC_0342.JPG")
biofilm_top_photo = os.path.join(this_dir, "../../proc_data/bf_live_photos/BF_movie12/DSC_0325.JPG")

bfedge = skimage.io.imread(biofilm_edge_photo)[0]
## Image seems to have two things in side. 
# 0 is the normal image and [1] is 
#<PIL.MpoImagePlugin.MpoImageFile image mode=RGB size=6000x4000 at 0x118124BE0>
#(2,)
bfedge = np.flipud(bfedge)
skimage.io.imsave(os.path.join(this_dir, "bf_edge_photo.jpg"), bfedge)



bftop = skimage.io.imread(biofilm_top_photo)[0]
## Image seems to have two things in side. 
# 0 is the normal image and [1] is 
#<PIL.MpoImagePlugin.MpoImageFile image mode=RGB size=6000x4000 at 0x118124BE0>
#(2,)
bftop = np.flipud(bftop)
skimage.io.imsave(os.path.join(this_dir, "bf_top_photo.jpg"), bftop)

grad_image = skimage.io.imload(os.path.join(this_dir, "tilescan_3.tif"))
bftop = skimage.io.imread(biofilm_top_photo)[0]
## Image seems to have two things in side. 
# 0 is the normal image and [1] is 
#<PIL.MpoImagePlugin.MpoImageFile image mode=RGB size=6000x4000 at 0x118124BE0>
#(2,)
bftop = np.flipud(bftop)
skimage.io.imsave(os.path.join(this_dir, "bf_top_photo.jpg"), bftop)
