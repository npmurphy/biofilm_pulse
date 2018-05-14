import os.path
import matplotlib.pyplot as plt
#import matplotlib.ticker as mticker
#import matplotlib.gridspec as gs
import numpy as np
import skimage.io
import skimage.exposure


from lib.resolutions import PX_TO_UM_LSM780_63x as PX_TO_UM
##plt.style.use('../figstyle.mpl')
from lib.figure_util import draw_scale_bar

def process_channel(path, ch, rescale, roi, cache_dir):
    slice_r, slice_c = roi
    cordstr = "_".join([ str(x) for x in [slice_r[0],slice_r[1], slice_c[0],slice_c[1]]]) + ".tiff"
    cachename = "spoiid_image_{0}_".format(ch) + cordstr 
    print(cachename)
    cache_path = os.path.join(cache_dir, cachename)
    if os.path.exists(cache_path):
        print("using cached image ", cachename )
        im = skimage.io.imread(cache_path)
    else:
        im = skimage.io.imread(path)
        im = im[slice_r[0]:slice_r[1], slice_c[0]:slice_c[1]].copy()
        skimage.io.imsave(cache_path, im)
    im = skimage.exposure.rescale_intensity(im[:,:].astype(np.uint32), in_range=rescale, out_range=(0,255)).astype(np.uint8)
    return im 


def get_figure(ax, img_base, cache_path):
    name = "JLB124_48hrs_center_63x_tilescan_unmixing"
    pattern = "_c{0}.tiff"
    img_pattern = os.path.join(img_base, name, name + pattern)
    ## The LSM is rotated 90 clockwise compared to the extrated images. 
    c = 1335 #(19563 - 17728 - 500)
    r = 5281
    w = 500
    slice_it = ((r, r+w), (c, c+w))
    #strain = "wt_sigar_sigby_spoiidc"
    maxv = (2**16)-1
    channel_settings = [("r", (7000, int(maxv*1.3)), slice_it),
                        ("g", (3000, int(maxv*0.8)), slice_it),
                        ("b", (2000, 12000), slice_it),
                        ]
    print("channel settings", channel_settings)
    #channels = [ process_channel(img_pattern.format(ch), rescale, region) for ch, rescale, region in channel_settings]
    channels = [ process_channel(img_pattern.format(ch), ch, rescale, region, cache_path) for ch, rescale, region in channel_settings]
    img = np.dstack(channels)
    # make magenta 
    #img[:,:,0] = np.max(np.dstack([img[:,:,0], img[:,:,2]]), axis=2)
    #img[:,:,0] = 0 # hide red
    # turn blue to red 
    # img[:,:,0] = img[:,:,2] 
    # img[:,:,2] = 0
    img = np.rot90(img)
    print(img.shape)
    img = draw_scale_bar(img, 30, 30, 5/PX_TO_UM, 10, "5μm")

    #label = "figure_util.strain_label[des_strain_map[strain].upper()]
    #ax.imshow(img, interpolation="none") #bicubic")
    ax.imshow(img, interpolation="bilinear") # Turn to none before submissiton 
    #ax.set_title(label)
    ax.grid(False)
    ax.axis('off')
    #aximg.text(letter_lab[0], letter_lab[1], letters[i], transform=aximg.transAxes, fontsize=8)
    return ax

def main():
    fig, ax = plt.subplots(1,1)
    base = "../../proc_data/fp3_unmixing/rsiga_ysigb_cspoiid/"
    ax = get_figure(ax, base)
    plt.show()


if __name__ == "__main__":
    main()