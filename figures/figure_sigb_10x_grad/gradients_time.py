from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import scipy.io
import os
from string import ascii_uppercase

from lib import strainmap
from lib import filedb
# from data.bio_film_data.sigb_sc_biofilm_slice_analysis.slice_histogram import *
# from data.bio_film_data.sigb_sc_biofilm_slice_analysis.sliding_windows import *
#plt.style.use('../figstyle.mpl')

from lib import figure_util
this_dir = os.path.dirname(__file__)
base = os.path.join(this_dir, "../../datasets/LSM780_10x_sigb/")
gradient_df = pd.read_hdf(base + "gradient_data.h5")
gradient_df["ratio"] = gradient_df["green_bg_mean"]/gradient_df["red_bg_mean"]


file_df = filedb.get_filedb(base + "filedb.tsv")

def get_strain(name, location, time):
    fids = file_df[(file_df["time"] == time) &
                   (file_df["location"] == location) &
                   (file_df["strain"] == des_strain_map[name])].index

    df = gradient_df[gradient_df["file_id"].isin(fids)]
    return df

strain_map, des_strain_map = strainmap.load()
print(des_strain_map)

fig, ax = plt.subplots(5, 2) #, sharex=True, sharey=True) 

# stp, width = 5, 1
# wt_sigby        jlb021
# delru_sigby     jlb088
# delqp_sigby     jlb039
# 2xqp_sigby      jlb095
# delsigb_sigby   jlb098
letters = np.array(list(ascii_uppercase[:5*2])).reshape((5,2))
letter_lab = (-0.13, 0.98)
plotticker = mticker.MaxNLocator(nbins=4)

for a in ax.flatten():
    #a.set_ylim(0, 0.6)
    a.set_xlim(left=0, right=150)

color_map = plt.get_cmap("rainbow")
for s, strain in enumerate(["wt_sigar_sigby","2xqp_sigar_sigby","delru_sigar_sigby" ,"delqp_sigar_sigby",  "delsigb_sigar_sigby"]): # ,"2xqp_sigby" ,"delsigb_sigby"]
    for l, location in enumerate(["center", "edge"]):
        for t, time in enumerate([24, 36, 48, 72, 96][::-1]):
            df = get_strain(strain, location, time)
            df = df[df["cdist"]>2.0]
            print(df.columns)
            chan = "green_raw_mean"
            df_mean = df.groupby("cdist").mean()
            df_sem = df.groupby("cdist").sem()
            #color = figure_settings.strain_color[des_strain_map[strain].upper()]
            label = figure_util.strain_label[des_strain_map[strain].upper()]
            tcolor = color_map(t/5)
            ax[s, l].set_title("{0} biofilm {1}".format(label, location), y=0.65)
            ax[s, l].plot(df_mean.index, df_mean[chan], color=tcolor, label="{0} hours".format(time))#/df["mean_red"])
            ax[s, l].fill_between(df_mean.index, df_mean[chan]-df_sem[chan],df_mean[chan]+df_sem[chan],color=tcolor, alpha=0.4 )#/df["mean_red"])
            ax[s, l].text(letter_lab[0], letter_lab[1], letters[s,l], transform=ax[s,l].transAxes, fontsize=8)
            #ax[s, l].yaxis.set_major_locator(plotticker)
            #yticks = ax[s, l].yaxis.get_major_ticks()
            #yticks[-1].label1On = False
            #yticks[-1].label2On=False

# Get the bounding box of the original legend
leg = ax[-1, -1].legend(loc="right", handlelength=1.0)
bb = leg.get_bbox_to_anchor().inverse_transformed(ax[-1,-1].transAxes)
print(bb)
# Change to location of the legend. 
x_shift = +0.1
bb.x0 += x_shift
bb.x1 += x_shift
print(bb)
leg.set_bbox_to_anchor(bb, transform = ax[-1,-1].transAxes)
leg.get_frame().set_alpha(1.0)


# top = ax[0,0].get_position().y1
# bottom = ax[-1,-1].get_position().y0
# left = ax[0,0].get_position().x0
# right = ax[-1,-1].get_position().x1

#print(fig.canvas.renderer)
#tick_label_top = min([a.xaxis.get_ticklabel_extents(fig.canvas.renderer)[0].inverse_transformed(fig.transFigure).y0 for a in ax[-1, :] ])
txt = ax[-1,-1].set_xlabel("invisibleinvisiblinvisiblinvisibleee")
txt = ax[-1,-1].set_xlabel(".", color="#FFFFFF") ## Forces mpl to give space for the fig label below. 

# failed attempts to get axis coords converted to figure coords. 
#print(ax[-1,-1].xaxis.get_label_coords())
#print(ax[-1,-1].xaxis.label.get_position())
# transform(fig.transFigure))
#print(txt.get_[0].inverse_transformed(fig.transFigure))

# a[-1,0].set_ylabel("Distance from air interface (μm)")
# label_space = rcParams["axes.labelpad"]
# a[-1,0].yaxis.set_label_coords(tick_label_left - 0.01, (left + right)/2, transform=fig.transFigure)
 
#label_position = fig.transFigure.inverted().transform(ax[-1,-1].xaxis.label.get_position())
#print(fig.transFigure.inverted().transform(ax[-1,-1].xaxis.label.get_position()))
fig.text(0.5, 0.009, "Distance from air interface (μm)",
        horizontalalignment='center',
        color=rcParams["axes.labelcolor"],
        fontsize=rcParams["xtick.labelsize"])

ax[2,0].set_ylabel("YFP/RFP ratio")

filename = "fig_10x_grad_all"

width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=1.0 )
fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.tight_layout()
print("request size : ", figure_util.inch2cm((width, height)))
figure_util.save_figures(fig, filename, ["pdf", "png"], this_dir)

