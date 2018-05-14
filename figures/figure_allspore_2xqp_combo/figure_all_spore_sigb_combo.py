import pandas as pd
import numpy as np
import os.path
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_spoiid_vs_sigb_raw_cor
import subfig_sigb_grad
#import subfig_density_gradient
import subfig_spore_count_gradient
#import subfig_histograms
from figures.figure_63x_sigb_histo import subfig_indivfile_histo
import subfig_spoiid_image
import subfig_spore_image       
#import subfig_spoiid_vs_sigb_isolines             
from lib import strainmap

import lib.figure_util as figure_util
figure_util.apply_style()
from lib.figure_util import strain_color, strain_label
import matplotlib.ticker as mpt

fig = plt.figure()
#gs = gridspec.GridSpec(3, 4, width_ratio=[0])
gs = gridspec.GridSpec(3, 3, width_ratios=[0.3, 0.35, 0.35])

sbgrad_ax = plt.subplot(gs[1, 0])
spgrad_ax = plt.subplot(gs[0, 0])
corr_ax = plt.subplot(gs[2, 1])
spimg_ax = plt.subplot(gs[2, 2])
hist_ax = plt.subplot(gs[2, 0])
wtspr_ax = plt.subplot(gs[:2, 1])
x2spr_ax = plt.subplot(gs[:2, 2])

# sbgrad_ax = plt.subplot(gs[0, :2])
# spgrad_ax = plt.subplot(gs[1, :2])
# corr_ax = plt.subplot(gs[2, 2])
# spimg_ax = plt.subplot(gs[2, 3])
# hist_ax = plt.subplot(gs[2, 0:2])
# wtspr_ax = plt.subplot(gs[:2, 2])
# x2spr_ax = plt.subplot(gs[:2, 3])

########
## Spore spoiid correlation
########
this_dir = os.path.dirname(__file__)
basedir = os.path.join(this_dir, "../../datasets/LSM780_63x_spoiid_v_sigb/")
file_df = filedb.get_filedb(os.path.join(basedir, "filedb.tsv"))
print(file_df)
cell_df = pd.read_hdf(basedir + "rsiga_ysigb_cspoiid_redoedgedata.h5", "cells")
# Ignore first 2 um (only done for consistency)
cell_df = cell_df[cell_df["distance"] > 2].copy()

corr_ax, corr_cb = subfig_spoiid_vs_sigb_raw_cor.get_figure(corr_ax, file_df, cell_df)
#corr_ax, corr_cb, cont_cb = subfig_spoiid_vs_sigb_isolines.get_figure(corr_ax, file_df, cell_df)
cbar = fig.colorbar(corr_cb, ax=corr_ax)
#cbar.add_lines()#corr_cb)
cbar.ax.set_ylabel('Number of cells', rotation=270) 
print("orig pad  = ", cbar.ax.yaxis.labelpad)
cbar.ax.yaxis.labelpad = 10

###########
## 10x sigb grad
###########
tenx_basepath = os.path.join(this_dir, "../../datasets/LSM780_10x_sigb/")
tenx_gradient_df = pd.read_hdf(os.path.join(tenx_basepath, "gradient_data.h5"), "data")
#gradient_df["ratio"] = gradient_df["mean_green"]/gradient_df["mean_red"]
print(tenx_gradient_df.columns)
tenx_gradient_df["ratio"] = tenx_gradient_df["green_bg_mean"]/tenx_gradient_df["red_bg_mean"]
tenx_file_df = filedb.get_filedb(os.path.join(tenx_basepath, "filedb.tsv"))
sbgrad_ax = subfig_sigb_grad.get_figure(sbgrad_ax, tenx_file_df, tenx_gradient_df)


#######
# spore gradient
# #############
sspb_strains = [ (st, figure_util.strain_label[st]) for st in ['JLB077', 'JLB117', 'JLB118']]
spbase = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")
sp_grad_file = os.path.join(spbase, "spore_cell_counts.mat")
spfile_df = filedb.get_filedb(spbase + "file_list.tsv")
spgrad_ax = subfig_spore_count_gradient.get_figure(spgrad_ax, sp_grad_file, sspb_strains, "sporecounts" )
#spgrad_ax = subfig_density_gradient.get_figure(spgrad_ax, spdatadir, spfile_df, sspb_strains, "spore")
#spcount_ax = subfig_density_gradient.get_figure(spcount_ax, datadir, file_df, sspb_strains, "spore")
spgrad_ax.set_ylabel("Spore counts")
leg = spgrad_ax.legend(loc="upper right")
#spgrad_ax.set_ylim(0, 0.0003)
spgrad_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
spgrad_ax.set_xlim(0, 150)
spgrad_ax.set_ylim(0, 800)
spgrad_ax.set_xlabel("Distance from top of biofilm (μm)")


################
## Histogram
################
USE_CACHE_PLOTS = True
#USE_CACHE_PLOTS = False
histo_basedir = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/")
#histo_cell_df = pd.read_hdf(os.path.join(histo_basedir, "new_edge_bgsub_norm_lh1segment.h5"), "cells")
gchan = "green_raw_bg_meannorm"
rchan = "red_raw_bg_meannorm"
if not USE_CACHE_PLOTS:
    histo_cell_df = pd.read_hdf(os.path.join(histo_basedir, "single_cell_data.h5"), "cells")
    histo_file_df = filedb.get_filedb(os.path.join(histo_basedir, "file_list.tsv"))
    #histo_cell_df = histo_cell_df[(histo_cell_df["red_raw"] > 0)].copy()
    histo_cell_df = histo_cell_df[histo_cell_df[rchan] > 0].copy()
else: 
    histo_file_df = None
    histo_cell_df = None

max_val = 6.5 
gmax_val = 6.5
nbins = 150
rbins = (0, max_val, nbins)
gbins = (0, gmax_val, nbins)
percentile = 0
time = 48
location = "center"
strain_map, des_strain_map = strainmap.load()
slice_srt, slice_end = 5, 7 #10, 15/

list_of_histos = [ 
        ("wt_sigar_sigby", gchan, "{0} P$_{{sigB}}$-YFP".format(strain_label['JLB021']), strain_color["JLB021"]),
        ("2xqp_sigar_sigby", gchan, "{0} P$_{{sigB}}$-YFP".format(strain_label['JLB095']), strain_color["JLB095"])
]
#hist_ax = subfig_histograms.get_figure(hist_ax, histo_file_df, histo_cell_df)
for i, (strain, chan, label, color) in enumerate(list_of_histos):
    strain_df = None
    if not USE_CACHE_PLOTS:
        print(strain)
        fids = histo_file_df[(histo_file_df["time"] == time) &
                        (histo_file_df["location"] == location) &
                        (histo_file_df["strain"] == des_strain_map[strain])].index
        strain_df = histo_cell_df[histo_cell_df["global_file_id"].isin(fids)]

    dset = time, location, strain
    plot_args = {"color":color, "max_min": "std", "mode_mean": False}
    tbins = gbins
    if "red" in chan:
        tbins = rbins
    histo_dir = os.path.join(this_dir, "../figure_63x_sigb_histo/")
    args = (hist_ax, strain_df, chan, tbins, (slice_srt, slice_end), dset, percentile, USE_CACHE_PLOTS, histo_dir, plot_args)
    hist_ax, _, meandmed = subfig_indivfile_histo.get_figure(*args)

hist_ax.set_ylim(0, 4)
#leg = hist_ax.legend(loc="center right")
hist_ax.set_xlabel("Mean normalised cell fluoresence")
hist_ax.set_ylabel("Percentage of cells")


################
## SpoIID image
################
spoiid_base = os.path.join(this_dir, "../../proc_data/fp3_unmixing/rsiga_ysigb_cspoiid/")
spimg_ax = subfig_spoiid_image.get_figure(spimg_ax, spoiid_base, this_dir) 

########
## Spore images
########
sp_image_basedir = os.path.join(this_dir, "../../proc_data/spores_63xbig/")
files = [ {"Path": "Batch3/JLB077_48hrs_center_3_1.lsm", "x": 780 * 20, "y": 250 *20, 
        "cr_min":0, 
        "cr_max":10000, 
        "cg_min":2000,
        "cg_max":(2**14),
          },
          {"Path": "Batch1/JLB117_48hrs_center_4_1.lsm", "x" : 800*20, "y": 70*20,
        "cr_min":0, 
        "cr_max":30000, 
        "cg_min":2000,
        "cg_max":(2**15), }]
height = 260 * 20 
width = 500 * 20

for i, ax in zip(files, [wtspr_ax, x2spr_ax]):
    ax = subfig_spore_image.plot_big_image(ax,
                                           sp_image_basedir + i["Path"],
                                           this_dir,
                                           ((i["y"], i["y"] + height),
                                           (i["x"], i["x"] + width)), 
                                           (height, width),
                                           i)
letter_lab = (-0.14, 1.0)
axes = [spgrad_ax, sbgrad_ax, hist_ax, wtspr_ax, x2spr_ax, corr_ax, spimg_ax] 
for a, l in zip(axes, figure_util.letters):
    a.text(letter_lab[0], letter_lab[1], l, 
            verticalalignment="top",
            horizontalalignment="right",
           transform=a.transAxes, fontsize=figure_util.letter_font_size)
    a.yaxis.set_major_locator(mpt.MaxNLocator(nbins=4, prune='upper'))


# # remove the top tick label when the letter gets in the way
# for a in [sbgrad_ax, spgrad_ax]:
#     yticks = a.yaxis.get_minor_ticks()
#     #ticklabs = a.yaxis.get_ticklabels()
#     #ticklabs = a.get_yticks()#.tolist()
#     #ticklabs[-1] = ''
#     #a.set_yticklabels(ticklabs)
#     #print([ t.get_text() for t in ticklabs])
#     #ticklabs[-1].visible = False
#     #ticklabs[-1].label1On = False
#     yticks[-1].label1.set_visible(False)


filename = "spore_sigb_combo"
width, height = figure_util.get_figsize(figure_util.fig_width_big_pt, wf=1.0, hf=0.9 )
fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.06, hspace=0.25, wspace=0.25)
figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
