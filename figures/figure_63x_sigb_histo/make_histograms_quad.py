import os.path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

import subfig_draw_bin
#import subfig_indivfile_histo
import subfig_normalised_histos

import lib.filedb as filedb
from lib import strainmap

from lib import figure_util
from lib.figure_util import strain_color
 
figure_util.apply_style()


this_dir = os.path.dirname(__file__)

FP_max_min = [ (0,    30000), # RFP
               (1000, 11000) ] # YFP
image_base_dir = os.path.join(this_dir, "images/")
image_list = [ 
    # ("WT P$_{sigA}$-RFP", 
    # "SigB_48hrs_center_4_100615_sect_stitched.tiff",
    # ((726, 726 + 500), (72,72+500)), # row, cols 
    # [0]), # channels to include
    ("WT P$_{sigB}$-YFP",
    "SigB_48hrs_center_4_100615_sect_stitched.tiff",
    ((726, 726 + 500), (72,72+500)), # row, cols
    [0, 1]), # channels to include
    ("ΔrsbQP",
     "delQP_48hrs_center_2_100615_sect_stitched.tiff",
    ((1342,1342+500), (100,100+500)), # row, cols 
    [0, 1]), # channels to include
    ("ΔrsbRU", 
    "delRU_48hrs_center_3_100615_sect_stitched.tiff",
    ((678,678+500),(137,137+500)), # row, cols 
    [0, 1]) # channels to include
]

topletters = figure_util.letters[:3]
letters = figure_util.letters[3:3+3]
imgletter_lab = (-0.05, 0.97)
hisletter_lab = (-0.05, 0.97)
#hisletter_lab = (-0.16, 0.97)
letter_settings = { 
           "horizontalalignment": 'right',
           "verticalalignment": 'top',
           "fontsize": figure_util.letter_font_size}
label_settings = { 
           "horizontalalignment": 'left',
           "verticalalignment": 'bottom',
           "fontsize": figure_util.letter_font_size}

#USE_CACHE_PLOTS = False 
USE_CACHE_PLOTS = True 

def main():

    basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb")

    time = 48
    location = "center"
    #slice_srt, slice_end = 5, 7 #10, 15
    slice_srt_end = (5, 7)

    fig, ax = plt.subplots(2, 2)
    axhisto = ax[1,1]
    aximage = [ax[0,0], ax[0,1], ax[1,0]]

    for i, (name, path, roi, chans) in enumerate(image_list):
        impath = os.path.join(image_base_dir, path)
        aximage[i] = subfig_draw_bin.get_figure(aximage[i], name, impath, roi,
                                                chans, FP_max_min, slice_srt_end, add_scale_bar=i==0)
        aximage[i].set_title("")
        aximage[i].text(imgletter_lab[0], imgletter_lab[1], topletters[i],
                         transform=aximage[i].transAxes, **letter_settings)#, color="white")
        aximage[i].text(0.05, 0.05, name,
                         transform=aximage[i].transAxes, **label_settings, color="white")


    ##################### 
    ## Histograms 
    generate_data_subset = False

    strain_map, des_strain_map = strainmap.load()

    file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
    cachedpath = os.path.join(basedir, "histo_tops_normed.h5")
    

    gchan = "green_raw_bg_mean"
    rchan = "red_raw_bg_mean"
    nbins = 150
    gmax = 1
    gbins = np.linspace(0, gmax, nbins)

    list_of_histos = [ 
            #("2xqp_sigar_sigby",  gchan, rchan, gbins, slice_srt_end, "2xQP", strain_color["JLB095"]),
            ("wt_sigar_sigby",    gchan, rchan, gbins, slice_srt_end, "WT P$_{sigB}$-YFP", strain_color["JLB021"]),
            ("delqp_sigar_sigby", gchan, rchan, gbins, slice_srt_end, "ΔrsbQP P$_{sigB}$-YFP", strain_color["JLB039"]),
            ("delru_sigar_sigby", gchan, rchan, gbins, slice_srt_end, "ΔrsbRU P$_{sigB}$-YFP", strain_color["JLB088"])]
    axes = [axhisto] *len(list_of_histos)
    if generate_data_subset :
        df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
        cellsdf = subfig_normalised_histos.get_data_subset(df, file_df, list_of_histos, time, location, cachedpath)
    else:  
        cellsdf = pd.read_hdf(cachedpath, "cells")

    axes = subfig_normalised_histos.get_figure(cellsdf, file_df, axes, time, location, list_of_histos)
    axes[0].legend()


    axhisto.text(hisletter_lab[0], hisletter_lab[1], letters[0],
                    transform=axhisto.transAxes, **letter_settings)

        
    axhisto.set_ylabel("Percentage of cells")
    
    axhisto.set_xlim(0, gmax)
    axhisto.set_ylim(0, 8.5)
    axhisto.tick_params(axis='x', which='both', direction='out')#, length=2, pad=0)
    axhisto.tick_params(axis='y', which='both', direction='out')#, length=2, pad=0)
    axhisto.yaxis.set_major_locator(mticker.MaxNLocator(nbins=3, integer=True))
    axhisto.set_xlabel("Normalised cell fluorecence")
        

    filename = "demo_longtail"
    fig.subplots_adjust(left=0.05, right=0.95, top = 0.99, bottom=0.1, hspace=0.08, wspace=0.20)
    width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.9)
    fig.set_size_inches(width, height)
    figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)



if __name__ == "__main__":
    main()

