
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import scipy.io
import scipy.stats
import glob
#import data.bio_film_data.strainmap as strainmaper
import skimage.io
from lib import figure_util
import matplotlib.gridspec as gs
import matplotlib as mpl
import os
import pandas as pd
import subfig_traces
import subfig_hists

figure_util.apply_style()

this_dir = os.path.dirname(__file__)

figall = plt.figure()

gridmain = gs.GridSpec(2, 1,
             height_ratios=[2.5, 4], hspace=0.05)
gridtracehist = gs.GridSpecFromSubplotSpec(4, 2,
                    width_ratios=[0.5, 0.5],
                    subplot_spec=gridmain[1,0], wspace=0.35)

aximg = plt.subplot(gridmain[0, 0:2])
#movie = skimage.io.imread("sigB_biofilmpad6-O001_3_1_strip.png")
movie = skimage.io.imread(os.path.join(this_dir, "sigB_biofilmfinal-B_4_movie_strip.png"))
aximg.imshow(movie, rasterized=True, interpolation="none")
aximg.grid(False)
aximg.axis('off')


axall = np.empty((4, 2), dtype=plt.Axes)
for r in range(0, 4): #grid.shape[0]-1):
    for c in range(0, 2): #grid.shape[1]):
        axall[r,c] = plt.subplot(gridtracehist[r,c])


# plots_st = [ ("WT",     "WT",  figure_util.strain_color["JLB021"], "R_cells" , 280)
#             ,("WT",     "WT",  figure_util.strain_color["JLB021"], "Y_cells", 180)
#             ,("ΔrsbRU", "DRU",  figure_util.strain_color["JLB088"], "Y_cells", 180)
#             ,("ΔrsbQP", "DQP",  figure_util.strain_color["JLB039"], "Y_cells", 180)]

histticker = mticker.MaxNLocator(nbins=4)

basedir = os.path.join(this_dir, "../../datasets/padmovies_brightfield/hists/")
bin_width = 10
nbins = np.arange(-10, 240, bin_width)
strains = [ ("wt",    "MR", "JLB021", 280, nbins),
            ("wt",    "MY", "JLB021", 280, nbins),
            ("delru", "MY", "JLB088", 280, nbins),
            ("delqp", "MY", "JLB039", 280, nbins)]    

for i, (filen, chan, strainnum, xmax, bins) in enumerate(strains):
    df = pd.read_csv(os.path.join(basedir, filen + ".tsv"), sep="\t", )
    h_style= {"width": ((nbins[1] - nbins[0]) ) * 0.8,
                "alpha":1.0,
                "color":figure_util.strain_color[strainnum]}
    strain = figure_util.strain_label[strainnum]
    print(strain)
    axall[i,1] = subfig_hists.get_figure(axall[i,1], df, chan, bins, h_style )
    axall[i,1].set_ylim(0, 30)
    axall[i,1].set_xlim(-10, xmax)

    reporter = "P$_{sigA}$-RFP" if chan == "MR" else "P$_{sigB}$-YFP"
    axall[i, 1].set_title("{0}: {1}".format(strain, reporter), y=0.6)
    axall[i, 1].yaxis.set_major_locator(histticker)
    yticks = axall[i, 1].yaxis.get_major_ticks()
    #yticks[-1].label1On=False
    #yticklabels[-1].visible = False
    #axall[i, 1].set_yticklabels([])

    if i in [1,2]:
        axall[i, 1].set_xticklabels([])



##################
## Traces 
##################
basedir = os.path.join(this_dir, "../../datasets/padmovies_brightfield/traces/")
frames = 21
strains = [ ("sigb",  "MR", "WT",     frames, [83, 134, 198, 112]),
            ("sigb",  "MY", "WT",     frames, [83, 134,112, 198]),
            ("delru", "MY", "ΔrsbRU", frames, [57, 74,  105, 101] ),
            ("delqp", "MY", "ΔrsbQP", frames, [91, 71, 89, 65])]

bg_style= {"linewidth":0.25, "alpha":0.4, "color":"gray", "label":'_nolegend_'}
hl_style= {"linewidth":1, "alpha":1.}

traceticker = mticker.MaxNLocator(nbins=2)

for i, (filen, chan, label, frames_include, hlcells) in enumerate(strains):
    df = pd.read_csv(os.path.join(basedir, filen + ".tsv"), sep="\t", )
    axall[i,0] = subfig_traces.get_figure(axall[i,0], df, chan, hlcells, frames_include, bg_style, hl_style )
    axall[i,0].set_ylim(0,235)
    axall[i,0].set_xlim(0,5.25)
    # title = "P$_{sigA}$-RFP" if chan == "R" else "P$_{sigB}$-YFP"
    # title = "P$_{sigA}$-RFP" if chan == "R" else "P$_{sigB}$-YFP"
    # axall[i, 0].set_title(label + " " + title, y=0.6)
    if i < 3:
        axall[i, 0].set_xticklabels([])
    axall[i, 0].yaxis.set_major_locator(traceticker)
    #ytticks = axall[i, 0].yaxis.get_major_ticks()
    #ytticks[-2].label1On=False

for a in axall.flatten():
    a.tick_params(axis="both", length=2, direction="out")
    
axall[-1, 0].set_xlabel("Time (hours)")
axall[-1, 1].set_xlabel("Fluorescence (AU)")
axall[1,0].annotate("Fluorescence (AU)", 
                 xy=(0,0),
                 xytext=(0.07, 0.35),  
                 xycoords='figure fraction',
                 textcoords='figure fraction',
                 horizontalalignment='center', verticalalignment='center',
                 rotation=90,
                 fontsize="medium", color=mpl.rcParams['axes.labelcolor']
                 )
axall[1, 1].set_ylabel("")
axall[1,1].annotate("Percentage total cells", 
                 xy=(0,0),
                 xytext=(-0.18, 0.0),  
                 xycoords='axes fraction',
                 textcoords='axes fraction',
                 horizontalalignment='center', verticalalignment='center',
                 rotation=90,
                 fontsize="medium", color=mpl.rcParams['axes.labelcolor']
                 )

letter_settings = { 
           "horizontalalignment": 'center',
           "verticalalignment": 'top',
           "fontsize": figure_util.letter_font_size, 
           "color": "black"}

x1 = 0.02
aximg.text(x1, 0.995, "B", transform=figall.transFigure, **letter_settings)
aximg.text(x1, 0.64, "C",  transform=figall.transFigure, **letter_settings)
aximg.text(x1, 0.50, "D",  transform=figall.transFigure, **letter_settings)
aximg.text(x1, 0.36, "E",  transform=figall.transFigure, **letter_settings)
aximg.text(x1, 0.22, "F",  transform=figall.transFigure, **letter_settings)

x2 = 0.53
aximg.text(x2, 0.64, "G",  transform=figall.transFigure, **letter_settings)
aximg.text(x2, 0.50, "H",  transform=figall.transFigure, **letter_settings)
aximg.text(x2, 0.36, "I",  transform=figall.transFigure, **letter_settings)
aximg.text(x2, 0.22, "J",  transform=figall.transFigure, **letter_settings)


filename = "pad_movie_tracemain"

width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.0)
figall.set_size_inches(width, height)
figall.subplots_adjust(left=0.15,
                       right=0.99,
                       top=1.0,
                       bottom=0.1) 
                       #hspace=0.05)

print("request size : ", figure_util.inch2cm((width, height)))
figure_util.save_figures(figall, filename, ["png", "pdf"], this_dir)
