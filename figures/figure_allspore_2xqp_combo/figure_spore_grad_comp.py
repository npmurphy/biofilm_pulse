import os.path
import lib.filedb as filedb
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_density_gradient
import subfig_spore_image       

import lib.figure_util as figure_util
figure_util.apply_style()
#from figure_util import dpi

#fig = plt.figure()
# gs = gridspec.GridSpec(3, 1, height_ratios=[0.4, 0.3, 0.3])

# spimg_ax = plt.subplot(gs[0])
# spcount_ax = plt.subplot(gs[1])
# cellcount_ax = plt.subplot(gs[2])
fig, ax = plt.subplots(2,1)

spcount_ax = ax[0]
cellcount_ax = ax[1]

ylabel_cord = (-0.07, 0.5)

sspb_strains = [ (st, figure_util.strain_label[st]) for st in ['JLB077', 'JLB117', 'JLB118']]

this_dir = os.path.dirname(__file__)
base = os.path.join(this_dir, "../../datasets/LSM700_63x_sspb_giant/")
datadir = os.path.join(base, "kd_spore_cell")
file_df = filedb.get_filedb(base + "file_list.tsv")

###########
## Spore density
spcount_ax = subfig_density_gradient.get_figure(spcount_ax, datadir, file_df, sspb_strains, "spore")
spcount_ax.set_ylabel("Spore density")
spcount_ax.set_ylim(0, 0.0003)
spcount_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
spcount_ax.get_yaxis().set_label_coords(*ylabel_cord)
leg = spcount_ax.legend()

###########
## cell density
cellcount_ax = subfig_density_gradient.get_figure(cellcount_ax, datadir, file_df, sspb_strains, "cell")
cellcount_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
cellcount_ax.get_yaxis().set_label_coords(*ylabel_cord)
cellcount_ax.set_ylim(0, 0.00175)
cellcount_ax.set_ylabel("Cell density")
cellcount_ax.set_xlabel("Distance from top of biofilm (μm)")

for a in [spcount_ax, cellcount_ax]:
    a.set_xlim(0, 140)

########
## Spore image
########
# sp_image_basedir = os.path.join(this_dir, "../../proc_data/spores_63xbig/")

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
#                                         this_dir, # cache path.
#                                         ((i["y"], i["y"] + height),
#                                         (i["x"], i["x"] + width)), 
#                                         (height, width),
#                                         i, vertical=False, scalebar=True)
# letter_lab = (-0.10, 0.98)
# for l, a in zip(figure_util.letters, [spimg_ax, spcount_ax, cellcount_ax]):
#     a.text(letter_lab[0], letter_lab[1], l, transform=a.transAxes, fontsize=figure_util.letter_font_size)

filename = "spore_grad_density_compare"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.1 )
fig.subplots_adjust(left=0.1, right=0.95, top=0.98, bottom=0.09, hspace=0.35) #, wspace=0.25)

fig.set_size_inches(width, height)
figure_util.save_figures(fig, filename, ["pdf", "png"], os.path.dirname(__file__) )
# print("request size : ", figure_util.inch2cm((width, height)))
# fig.savefig(filename + ".png", dpi=dpi) 
# fig.savefig(filename + ".pdf", dpi=dpi) 
# figure_util.print_pdf_size(filename + ".pdf")