import os
import os.path
import numpy as np

import skimage.io
import skimage.morphology




def bit16_to_bit8(im):
    imr = skimage.exposure.rescale_intensity(im[:,:,0], in_range=(0, 30000), out_range=(0,255)).astype(np.uint8)
    img = skimage.exposure.rescale_intensity(im[:,:,1], in_range=(0, 40000), out_range=(0,255)).astype(np.uint8)
    imb = skimage.exposure.rescale_intensity(im[:,:,2], in_range=(0, 6897), out_range=(0,255)).astype(np.uint8)
    imx = np.dstack([imr, img, imb]) #np.zeros_like(imr)])
    return imx

def get_image(image_pattern, frame, channels):
    images = [ skimage.io.imread(image_pattern.format(frame, ch)) for ch in channels ]
    #images = [ skimage.filters.gaussian(im, sigma=3, preserve_range=True).astype(np.uint16) for im in images]
    #images = [ skimage.filters.gaussian(im, sigma=3) for im in images]
    rescales = {
        "00": (0, 65520),
        "01": (0, 38000),
        "b": (0, 6897) }

    for ch, i in zip(channels, range(len(images))):
        images[i] = skimage.exposure.rescale_intensity(images[i],
                                                        in_range=rescales[ch], 
                                                        out_range=(0,255)).astype(np.uint8)

    if len(images) < 3:
        images += [np.zeros_like(images[0])]
    imx = np.dstack(images)
    return imx

def annotate_image(image, time): #, center, window):
    #center = tuple((int(c) for c in center))
    micro = 100
    # File claims 1.36 px to um scale. 
    # however, the microscope was broken and thought it was in 
    # 10x mode, not 20x. So I guess divide by 2? 
    scale = micro / (1.36 /2)
    legend = "{0} μm".format(micro)
    fontsize = 40
    small = figure_util.draw_scale_bar(image, 10, 10, scale, 20, legend, fontsize=fontsize)
    time_str = "{0:02d}:{1:02d}".format(int(time//60), int(time%60))
    small = figure_util.annotate_image(small, small.shape[0]-50, small.shape[1] - 120, time_str, fontsize=fontsize )
    return small


def make_movie(start, end, image_pattern, output_pattern, channels):

    for i in range(start, end):
        print("frame {0}".format(i))
        window = 150
        
        current_image = get_image(image_pattern, i, channels)
        small = current_image[:, 380:]
        time_offset = (12 * 60) + 3
        time = time_offset + (i * 10)
        annotated = annotate_image(small, time)
        
        skimage.io.imsave(output_pattern.format(i), annotated)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--image_pattern", type=str)
    parser.add_argument('-o', "--output_pattern", type=str)
    parser.add_argument('-s', "--start_frame", type=int)
    parser.add_argument('-e', "--end_frame", type=int)
    #parser.add_argument("--offset_time", type=str)
    parser.add_argument('--channels', nargs="+", type=str, default=["r", "g"])
    arguments = parser.parse_args()


    try:
        os.mkdir(os.path.dirname(arguments.output_pattern))
    except FileExistsError as e:
        pass

    make_movie(arguments.start_frame,
               arguments.end_frame,
               arguments.image_pattern,
               arguments.output_pattern,
               arguments.channels)


if __name__ == '__main__':
    main()
