import os.path
import lib.filedb
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
import subfig_spore_count_gradient
#import subfig_spore_image       

import lib.figure_util 
lib.figure_util.apply_style()

fig, cellcount_ax = plt.subplots(1,1)

#fig = plt.figure()
#gs = gridspec.GridSpec(3, 1, height_ratios=[0.4, 0.3, 0.3])
# spimg_ax = plt.subplot(gs[0])s
# spcount_ax = plt.subplot(gs[1])
# cellcount_ax = plt.subplot(gs[2])

ylabel_cord = (-0.07, 0.5)

sspb_strains = [ (st, lib.figure_util.strain_label[st]) for st in ['JLB077', 'JLB117', 'JLB118']]

this_dir = os.path.dirname(__file__)
base = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")
cachefile = os.path.join(base, "spore_cell_counts.mat")
# datadir = os.path.join(base, "kd_spore_cell")
# file_df = lib.filedb.get_filedb(base + "file_list.tsv")

##
#spimg_ax = subfig_spore_count_gradient.get_figure(spimg_ax, cachefile,  sspb_strains, "totalcounts")
#spimg_ax.set_ylabel("Total biofilm mass")
##spcount_ax.set_ylim(0, 0.0003)
#spimg_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
#spimg_ax.get_yaxis().set_label_coords(*ylabel_cord)

###########
## Spore density
#spcount_ax = subfig_cell_count_gradient.get_figure(spcount_ax, datadir, file_df, sspb_strains, "spore")

#spcount_ax = subfig_spore_count_gradient.get_figure(spcount_ax,cachefile,  sspb_strains, "sporecounts")
#spcount_ax.set_ylabel("Spore counts")
##spcount_ax.set_ylim(0, 0.0003)
#spcount_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
#spcount_ax.get_yaxis().set_label_coords(*ylabel_cord)
#leg = spcount_ax.legend()

###########
## cell density
#cellcount_ax = subfig_cell_count_gradient.get_figure(cellcount_ax, datadir, file_df, sspb_strains, "cell")
cellcount_ax = subfig_spore_count_gradient.get_figure(cellcount_ax, cachefile, sspb_strains, "cellcounts") 
cellcount_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
cellcount_ax.get_yaxis().set_label_coords(*ylabel_cord)
#cellcount_ax.set_ylim(0, 0.00175)
cellcount_ax.set_ylabel("Cell counts")
cellcount_ax.set_xlabel("Distance from top of biofilm (μm)")
leg = cellcount_ax.legend()
cellcount_ax.set_xlim(0, 140)

# for a in [spcount_ax, cellcount_ax]:
#     a.set_xlim(0, 140)

########
## Spore image
########
# sp_image_basedir = "../../data/bio_film_data/data_local_cache/spores_63xbig/"

# files = [{"Path": "Batch3/JLB118_48hrs_center_7_1.lsm", "x": 1832 * 20, "y": 227 *20, 
#         "cr_min":0, 
#         "cr_max":10000, 
#         "cg_min":2000,
#         "cg_max":(2**14), }]
# height = 260 * 20 
# width = 700 * 20
# i = files[0]
# spimg_ax = subfig_spore_image.plot_big_image(spimg_ax,
#                                         sp_image_basedir + i["Path"],
#                                         ((i["y"], i["y"] + height),
#                                         (i["x"], i["x"] + width)), 
#                                         (height, width),
#                                         i, vertical=False, scalebar=True)
# letter_lab = (-0.10, 0.98)
# for l, a in zip(lib.figure_util.letters, [spimg_ax, spcount_ax, cellcount_ax]):
#     a.text(letter_lab[0], letter_lab[1], l, transform=a.transAxes, fontsize=lib.figure_util.letter_font_size)

#filename = "spore_count_compare"
filename = "spore_grad_compare"
width, height = lib.figure_util.get_figsize(lib.figure_util.fig_width_small_pt, wf=1.0, hf=0.4 )
fig.subplots_adjust(left=0.1, right=0.95, top=0.98, bottom=0.09, hspace=0.35) #, wspace=0.25)
fig.set_size_inches(width, height)

lib.figure_util.save_figures(fig, filename, ["png", "pdf"], os.path.dirname(__file__))
# print("request size : ", figure_util.inch2cm((width, height)))
# fig.savefig(filename + ".png", dpi=dpi) 
# fig.savefig(filename + ".pdf", dpi=dpi) 
# figure_util.print_pdf_size(filename + ".pdf")