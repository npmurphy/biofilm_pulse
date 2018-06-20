import pandas as pd
#import numpy as np
import os.path
import skimage.io
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import lib.filedb
import subfig_trace 
import subfig_hist 
#import subfig_gradient
#import data.bio_film_data.strainmap as strainmap

this_dir = os.path.dirname(__file__)
stylefile = os.path.join(this_dir, '../figstyle.mpl')
plt.style.use(stylefile)
import lib.figure_util as figure_util
#from lib.figure_util import dpi, strain_color, strain_label

fig = plt.figure()

# Making less wide 
outer_gs = gridspec.GridSpec(2, 2, 
                             height_ratios=[1, 1],
                             #hspace=0.18, wspace=0.25,
                             width_ratios=[1.5, 1])
ax_rfpulses = plt.subplot(outer_gs[0, 0])
ax_yfpulses = plt.subplot(outer_gs[1, 0])
ax_rfhistos = plt.subplot(outer_gs[0, 1])
ax_yfhistos = plt.subplot(outer_gs[1, 1])



# BF movie traces
base_dir =  "datasets/iphox_singlecell/BF10_timelapse/" 
movie = "Column_2"
comp_path  = os.path.join(base_dir, movie , "compiled.tsv")
ct_path = os.path.join(base_dir, movie , "cell_track.json")
compiled_trace, cell_tracks = subfig_trace.load_data(comp_path, ct_path)
compiled_trace["red"] = compiled_trace["red"]/1000
compiled_trace["green"] = compiled_trace["green"]/1000
compiled_trace["time"] = compiled_trace["time"]/60 # hours
print(compiled_trace.columns)

ymax = 3.5
rmax = 6.0
plots = [("red", "P$_{sigA}$-RFP (AU)", rmax,  ax_rfpulses),
         ("green", "P$_{sigB}$-YFP (AU)", ymax, ax_yfpulses)
        ]
for chan, ylab, cmax, ax in plots: 
        ax = subfig_trace.get_figure(ax, compiled_trace, cell_tracks, chan)
        ax = subfig_trace.get_figure(ax, compiled_trace, cell_tracks, chan)
        ax.set_ylabel(ylab)
        ax.set_xlim(20, right=96)
        ax.set_ylim(bottom=0, ymax=cmax)

plots = [("red", "P$_{sigA}$-RFP (AU)", rmax, ax_rfhistos),
         ("green", "P$_{sigB}$-YFP (AU)",ymax, ax_yfhistos)
        ]
for chan, ylab, cmax, ax in plots: 
        ax = subfig_hist.get_figure(ax, compiled_trace, cell_tracks, chan)
        ax = subfig_hist.get_figure(ax, compiled_trace, cell_tracks, chan)
        ax.set_ylabel(ylab)
        ax.set_ylim(bottom=0, ymax=cmax)
        #ax.set_xlim(20, right=96)
        #ax.set_ylim(bottom=0)

# letter_x = 0.03 
# axes[0].text(letter_x, 0.995, "A", transform=fig.transFigure, **letter_style)
# axes[1].text(0.47,     0.995, "B", transform=fig.transFigure, **letter_style)
# axes[2].text(letter_x,  0.63, "C", transform=fig.transFigure, **letter_style)
# axes[3].text(letter_x,  0.26, "D", transform=fig.transFigure, **letter_style)


filename = "supfig_bfmovie_pulses"
#width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.5 )
width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=1.0 )
fig.subplots_adjust(left=0.085, right=0.97, top=0.97, bottom=0.06)#, hspace=0.25, wspace=0.25)

fig.set_size_inches(width, height)# common.cm2inch(width, height))
figure_util.save_figures(fig, filename, ["png", "pdf"], base_dir=this_dir )