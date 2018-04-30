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
    smallfont = ImageFont.truetype("Arial", 30)
    # draw.text((x, y),"Sample Text",(r,g,b))
    #draw.text((0, 0), "{0} mins".format(i * 15), (255, 255, 255), font=font)
    time = time_offset + (i * time_step)
    hour = time // 60
    mins = time % 60
    draw.text((0, 0), "{0}:{1:02}".format(hour, mins), (255, 255, 255), font=font)
    try:
        annotation_list = arrow_locations[i]
        for arrow_loc, direct, num  in annotation_list:
            actual_loc = (arrow_loc[0] - ROI[1].start, arrow_loc[1] - ROI[0].start)
            if direct == "r":
                draw.bitmap( actual_loc, arrpil_r, fill=(255, 255, 255))
                num_offset = (0,0)
            else:
                draw.bitmap( actual_loc, arrpil, fill=(255, 255, 255))
                num_offset = (30,0)
            num_loc = tuple([sum(x) for x in zip(actual_loc , num_offset)])
            draw.text(num_loc , "{0}".format(num), (255, 255, 255), font=smallfont)
    except KeyError:
        pass
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

    #image_range = list(range(22, 33))
    thisdir = os.path.dirname(__file__)
    outimage = os.path.join(thisdir, "delru_bf10_col2")
    #start_time 
    frame_selection = [ 48, 58, 68 , 78, 88, 98]
    #frame_selection = [ 28 + (s)*25 for s in range(6)] 
    #image_range = list(range(25, 41, 1))
    arrow_locations = {} # in XY
        # 25: [((700, 558), "l", 1)], # 375
        # 26: [((703, 553), "l", 1)], # 390
        # 27: [((707, 585), "l", 1)], # 405
        # 28: [((695, 568), "l", 1)], # 420
        # 29: [((715, 565), "l", 1)], # 435
        # 30: [((720, 526), "l", 1)], # 450
        # 31: [((712, 536), "l", 1)], # 465
        # 32: [((718, 542), "l", 1)], # 480
        # 33: [((700, 565), "l", 2)], # 495
        # 34: [((670, 566), "l", 2)], # 510
        # 35: [((660, 560), "l", 2)], # 525
        # 36: [((662, 575), "l", 2),
        #      ((550, 543), "r", 3) ], # 540 # tracking a different cell now
        # 37: [((650, 565), "l", 2),
        #      ((520, 520), "r", 3)], # 555
        # 38: [((570, 510), "l", 3)], # 570
        # 39: [((550, 500), "l", 3)], # 585
        # 40: [((555, 490), "l", 3)]  # 600
        # } 
    yfp_images = [ skimage.io.imread(image_path.format(i, "01")) for i in frame_selection]
    #phs_images = [ skimage.io.imread(path.format("p", i)) for i in image_range]
    rfp_images = [ skimage.io.imread(image_path.format(i, "00")) for i in frame_selection]
    print( yfp_images[0].shape, rfp_images[0].shape)
    max_yfp = 4000 #350 #np.max([ y.max() for y in yfp_images])
    #min_yfp = 254 #(max bacground)
    min_yfp = 680 #300 #329 #(mean off cell)
    max_rfp = 10000 # chosen
    min_rfp = 730 # chosen
    # max_phase = np.max([ y.max() for y in phs_images])
    # min_phase = np.min([ y.min() for y in phs_images])
    #ROI = (slice(300,760), slice(570, 780)) # Row Col
    ROI = (slice(0,1048), slice(700, 2000)) # Row Col

    # arrow = skimage.io.imread("arrow_ang.tif")#[:, :,0]
    # arrpil = Image.fromarray(arrow) #, mode='L').convert('1')
    # arrpil_r = arrpil.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    proc_yfp = [process_fp(im, ROI, min_yfp, max_yfp) for im in yfp_images]
    proc_rfp = [process_fp(im, ROI, min_rfp, max_rfp) for im in rfp_images]
    #proc_phase = [process_phase(im, ROI, min_phase, max_phase) for im in phs_images]
    #joined_phs = np.hstack(list([process_phase(im, i, min_phase, max_phase) for i, im in zip(image_range, phs_images)]))

    # YFP and phase
    #color_indv = [np.dstack([p, add_no_over(p, y), p]) for y, p in zip(proc_yfp, proc_phase)]
    #color_indv = [np.dstack([add_no_over(p, r), add_no_over(p, y), p]) for r, y, p in zip(proc_rfp, proc_yfp, proc_phase)]
    color_indv = [np.dstack([r, y, np.zeros_like(r)]) for y, r in zip(proc_yfp, proc_rfp)]

    color_anotate = [add_annotations(im, i, start_time, step_time) for i, im in zip (frame_selection, color_indv)]

    rows = 2
    imgs_in_row = len(color_anotate)//rows
    list_of_points = [ ((r * imgs_in_row), ((r + 1) * imgs_in_row) )  for r in range(rows)]
    print(list_of_points)

    image_rows = [np.hstack(color_anotate[(r * imgs_in_row): ((r + 1) * imgs_in_row)]) for r in range(rows)]
    final = np.vstack(image_rows)
    skimage.io.imsave(outimage + "_strip.png", final)
    #skimage.io.imsave(outimage + "_strip.jpg", final)
