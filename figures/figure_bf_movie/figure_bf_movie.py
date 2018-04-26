import pandas as pd
import numpy as np
import os.path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_trace 
#import data.bio_film_data.strainmap as strainmap

this_dir = os.path.dirname(__file__)
stylefile = os.path.join(this_dir, '../figstyle.mpl')
plt.style.use(stylefile)
import lib.figure_util as figure_util
from lib.figure_util import dpi, strain_color, strain_label

fig = plt.figure()
gs = gridspec.GridSpec(2, 2, width_ratios=[0.5, 0.5])

ax_exprmt = plt.subplot(gs[0, 0])
ax_fstrip = plt.subplot(gs[0, 1])
ax_gradnt = plt.subplot(gs[1, 0])
ax_pulses = plt.subplot(gs[1, 1])


# BF movie traces
base_dir =  "proc_data/iphox_movies/BF10_timelapse/" 
movie = "Column_2"
comp_path  = os.path.join(base_dir, movie , "compiled.tsv")
ct_path = os.path.join(base_dir, movie , "cell_track.json")
compiled_trace, cell_tracks = subfig_trace.load_data(comp_path, ct_path)
compiled_trace["time"] = compiled_trace["time"]/60
ax_pulses = subfig_trace.get_figure(ax_pulses, compiled_trace, cell_tracks )



filename = os.path.join(this_dir, "bf_movie_main")
width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.9 )
fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.06, hspace=0.25, wspace=0.25)

fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.savefig(filename + ".png") #, bbox_inches="tight"  )
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".pdf") #, bbox_inches="tight"  )
figure_util.print_pdf_size(filename + ".pdf")