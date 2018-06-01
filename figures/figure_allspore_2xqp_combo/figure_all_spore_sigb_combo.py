import pandas as pd
#import numpy as np
import os.path
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#import subfig_spoiid_vs_sigb_raw_cor
import subfig_sigb_grad
#import subfig_density_gradient
import subfig_spore_count_gradient
#import subfig_histograms
#from figures.figure_63x_sigb_histo import subfig_indivfile_histo
#import subfig_spoiid_image
import subfig_spore_image       
#import subfig_spoiid_vs_sigb_isolines             
#from lib import strainmap

import lib.figure_util as figure_util
figure_util.apply_style()
from lib.figure_util import strain_color, strain_label
import matplotlib.ticker as mpt

fig = plt.figure()
this_dir = os.path.dirname(__file__)

outer_gs = gridspec.GridSpec(2, 2, height_ratios=[.3, 1],
                            hspace=0.18, wspace=0.35,
                            width_ratios=[1, 1])

picts_gs  = gridspec.GridSpecFromSubplotSpec(2, 1, 
                                  height_ratios=[1,1],
                                  subplot_spec = outer_gs[1,:],
                                  hspace=0.03)



sbgrad_ax = plt.subplot(outer_gs[0, 1])
spgrad_ax = plt.subplot(outer_gs[0, 0])
wtspr_ax = plt.subplot(picts_gs[0, :])
x2spr_ax = plt.subplot(picts_gs[1, :])

###########
## 10x sigb grad
###########
tenx_basepath = os.path.join(this_dir, "../../datasets/LSM780_10x_sigb/")
tenx_gradient_df = pd.read_hdf(os.path.join(tenx_basepath, "gradient_data.h5"), "data")
#gradient_df["ratio"] = gradient_df["mean_green"]/gradient_df["mean_red"]
print(tenx_gradient_df.columns)
tenx_gradient_df["ratio"] = tenx_gradient_df["green_bg_mean"]/tenx_gradient_df["red_bg_mean"]
tenx_file_df = filedb.get_filedb(os.path.join(tenx_basepath, "filedb.tsv"))
sbgrad_ax = subfig_sigb_grad.get_figure(sbgrad_ax, tenx_file_df, tenx_gradient_df, ["wt_sigar_sigby","2xqp_sigar_sigby"])


#######
# spore gradient
# #############
sspb_strains = ['JLB077', 'JLB117'] #, 'JLB118']
spbase = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")

spfile_df = filedb.get_filedb(os.path.join(spbase,  "file_list.tsv"))
spfile_df = spfile_df[~((spfile_df["name"] == "JLB077_48hrs_center_1_1") & 
                        (spfile_df["dirname"] == "Batch1"))]
spindividual = pd.read_csv(os.path.join(spbase,"spore_cell_individual.tsv"), sep="\t",index_col="index" )

spchan = "fraction_spores"
#spchan = "area_norm_spore_counts"
for strain in sspb_strains: 
    spgrad_ax = subfig_spore_count_gradient.get_figure(spgrad_ax, spfile_df, spindividual, strain, spchan, 100)

#spgrad_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
spgrad_ax.set_ylim(0, 0.25)
spgrad_ax.set_ylabel("Spore/cell ratio")
leg = spgrad_ax.legend()



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

for a in [spgrad_ax, sbgrad_ax]:
    a.set_xlim(0,140)

for i, ax in zip(files, [wtspr_ax, x2spr_ax]):
    ax = subfig_spore_image.plot_big_image(ax,
                                           sp_image_basedir + i["Path"],
                                           this_dir,
                                           ((i["y"], i["y"] + height),
                                           (i["x"], i["x"] + width)), 
                                           (height, width),
                                           i,vertical=False)
letter_lab = (-0.14, 1.0)
axes = [spgrad_ax,sbgrad_ax, wtspr_ax, x2spr_ax]#, hist_ax, corr_ax, spimg_ax] 
for a, l in zip(axes, figure_util.letters):
    a.text(letter_lab[0], letter_lab[1], l, 
            verticalalignment="top",
            horizontalalignment="right",
           transform=a.transAxes, fontsize=figure_util.letter_font_size)
    a.yaxis.set_major_locator(mpt.MaxNLocator(nbins=4, prune='upper'))


filename = "spore_sigb_combo"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.3 )
fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.subplots_adjust(left=0.15, right=0.98, top=0.98, bottom=0.005)
#figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
figure_util.save_figures(fig, filename, ["png","pdf"], this_dir)
