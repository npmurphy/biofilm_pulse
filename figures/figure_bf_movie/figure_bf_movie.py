import pandas as pd
import numpy as np
import os.path
import skimage.io
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import lib.filedb
import subfig_trace 
import subfig_gradient
#import data.bio_film_data.strainmap as strainmap

this_dir = os.path.dirname(__file__)
stylefile = os.path.join(this_dir, '../figstyle.mpl')
plt.style.use(stylefile)
import lib.figure_util as figure_util
from lib.figure_util import dpi, strain_color, strain_label

fig = plt.figure()
gs = gridspec.GridSpec(2, 2, width_ratios=[0.3, 0.7], height_ratios=[0.6, 0.4])

ax_exprmt = plt.subplot(gs[0, 0])
ax_fstrip = plt.subplot(gs[0, 1])
ax_gradnt = plt.subplot(gs[1, 0])
ax_pulses = plt.subplot(gs[1, 1])

################
## experiment figure
#################
ax_exprmt.spines['top'].set_visible(True)
ax_exprmt.spines['bottom'].set_visible(True)
ax_exprmt.spines['left'].set_visible(True)
ax_exprmt.spines['right'].set_visible(True)
ax_exprmt.axes.get_xaxis().set_ticks([])
ax_exprmt.axes.get_yaxis().set_ticks([])



# BF movie traces
base_dir =  "datasets/iphox_singlecell/BF10_timelapse/" 
movie = "Column_2"
comp_path  = os.path.join(base_dir, movie , "compiled.tsv")
ct_path = os.path.join(base_dir, movie , "cell_track.json")
compiled_trace, cell_tracks = subfig_trace.load_data(comp_path, ct_path)
compiled_trace["time"] = compiled_trace["time"]/60
ax_pulses = subfig_trace.get_figure(ax_pulses, compiled_trace, cell_tracks )

################
## Gradient 
###############
dataset_dir = "datasets/iphox_gradient_snaps/"
file_df = lib.filedb.get_filedb(dataset_dir + "filedb.tsv")
df = pd.read_hdf(dataset_dir + "gradient_data_distmap.h5")
#df["g_by_r"] = df["green_bg_mean"]/df["red_bg_mean"]
times = file_df["time"].unique()
#times = [24, 48, 72, 96]

plotset = {"linewidth":0.6, "alpha":0.3}
ax_gradnt = subfig_gradient.get_figure(ax_gradnt, df, file_df, "green_bg_mean", "", "", times, plotset)
ax_gradnt.legend()
ax_gradnt.set_xlim(0, 150) 
ax_gradnt.set_xlabel("Distance from air interface (μm)")
ax_gradnt.set_ylabel("YFP (AU)")

###################
## film strip
##################
im = skimage.io.imread(os.path.join(this_dir, "delru_bf10_col2_strip.png"))
ax_fstrip.imshow(im, 
        #interpolation="bicubic")
        interpolation="none")
    # aximg.text(0.9, 0.98, label, ha="right", va="top", 
    #             transform=aximg.transAxes, 
    #             fontsize=plt.rcParams["axes.titlesize"],
    #             color="white")
ax_fstrip.grid(False)
ax_fstrip.axis('off')
    # aximg.text(letter_lab[0], letter_lab[1], letters[i],
    #              transform=aximg.transAxes,
    #              verticalalignment="top",
    #              horizontalalignment="right",
    #              fontsize=figure_util.letter_font_size)


filename = os.path.join(this_dir, "bf_movie_main")
width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.5 )
fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.06, hspace=0.25, wspace=0.25)

fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.savefig(filename + ".png") #, bbox_inches="tight"  )
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".pdf") #, bbox_inches="tight"  )
figure_util.print_pdf_size(filename + ".pdf")