#import glob.glob
import skimage.io
import numpy as np
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
#import matplotlib.pyplot as plt
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

def add_annotations(im, i):
    pilim = Image.fromarray(im)
    draw = ImageDraw.Draw(pilim)
    # font = ImageFont.truetype(<font-file>, <font-size>
    font = ImageFont.truetype("Arial", 60)
    smallfont = ImageFont.truetype("Arial", 30)
    # draw.text((x, y),"Sample Text",(r,g,b))
    #draw.text((0, 0), "{0} mins".format(i * 15), (255, 255, 255), font=font)
    draw.text((0, 0), "{0}".format(i * 15), (255, 255, 255), font=font)
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


""" Original del RU movie 
    path = "movie_strip/sigB_biofilmpad6-O001_3-{0}-{1:03d}.tif"
    start = 22
    end = 31
    outimage = "sigB_biofilmpad6-O001_3_1" 
    #image_range = list(range(22, 33))
    image_range = list(range(23, 33))
    arrow_locations = { # in XY
        22: (663, 552),
        23: (665, 552),
        24: (665, 559),
        25: (670, 550),
        26: (675, 535),
        27: (675, 520),
        28: (675, 520),
        29: (685, 520),
        30: (693, 510),
        31: (693, 510),
        32: (700, 510),
        } 
"""
if __name__ == "__main__":
    this_dir = os.path.dirname(__file__)
    rpath = "../../proc_data/padmovies/2015-11-03/sigB_biofilmfinal-B_4/images/sigB_biofilmfinal-B_4-{0}-{1:03d}.tif"
    path = os.path.join(this_dir, rpath)
    #image_range = list(range(22, 33))
    outimage = "sigB_biofilmfinal-B_4"
    image_range = list(range(25, 41, 1))
    arrow_locations = {}
    # arrow_locations = { # in XY
    #     25: [((700, 558), "l", 1)], # 375
    #     26: [((703, 553), "l", 1)], # 390
    #     27: [((707, 585), "l", 1)], # 405
    #     28: [((695, 568), "l", 1)], # 420
    #     29: [((715, 565), "l", 1)], # 435
    #     30: [((720, 526), "l", 1)], # 450
    #     31: [((712, 536), "l", 1)], # 465
    #     32: [((718, 542), "l", 1)], # 480
    #     33: [((700, 565), "l", 2)], # 495
    #     34: [((670, 566), "l", 2)], # 510
    #     35: [((660, 560), "l", 2)], # 525
    #     36: [((662, 575), "l", 2),
    #          ((550, 543), "r", 3) ], # 540 # tracking a different cell now
    #     37: [((650, 565), "l", 2),
    #          ((520, 520), "r", 3)], # 555
    #     38: [((570, 510), "l", 3)], # 570
    #     39: [((550, 500), "l", 3)], # 585
    #     40: [((555, 490), "l", 3)]  # 600
    #     } 
    yfp_images = [ skimage.io.imread(path.format("y", i)) for i in image_range]
    phs_images = [ skimage.io.imread(path.format("p", i)) for i in image_range]
    rfp_images = [ skimage.io.imread(path.format("t", i))[0,:,:] for i in image_range]
    print( yfp_images[0].shape, rfp_images[0].shape)
    max_yfp = 500 #350 #np.max([ y.max() for y in yfp_images])
    #min_yfp = 254 #(max bacground)
    min_yfp = 269 #300 #329 #(mean off cell)
    max_rfp = 500 # chosen
    min_rfp = 220 # chosen
    max_phase = np.max([ y.max() for y in phs_images])
    min_phase = np.min([ y.min() for y in phs_images])
    #ROI = (slice(300,760), slice(570, 780)) # Row Col
    ROI = (slice(300,760), slice(500, 800)) # Row Col

    arrow = skimage.io.imread(os.path.join(this_dir, "arrow_ang.tif"))#[:, :,0]
    #skimage.io.imsave("arrow_ang.tif", arrow)

    # rarrow = skimage.exposure.rescale_intensity(arrow.astype(float), out_range=(0,1.0))
    # rarrow = -1 * (rarrow - 1.0)
    #print(arrow.shape)
    arrpil = Image.fromarray(arrow) #, mode='L').convert('1')
    arrpil_r = arrpil.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    proc_yfp = [process_fp(im, ROI, min_yfp, max_yfp) for im in yfp_images]
    proc_rfp = [process_fp(im, ROI, min_rfp, max_rfp) for im in rfp_images]
    proc_phase = [process_phase(im, ROI, min_phase, max_phase) for im in phs_images]
    #joined_phs = np.hstack(list([process_phase(im, i, min_phase, max_phase) for i, im in zip(image_range, phs_images)]))

    # YFP and phase
    color_indv = [np.dstack([p, add_no_over(p, y), p]) for y, p in zip(proc_yfp, proc_phase)]
    # YFP RFP and phase
    #color_indv = [np.dstack([add_no_over(p, r), add_no_over(p, y), p]) for r, y, p in zip(proc_rfp, proc_yfp, proc_phase)]
    color_anotate = [add_annotations(im, i) for i, im in zip (image_range, color_indv)]
    #print(len(color_anotate))
    rows = 2
    imgs_in_row = len(color_anotate)//rows
    list_of_points = [ ((r * imgs_in_row), ((r + 1) * imgs_in_row) )  for r in range(rows)]
    print(list_of_points)

    image_rows = [np.hstack(color_anotate[(r * imgs_in_row): ((r + 1) * imgs_in_row)]) for r in range(rows)]
    final = np.vstack(image_rows)
    skimage.io.imsave(os.path.join(this_dir, outimage + "_strip.png"), final)
    skimage.io.imsave(os.path.join(this_dir, outimage + "_strip.jpg"), final)
