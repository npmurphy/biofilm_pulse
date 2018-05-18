import pandas as pd
#import numpy as np
import os.path
import numpy as np
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_spoiid_vs_sigb_raw_cor
from figures.figure_allspore_2xqp_combo import subfig_sigb_grad
from figures.sup_63x_gradients import subfig_plot_grad_errors 
#import subfig_density_gradient
from figures.figure_allspore_2xqp_combo import subfig_spore_count_gradient
#import subfig_histograms
import subfig_spoiid_image
#import subfig_spoiid_vs_sigb_isolines             
#from lib import strainmap

import lib.figure_util as figure_util
figure_util.apply_style()
#from lib.figure_util import strain_color, strain_label
#import matplotlib.ticker as mpt

fig = plt.figure()
#fig, ax = plt.subplots(1,3)
gs = gridspec.GridSpec(2, 2, width_ratios=[1,0.8])
#gs = gridspec.GridSpec(3, 3, width_ratios=[0.3, 0.35, 0.35])

# spimg_ax = plt.subplot(ax[0])
# corr_ax = plt.subplot(ax[1])
# sb_grad_ax = plt.subplot(ax[2]) # also spores
spimg_ax = plt.subplot(gs[0, 0])
#corr_ax = plt.subplot(ax[1])
corr_ax = plt.subplot(gs[0, 1])
sb_grad_ax = plt.subplot(gs[1,:]) # also spores

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

# corr_ax, corr_cb = subfig_spoiid_vs_sigb_raw_cor.get_figure(corr_ax, file_df, cell_df)
# #corr_ax, corr_cb, cont_cb = subfig_spoiid_vs_sigb_isolines.get_figure(corr_ax, file_df, cell_df)
# cbar = fig.colorbar(corr_cb, ax=corr_ax)
# #cbar.add_lines()#corr_cb)
# cbar.ax.set_ylabel('Number of cells', rotation=270) 
# print("orig pad  = ", cbar.ax.yaxis.labelpad)
# cbar.ax.yaxis.labelpad = 10

#cfp_thresh = 3000
cfp_thresh = 2000
time = 48
location = "center"
fids = file_df[(file_df["time"] == time) & (file_df["location"] == location)].index
green_bins = np.linspace(0, 50000, 100)
green_x = green_bins[1:] - (green_bins[1] - green_bins[0])

timsct = cell_df[cell_df["global_file_id"].isin(fids)].copy()
timsct["one"] = 1
timsct["gthn"] = (timsct["mean_blue"] > cfp_thresh).values
counts = timsct.groupby(pd.cut(timsct["mean_green"], green_bins)).sum()
corr_ax.plot(green_x, counts["gthn"]/counts["one"], label=str(cfp_thresh))
corr_ax.set_xlim(green_bins[0], green_bins[-1])
corr_ax.set_ylabel("% of cells with P$_{spoIID}$-CFP over threshold")
corr_ax.set_xlabel("P$_{\sigma^B}$-YFP")
corr_ax.set_ylim(0, 1.0)

#plt.legend()


###########
## 10x sigb grad
###########
normalisation = [#("unnormed", (0, 8e3), "P$_{sigB}$-YFP (AU)"), 
                    ("ratio", (0, 1), "YFP/RFP Ratio")]
spec = "jlb021"
this_dir = os.path.join(os.path.dirname(__file__))
base = os.path.join(this_dir, "../../datasets/LSM700_63x_sigb/gradients")

plotset = {"linewidth":0.5, "alpha":0.3, "color":figure_util.green}
for n, (norm, ylim, ylabel) in enumerate(normalisation):
    args = (sb_grad_ax, base, norm, ylim, "quantile75", spec, [48], plotset)
    sb_grad_ax = subfig_plot_grad_errors.get_figure(*args)

# tenx_basepath = os.path.join(this_dir, "../../datasets/LSM780_10x_sigb/")
# tenx_gradient_df = pd.read_hdf(os.path.join(tenx_basepath, "gradient_data.h5"), "data")
# print(tenx_gradient_df.columns)
# tenx_gradient_df["ratio"] = tenx_gradient_df["green_bg_mean"]/tenx_gradient_df["red_bg_mean"]
# tenx_file_df = filedb.get_filedb(os.path.join(tenx_basepath, "filedb.tsv"))
# sb_grad_ax = subfig_sigb_grad.get_figure(sb_grad_ax, tenx_file_df, tenx_gradient_df, ["wt_sigar_sigby"])
sb_grad_ax.set_ylabel("YFP/RFP Ratio")
sb_grad_ax.set_ylim(0,0.4)
sb_grad_ax.set_xlim(0,140)
sp_grad_ax = sb_grad_ax.twinx()

sspb_strains = ['JLB077'] 
spbase = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")
spfile_df = filedb.get_filedb(os.path.join(spbase,  "file_list.tsv"))
spfile_df = spfile_df[~((spfile_df["name"] == "JLB077_48hrs_center_1_1") & 
                        (spfile_df["dirname"] == "Batch1"))]
spindividual = pd.read_csv(os.path.join(spbase,"spore_cell_individual.tsv"), sep="\t",index_col="index" )
spchan = "fraction_spores"
for strain in sspb_strains: 
    sb_grad_ax = subfig_spore_count_gradient.get_figure(sp_grad_ax, spfile_df, spindividual, strain, spchan, 100, {"color":figure_util.blue})
    
sb_grad_ax.set_xlabel("Distance from air interface (μm)")

#spgrad_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
#spgrad_ax.set_ylim(0, 0.25)
sp_grad_ax.set_ylabel("Spore/cell ratio")
#sb_grad_ax.set_ylabel("YFP/RFP")
leg = sp_grad_ax.legend()



################
## SpoIID image
################
spoiid_base = os.path.join(this_dir, "../../proc_data/fp3_unmixing/rsiga_ysigb_cspoiid/")
spimg_ax = subfig_spoiid_image.get_figure(spimg_ax, spoiid_base, this_dir) 



filename = "sigb_vs_spores"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.0 )
fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.subplots_adjust(left=0.10, right=0.9, top=0.98, bottom=0.1, hspace=0.35, wspace=0.2)
figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
