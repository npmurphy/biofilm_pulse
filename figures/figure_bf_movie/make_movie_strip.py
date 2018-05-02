#import glob.glob
import skimage.io
import numpy as np
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import matplotlib.pyplot as plt
import lib.figure_util
from lib.cell_tracking.track_data import TrackData
import lib.cell_tracking.track_data as track_data
import os.path
from lib.resolutions import PX_TO_UM_IPHOX_100x_1p5zoom  as PX_TO_UM

def process_fp(im, ROI, min_fp, max_fp):
    lim = im.copy()
    lim[im<min_fp] = 0
    #rescale = skimage.exposure.rescale_intensity(im, in_range=(min_fp, max_fp), out_range="uint8").astype(np.uint8)
    print(min_fp, max_fp)
    rescale = skimage.exposure.rescale_intensity(lim, in_range=(min_fp, max_fp), out_range=(0, 255)).astype(np.uint8)
    #rescale = skimage.exposure.rescale_intensity(im, in_range=(0, max_fp), out_range=(0, 255)).astype(np.uint8)
    # plt.figure()
    # plt.hist(rescale.flatten(), bins=np.arange(1,256))
    # plt.show()
    cuted = rescale[ROI]
    return cuted

def process_phase(im, ROI, min_fp, max_fp):
    rescale = skimage.exposure.rescale_intensity(im, in_range=(min_fp, max_fp), out_range="uint8").astype(np.uint8)
    cuted = rescale[ROI]
    return cuted

def add_annotations(im, i, time_offset=0, time_step=1):
    pilim = Image.fromarray(im)
    draw = ImageDraw.Draw(pilim)
    # font = ImageFont.truetype(<font-file>, <font-size>
    font = ImageFont.truetype("Arial", 80)
    #smallfont = ImageFont.truetype("Arial", 30)
    # draw.text((x, y),"Sample Text",(r,g,b))
    #draw.text((0, 0), "{0} mins".format(i * 15), (255, 255, 255), font=font)
    time = time_offset + (i * time_step)
    hour = time // 60
    mins = time % 60
    draw.text((0, 0), "{0}:{1:02}".format(hour, mins), (255, 255, 255), font=font)

    return np.array(pilim)

def add_no_over(a, b):
    r = a.copy()
    b = 255 - b  
    np.putmask(r, b < r, b)  
    r += 255 - b 
    return r

def using_timelapse_movie():
    image_path="proc_data/iphox_movies/BF10_timelapse/Column_2/Column_2_t{0:03}_ch{1}.tif"
    data_path = "datasets/iphox_singlecell/BF10_timelapse/Column_2/cell_track.json"
    td = TrackData(data_path)
    start_time = track_data.parse_time(td.metadata["time_offset"])
    step_time = track_data.parse_time(td.metadata["time_step"])

    thisdir = os.path.dirname(__file__)
    outimage = os.path.join(thisdir, "delru_bf10_col2")

    #frame_selection = [ 48, 58, 68 , 78, 88, 98]
    #frame_selection = [ 30 + (s)*20 for s in range(3)] 
    #80 = 27 hours
    frame_selection = [ 110 + (s)*144 for s in range(3)] 
    rows = 1

    arrow_locations = {} # in XY
    yfp_images = [ skimage.io.imread(image_path.format(i, "01")) for i in frame_selection]
    rfp_images = [ skimage.io.imread(image_path.format(i, "00")) for i in frame_selection]
    print( yfp_images[0].shape, rfp_images[0].shape)
    #max_yfp = 4000 #350 #np.max([ y.max() for y in yfp_images])
    max_yfp = 3000 #350 #np.max([ y.max() for y in yfp_images])
    min_yfp = 680 #300 #329 #(mean off cell)
    max_rfp = 10000 # chosen
    min_rfp = 730 # chosen

    # Original full view
    #ROI = (slice(0,1048), slice(700, 2000)) # Row Col
    #zoomed in view
    ROI = (slice(0,800), slice(700, 1500)) # Row Col

    proc_yfp = [process_fp(im, ROI, min_yfp, max_yfp) for im in yfp_images]
    proc_rfp = [process_fp(im, ROI, min_rfp, max_rfp) for im in rfp_images]
    color_indv = [np.dstack([r, y, np.zeros_like(r)]) for y, r in zip(proc_yfp, proc_rfp)]

    color_anotate = [add_annotations(im, i, start_time, step_time) for i, im in zip (frame_selection, color_indv)]

    imgs_in_row = len(color_anotate)//rows
    list_of_points = [ ((r * imgs_in_row), ((r + 1) * imgs_in_row) )  for r in range(rows)]
    print(list_of_points)

    image_rows = [np.hstack(color_anotate[(r * imgs_in_row): ((r + 1) * imgs_in_row)]) for r in range(rows)]
    final = np.vstack(image_rows)
    skimage.io.imsave(outimage + "_strip.png", final)
    #skimage.io.imsave(outimage + "_strip.jpg", final)



def using_snap_shots():
    # column = 2
    # ROI2 = (slice(0,800), slice(1950, 2950)) # Row Col
    # ROI = (slice(0,800), slice(950, 1950)) # Row Col
    # def roi_time(x):
    #     if x == 12: 
    #         return ROI2
    #     else:
    #         return ROI
    
    column = 3
    ROI_12 = (slice(0,800), slice(1948, 2948)) # Row Col
    ROI = (slice(0,800), slice(1224, 2224)) # Row Col
    def roi_time(x):
        if x == 12: 
            return ROI_12
        else:
            return ROI

    thisdir = os.path.dirname(__file__)

    base_path = os.path.join(thisdir, "../../proc_data/iphox_live_gradient_checks/BF_12hoursnaps2/")
    timedir = "{1}hr_timepoint/delRU_{1}hr_Column{0}/delRU_{1}hr_Column{0}_c{2}.tiff"
    image_path = os.path.join(base_path, timedir)

    outimage = os.path.join(thisdir, "delru_bf10_col2")

    all_times = [ 12, 24, 36, 48, 60, 72, 96]
    time_selection = [ 24, 48, 72]
    time_selection = all_times
    rows = 2

    #arrow_locations = {} # in XY
    yfp_images = [ skimage.io.imread(image_path.format(column, t, "g")) for t in time_selection]
    rfp_images = [ skimage.io.imread(image_path.format(column, t, "r")) for t in time_selection]
    print( yfp_images[0].shape, rfp_images[0].shape)
    #max_yfp = 4000 #350 #np.max([ y.max() for y in yfp_images])
    max_yfp = 5000 #350 #np.max([ y.max() for y in yfp_images])
    min_yfp = 1000 #300 #329 #(mean off cell)
    max_rfp = 10000 # chosen
    min_rfp = 730 # chosen

    # Original full view
    #ROI = (slice(0,1048), slice(700, 2000)) # Row Col
    #zoomed in view


    proc_yfp = [process_fp(im, roi_time(t), min_yfp, max_yfp) for (t, im) in zip(time_selection, yfp_images)]
    proc_rfp = [process_fp(im, roi_time(t), min_rfp, max_rfp) for (t, im) in zip(time_selection, rfp_images)]
    color_indv = [np.dstack([r, y, np.zeros_like(r)]) for y, r in zip(proc_yfp, proc_rfp)]

    color_anotate = [add_annotations(im, i*60) for i, im in zip (time_selection, color_indv)]

    imgs_in_row = len(color_anotate)//rows
    #list_of_points = [ ((r * imgs_in_row), ((r + 1) * imgs_in_row) )  for r in range(rows)]

    image_rows = [np.hstack(color_anotate[(r * imgs_in_row): ((r + 1) * imgs_in_row)]) for r in range(rows)]
    final = np.vstack(image_rows)

    half = (final.shape[1] // 3) + 10
    length = 20 
    final = lib.figure_util.draw_scale_bar(final, 150, half,
                               scale_length=length/PX_TO_UM,
                               thickness=30,
                               legend = "{0}μm".format(length), fontsize=60)

    skimage.io.imsave(outimage + "_strip.png", final)
    #skimage.io.imsave(outimage + "_strip.jpg", final)


if __name__ == "__main__":
    using_snap_shots()