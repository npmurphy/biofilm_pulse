import os.path

import matplotlib.pyplot as plt
#from scipy.stats import skew
import numpy as np
import pandas as pd

import subfig_draw_bin
import subfig_indivfile_histo

import lib.filedb as filedb
from lib import strainmap

from lib import figure_util
 
figure_util.apply_style()



this_dir = os.path.dirname(__file__)

FP_max_min = [ (0,    30000), # RFP
               (1000, 11000) ] # YFP
#image_base_dir = "/Users/npm33/data/Microscopy/teamJL_2/Eugene/LSM700/"
image_base_dir = os.path.join(this_dir, "images/")
image_list = [ 
    ("WT P$_{sigA}$-RFP", 
    "SigB_48hrs_center_4_100615_sect_stitched.tiff",
    ((726, 726 + 500), (82,82+500)), # row, cols 
    [0]), # channels to include
    ("WT P$_{sigB}$-YFP",
    "SigB_48hrs_center_4_100615_sect_stitched.tiff",
    ((726, 726 + 500), (82,82+500)), # row, cols
    [0, 1]), # channels to include
    ("ΔrsbQP",
     "delQP_48hrs_center_2_100615_sect_stitched.tiff",
    ((1342,1342+500), (150,150+500)), # row, cols 
    [0, 1]), # channels to include
    ("ΔrsbRU", 
    "delRU_48hrs_center_3_100615_sect_stitched.tiff",
    ((678,678+500),(147,147+500)), # row, cols 
    [0, 1]) # channels to include
]

topletters = ["A", "B", "C", "D" ]
letters = ["E", "F", "G", "H" ]
imgletter_lab = (-0.1, 1.0)
hisletter_lab = (-0.16, 1.0)
letter_settings = { 
           "horizontalalignment": 'right',
           "verticalalignment": 'top',
           "fontsize": figure_util.letter_font_size, 
           "color": "black"}

#USE_CACHE_PLOTS = False 
USE_CACHE_PLOTS = True 

def main():

    basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb")

    if not USE_CACHE_PLOTS:
        cell_df = pd.read_hdf(os.path.join(basedir, "single_cell_data.h5"), "cells")
        print(cell_df.columns)
        file_df = filedb.get_filedb(os.path.join(basedir, "file_list.tsv"))
        # file_df.loc[file_df["time"] == 26.0, ['time']] = 24.0
        # file_df.loc[file_df["time"] == 38.0, ['time']] = 36.0
    else: 
        file_df = None
        cell_df = None

    time = 48
    location = "center"
    #slice_srt, slice_end = 5, 6 #10, 15 # 
    # There is no major difference between 5-6 and 7-8, just the QP skew is bigger in 5-6
    #slice_srt, slice_end = 7, 8 #10, 15
    # Moving to 2um because it makes the plots look nicer. 
    slice_srt, slice_end = 5, 7 #10, 15

    fig, ax = plt.subplots( 4, 2)
    axhisto = ax[:, 1]
    aximage = ax[:, 0]

    for i, (name, path, roi, chans) in enumerate(image_list):
        impath = os.path.join(image_base_dir, path)
        aximage[i] = subfig_draw_bin.get_figure(aximage[i], name, impath, roi,
                                                chans, FP_max_min, (slice_srt, slice_end), add_scale_bar=i==0)
        aximage[i].set_title("")
        aximage[i].text(imgletter_lab[0], imgletter_lab[1], topletters[i],
                         transform=aximage[i].transAxes, **letter_settings)

    text_x = 0.40
    text_top = 0.85
    line_sep = 0.15
    title_loc, cv_loc, samp_loc, cell_loc = [ (text_x, text_top-(line_sep*i)) for i in range(4)]

        
    strain_map, des_strain_map = strainmap.load()
    # gchan = "meannorm_green"
    # rchan = "meannorm_red"
    #gchan = "green_autobgbleed_maxnorm"
    #gchan = "green_autobg_maxnorm"
    #rchan = "red_autobg_maxnorm"
    gchan = "green_raw_bg_meannorm"
    rchan = "red_raw_bg_meannorm"
    if not USE_CACHE_PLOTS:
        cell_df = cell_df[cell_df[rchan] > 0].copy()

    #gchan = "ratio"
    #max_val = 30000
    #max_val = 1.0 #6.0 #20000
    #gmax_val = 1.0 #7.5 
    max_val = 6.5 #2.5 
    gmax_val = 6.5 #0.75
    nbins = 150
    rbins = (0, max_val, nbins)
    gbins = (0, gmax_val, nbins)
    percentile = 0#99
    list_of_histos = [ 
            ("wt_sigar_sigby", rchan,   "WT P$_{sigA}$-RFP",      figure_util.strain_color["JLB021"]),
            ("wt_sigar_sigby", gchan, "WT P$_{sigB}$-YFP",        figure_util.strain_color["JLB021"]),
            ("delqp_sigar_sigby", gchan, "ΔrsbQP P$_{sigB}$-YFP", figure_util.strain_color["JLB039"]),
            ("delru_sigar_sigby", gchan, "ΔrsbRU P$_{sigB}$-YFP", figure_util.strain_color["JLB088"])
    ]
    print("-----------")
    for i, (strain, chan, label, color) in enumerate(list_of_histos):
        print(label)
        strain_df = None
        if not USE_CACHE_PLOTS:
            fids = file_df[(file_df["time"] == time) &
                            (file_df["location"] == location) &
                            (file_df["strain"] == des_strain_map[strain])].index
            strain_df = cell_df[cell_df["global_file_id"].isin(fids)]
        
        dset = time, location, strain
        plot_args = {"color":color, "max_min":"std", "mode_mean": False}
        tbins = gbins
        if "red" in chan:
            tbins = rbins
        
        args = (axhisto[i], strain_df, chan, tbins, (slice_srt, slice_end), dset, percentile, USE_CACHE_PLOTS, this_dir, plot_args)
        axhisto[i], _, meandmed = subfig_indivfile_histo.get_figure(*args)
        axhisto[i].text(1.0, 1.0, label, 
                        horizontalalignment='right', 
                        verticalalignment='top',
                        color="black", 
                        fontsize=plt.rcParams["axes.titlesize"],
                        transform=axhisto[i].transAxes) 

        axhisto[i].text(hisletter_lab[0], hisletter_lab[1], letters[i],
                         transform=axhisto[i].transAxes, **letter_settings)

    #leg = axhisto[0].legend(loc="center right")
        
    axhisto[-1].set_xlabel("Mean normalised cell fluorecence")
    # if i > 1:
    #    axhisto[i].set_yticklabels([])

    for a in np.ravel(axhisto):
        a.set_ylabel("Percentage of cells")
        a.set_ylim(0, 5)
        a.set_xlim(0, gmax_val)
        a.tick_params(axis='x', which='both', direction='out')#, length=2, pad=0)
        a.tick_params(axis='y', which='both', direction='out')#, length=2, pad=0)

        
    axhisto[0].set_xlim(0, max_val)

    filename = "demo_longtail"
    fig.subplots_adjust(left=0.04, right=0.98, top = 0.98, bottom=0.05, hspace=0.20, wspace=0.2)
    width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.8)
    fig.set_size_inches(width, height)
    figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)



if __name__ == "__main__":
    main()

