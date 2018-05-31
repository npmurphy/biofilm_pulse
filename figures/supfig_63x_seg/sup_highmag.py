import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import subfig_cell_seg
import subfig_spore_seg
from figures.figure_sigb_10x_grad import subfig_bfmask
import os.path

this_dir = os.path.dirname(__file__)
plt.style.use(os.path.join(this_dir, '../../figures/figstyle.mpl'))

import lib.figure_util as figure_util
from lib.figure_util import dpi

fig = plt.figure() 
grid = gridspec.GridSpec(2, 2) # height_ratios=[3,1])

bigi_ax = plt.subplot(grid[0, :])
cell_ax = plt.subplot(grid[1, 0])
spor_ax = plt.subplot(grid[1, 1])

tenx_image = os.path.join(this_dir, "../figure_sigb_10x_grad/images")
datapath_orig = os.path.join(this_dir, "../../proc_data/")
bigi_ax = subfig_bfmask.get_figure(bigi_ax, tenx_image, datapath_orig )
cell_ax = subfig_cell_seg.get_figure(cell_ax, datapath_orig)
spor_ax = subfig_spore_seg.get_figure(spor_ax, "../figure_allspore_2xqp_combo/")

letter_lab = (-0.10, 0.98)
#for a, l in zip(axes, letters):
bigi_ax.text(letter_lab[0]/2.1, letter_lab[1], "A", transform=bigi_ax.transAxes, fontsize=figure_util.letter_font_size)
cell_ax.text(letter_lab[0], letter_lab[1], "B", transform=cell_ax.transAxes, fontsize=figure_util.letter_font_size)
spor_ax.text(letter_lab[0], letter_lab[1], "C", transform=spor_ax.transAxes, fontsize=figure_util.letter_font_size)
bigi_ax.set_title("Biofilm segmentation")
spor_ax.set_title("Single spore segmentation")
cell_ax.set_title("Single cell segmentation")

filename = "sup_cell_spore_segment"
width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=0.8)
fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.03, hspace=0.15, wspace=0.15)

print("request size : ", figure_util.inch2cm((width, height)))
figure_util.save_figures(fig, filename, ["pdf", "png"], figure_util.dpi)
