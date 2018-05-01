#import glob.glob
import skimage.io
import numpy as np
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import matplotlib.pyplot as plt
from lib.cell_tracking.track_data import TrackData
import lib.cell_tracking.track_data as track_data
import os.path

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

def add_annotations(im, i, time_offset, time_step):
    pilim = Image.fromarray(im)
    draw = ImageDraw.Draw(pilim)
    # font = ImageFont.truetype(<font-file>, <font-size>
    font = ImageFont.truetype("Arial", 60)
    #smallfont = ImageFont.truetype("Arial", 30)
    # draw.text((x, y),"Sample Text",(r,g,b))
    #draw.text((0, 0), "{0} mins".format(i * 15), (255, 255, 255), font=font)
    time = time_offset + (i * time_step)
    hour = time // 60
    mins = time % 60
    draw.text((0, 0), "{0}:{1:02}".format(hour, mins), (255, 255, 255), font=font)
    # try:
    #     annotation_list = arrow_locations[i]
    #     for arrow_loc, direct, num  in annotation_list:
    #         actual_loc = (arrow_loc[0] - ROI[1].start, arrow_loc[1] - ROI[0].start)
    #         if direct == "r":
    #             draw.bitmap( actual_loc, arrpil_r, fill=(255, 255, 255))
    #             num_offset = (0,0)
    #         else:
    #             draw.bitmap( actual_loc, arrpil, fill=(255, 255, 255))
    #             num_offset = (30,0)
    #         num_loc = tuple([sum(x) for x in zip(actual_loc , num_offset)])
    #         draw.text(num_loc , "{0}".format(num), (255, 255, 255), font=smallfont)
    # except KeyError:
    #     pass
    return np.array(pilim)

def add_no_over(a, b):
    r = a.copy()
    b = 255 - b  
    np.putmask(r, b < r, b)  
    r += 255 - b 
    return r


if __name__ == "__main__":
    #
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
