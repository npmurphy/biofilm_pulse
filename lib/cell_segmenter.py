import numpy as np
import skimage.filters
import skimage.exposure
import skimage.filters.rank
import skimage.morphology
import scipy.ndimage

# first version of laphat segment
def laphat_segment_v0(img, cell_width_pixels=11):
    img_gauss = skimage.filters.gaussian(img, 2)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))

    cell_disc = skimage.morphology.disk(cell_width_pixels/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)

    # This attempts to remove noise.
    diffg = skimage.filters.rank.gradient((img_gauss_01*255).astype(np.uint8), selem=cell_disc)

    img_lap = skimage.filters.laplace(img_gauss, ksize=3)
    hat_lap = (img_hat > 0) & (img_lap > 0) & (diffg > 3)

    scell_width = max(3, cell_width_pixels - 5)
    scell_disc = skimage.morphology.disk(scell_width/2)
    scell_disc_area = np.count_nonzero(scell_disc)

    count_pixels = skimage.filters.rank.sum(hat_lap.astype(np.uint8), scell_disc)
    cell_bones = count_pixels == scell_disc_area
    # grow a small bit, then label
    cell_segflesh = skimage.morphology.binary_dilation(cell_bones, selem=scell_disc)
    cell_labels, _ = scipy.ndimage.label(cell_segflesh)
    # label the bones
    cell_lab_bones = cell_bones * cell_labels

    # grow with full sized cells
    cell_labeled = skimage.morphology.dilation(cell_lab_bones, selem=cell_disc)
    return cell_labeled

"""
The small cells flag is used when cells are small (width about 5)
as in the case of the LSM780 63x. 
The bones are too small to label with so we grow back after erosion 
and then label
"""
def laphat_segment_v1(img, cell_width_pixels=12, blur=2, noisethresh=3, small_cells=False, small_cell_disc=2):
    img_gauss = skimage.filters.gaussian(img, blur)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))

    cell_disc = skimage.morphology.disk(cell_width_pixels/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)

    # This attempts to remove noise.
    diffg = skimage.filters.rank.gradient((img_gauss_01*255).astype(np.uint8), selem=cell_disc)

    img_lap = skimage.filters.laplace(img_gauss, ksize=3)
    hat_lap = (img_hat > 0) & (img_lap > 0) & (diffg > noisethresh)

    scell_width = max(small_cell_disc, cell_width_pixels - 4)
    scell_disc = skimage.morphology.disk(scell_width/2)
    scell_disc_area = np.count_nonzero(scell_disc)

    count_pixels = skimage.filters.rank.sum(hat_lap.astype(np.uint8), scell_disc)
    cell_bones = count_pixels == scell_disc_area
    # grow a small bit, then label
    cell_segflesh = skimage.morphology.binary_dilation(cell_bones, selem=scell_disc)
    if small_cells:
        ## Extra grow before labeling
        cell_segflesh = skimage.morphology.binary_dilation(cell_segflesh,
                                                           selem=skimage.morphology.disk(2))
    else:                                                     
        ## this is the difference. its supposed to break up weakly connected T junctions or L junctions
        cell_segflesh = skimage.morphology.binary_erosion(cell_segflesh,
                                                      selem=skimage.morphology.disk(2))

    cell_labels, _ = scipy.ndimage.label(cell_segflesh)
    # label the bones
    cell_lab_bones = cell_bones * cell_labels

    # grow with full sized cells
    cell_labeled = skimage.morphology.dilation(cell_lab_bones, selem=cell_disc)
    return cell_labeled

def laphat_segment_vsp81off(img, cell_width_pixels=12, blur=2, noisethresh=3, small_cell_disc=2):
    img_gauss = skimage.filters.gaussian(img, blur)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))

    cell_disc = skimage.morphology.disk(cell_width_pixels/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)

    # This attempts to remove noise.
    diffg = skimage.filters.rank.gradient((img_gauss_01*255).astype(np.uint8), selem=cell_disc)

    img_lap = skimage.filters.laplace(img_gauss, ksize=10)
    hat_lap = (img_hat > 0) & (img_lap > 0) & (diffg > noisethresh)

    scell_width = max(small_cell_disc, cell_width_pixels - 4)
    scell_disc = skimage.morphology.disk(scell_width/2)
    scell_disc_area = np.count_nonzero(scell_disc)

    count_pixels = skimage.filters.rank.sum(hat_lap.astype(np.uint8), scell_disc)
    cell_bones = count_pixels == scell_disc_area
    # grow a small bit, then label
    cell_segflesh = skimage.morphology.binary_dilation(cell_bones, selem=scell_disc)

    cell_labels, _ = scipy.ndimage.label(cell_segflesh)
    # label the bones
    cell_lab_bones = cell_bones * cell_labels

    # grow with full sized cells
    cell_labeled = skimage.morphology.dilation(cell_lab_bones, selem=cell_disc)
    return cell_labeled


def laphat_segment_v1_view(img, cell_width_pixels=11):
    img_gauss = skimage.filters.gaussian(img, 2)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))

    cell_disc = skimage.morphology.disk(cell_width_pixels/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)

    # This attempts to remove noise.
    diffg = skimage.filters.rank.gradient((img_gauss_01*255).astype(np.uint8), selem=cell_disc)

    img_lap = skimage.filters.laplace(img_gauss, ksize=10)
    img_lap[img_lap < 0] = 0 
    #hat_lap = (img_hat > 0) & (img_lap > 0) & (diffg > 3)

    scell_width = max(3, cell_width_pixels - 4)
    scell_disc = skimage.morphology.disk(scell_width/2)
    scell_disc_area = np.count_nonzero(scell_disc)

    #count_pixels = skimage.filters.rank.sum(hat_lap.astype(np.uint8), scell_disc)

    img_hat_01 = skimage.exposure.rescale_intensity(img_hat, out_range=(0, 1.0))
    img_lap_01 = skimage.exposure.rescale_intensity(img_lap, out_range=(0, 1.0))
    returnv = np.dstack([img_hat_01, img_lap_01, img_gauss_01])
    print(returnv.dtype)
    return returnv

def view_outline(segment):
    eroded = skimage.morphology.disk(1)
    cell_erode = skimage.morphology.erosion(segment, selem=eroded)
    return segment-cell_erode 