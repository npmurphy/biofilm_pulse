import os.path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import pandas as pd
import skimage.io

import sys 
print(sys.path)

import lib.strainmap as strainmap


#from figure_util import dpi
import lib.figure_util as figure_util
figure_util.apply_style()

strain_map, des_strain_map = strainmap.load()


letter_lab = (-0.08, 1.0)

fig = plt.figure()
grid = gs.GridSpec(2, 3, height_ratios=[3,1])
grid.update(left=0.1, right=0.98, bottom=0.1, top=0.99, hspace=0.04)
#grid.update(hspace=0.05)

this_dir = os.path.dirname(os.path.realpath(__file__))

strains = [figure_util.strain_label[s] for s in ["JLB021", "JLB088", "JLB039"]]
biofilm_images = [ "SigB_48hrs_center_1_1_100615_sect.jpg",
                   "delRU_48hrs_3_6_100615sect.jpg", 
                   "delQP_48hrs_2_5_100615_sect.jpg"]


letters = figure_util.letters
for i, (label, imgpath) in enumerate(zip(strains, biofilm_images)): 
    im = skimage.io.imread(os.path.join(this_dir, "images", imgpath))
    aximg = plt.subplot(grid[0, i])
    #label = figure_util.strain_label[des_strain_map[strain].upper()]
    aximg.imshow(im, 
        #interpolation="bicubic")
        interpolation="none")
    #aximg.set_title(label, transform=aximg.transAxes)
    aximg.text(0.9, 0.98, label, ha="right", va="top", 
                transform=aximg.transAxes, 
                fontsize=plt.rcParams["axes.titlesize"],
                color="white")
    aximg.grid(False)
    aximg.axis('off')
    aximg.text(letter_lab[0], letter_lab[1], letters[i],
                 transform=aximg.transAxes,
                 verticalalignment="top",
                 horizontalalignment="right",
                 fontsize=figure_util.letter_font_size)

ax = plt.subplot(grid[1,:])

data_plots = [ "wt_sigar_sigby","delru_sigar_sigby" ,"delqp_sigar_sigby" ]

for c, strain in enumerate(data_plots):
    dpath = "datasets/LSM780_10x_sigb/gradient_summary/{0}.tsv"
    df = pd.read_csv(dpath.format(strain), sep="\t")
    print(df.columns)
    color = figure_util.strain_color[des_strain_map[strain].upper()]
    label = figure_util.strain_label[des_strain_map[strain].upper()]
    ax.plot(df["distance"], df["mean"], color=color, label=label, linewidth=0.5)
    ax.fill_between(df["distance"], df["upsem"], df["downsem"], color=color, alpha=0.4 )

leg = ax.legend(loc="upper right")
leg.get_frame().set_alpha(1.0)
ax, leg = figure_util.shift_legend(ax, leg, yshift=0.06)

ax.set_ylim(0, 0.29)
ax.set_xlim(left=0, right=150)
ax.set_xlabel("Distance from top of biofilm (μm)")
ax.set_ylabel("YFP/RFP ratio")
ax.text(-0.03, letter_lab[1], letters[3], ha="right", va="top", transform=ax.transAxes, fontsize=figure_util.letter_font_size)

filename = os.path.join(this_dir, "fig_10x_grad")
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.0 )
fig.set_size_inches(width, height)
#fig.tight_layout()
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".png")
fig.savefig(filename + ".pdf") 
fig.clear()
plt.close(fig)
figure_util.print_pdf_size(filename + ".pdf")


