
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rcParams
import numpy as np
import scipy.io
import scipy.stats
import glob
import data.bio_film_data.strainmap as strainmaper
import skimage.io
#import sys
import figure_util
import matplotlib.gridspec as gs

plt.style.use('../figstyle.mpl')

figall = plt.figure()

gridmain = gs.GridSpec(5, 3,
             width_ratios=[0.5, 0.25, 0.25],
             height_ratios=[3.5, 1, 1, 1, 1],
             left=0.05, right=0.98, wspace=0.45, hspace=0.15)

gridtraces = gs.GridSpecFromSubplotSpec(4, 1,
                subplot_spec=gridmain[1:5,0],
                wspace=0.0, hspace=0.3)

gridhist = gs.GridSpecFromSubplotSpec(4, 2,
                subplot_spec=gridmain[1:5,1:3],
                wspace=0.2, hspace=0.3)

aximg = plt.subplot(gridmain[0, 0:3])
#movie = skimage.io.imread("sigB_biofilmpad6-O001_3_1_strip.png")
movie = skimage.io.imread("sigB_biofilmfinal-B_4_strip.png")
aximg.imshow(movie, rasterized=True, interpolation="bicubic")
aximg.grid(False)
aximg.axis('off')


axall = np.empty((4, 3), dtype=plt.Axes)
for r in range(0, 4): #grid.shape[0]-1):
    #for c in range(0, 3): #grid.shape[1]):
        axall[r,0] = plt.subplot(gridtraces[r])

for r in range(0, 4): #grid.shape[0]-1):
    for c in range(1, 3): #grid.shape[1]):
        axall[r,c] = plt.subplot(gridhist[r, c-1])

plots_st = [ #("WT",     "WT",   R_cells", "#001C7F") # this is the sea born "dark" version of jlb021
             ("WT",     "WT",  figure_util.strain_color["JLB021"])
            ,("ΔrsbRU", "DRU",  figure_util.strain_color["JLB088"])
            ,("ΔrsbQP", "DQP",  figure_util.strain_color["JLB039"])
            ,("ΔsigB", "DSB",   figure_util.strain_color["JLB098"])]

def make_histogram(ax, dat_dict, chan, color):
    fp = dat[chan][0]
    fp = fp[~np.isnan(fp)]
    width = 10
    nbins = np.arange(-10, 240, width)
    bar_width = ((nbins[1] - nbins[0]) ) * 0.8
    counts, bins = np.histogram(fp, nbins)
    print("strain:", strain, chan,  "Skew:", scipy.stats.skew(fp))

    scaled = (counts / len(fp)) * 100
    ax.bar(bins[:-1], scaled, color=color, width=bar_width )
    return ax

minutes_per_frame = 15
letter_lab = (-0.14, 1.0)
axies_labels = [ ("B", "F", "J"), ("C", "G", "K"), ("D", "H", "L"), ("E", "I", "M") ]
histticker = mticker.MaxNLocator(nbins=4)

# Histograms 
for i, (strain, dat_file, color) in enumerate(plots_st):
    dat = scipy.io.loadmat("data/"+dat_file+".mat")
    ylim = 30
    xlim = 250

    for j, chan in enumerate(["R_cells", "Y_cells"]):
        make_histogram(axall[i, j+1], dat, chan, color)

        axall[i, j+1].set_ylim(0, ylim)
        axall[i, j+1].set_xlim(-10, xlim) #fpd.max() + xlim_buffer)
        reporter = "P$_{sigA}$-RFP" if chan == "R_cells" else "P$_{sigB}$-YFP"
        axall[i, j+1].set_title("{0}: {1}".format(strain, reporter), y=0.6)

    axall[i, 1].set_ylabel("% of cells")
    axall[i, 1].yaxis.set_major_locator(histticker)
    yticks = axall[i, 1].yaxis.get_major_ticks()
    yticks[-1].label1On=False
    #yticklabels[-1].visible = False
    axall[i, 2].set_yticklabels([])

    if i < 3:
        axall[i, 1].set_xticklabels([])
        axall[i, 2].set_xticklabels([])
    # texty = ylim * 0.8
    # textx = xlim * 0.05
    #axall[i].text(textx, texty, "{0}: {1}".format(strain, fname))
    #axall[i].set_xlabel("Mean Fluor. (AU)")
    # axall[i].xaxis.set_major_locator(xticks)
    # if i > 0:
    #     axall[i].set_yticklabels([])


tracestrains = [("WT", "wt", 10)
          ,("ΔrsbRU", "delru", 11)
          ,("ΔrsbQP", "delqp", 10)
          ,("Δσ^B", "delsigb", 10)]

traceticker = mticker.MaxNLocator(nbins=3)

for i, (strain, fname, xstart) in enumerate(tracestrains): 
    for df in glob.glob("data/" + fname + "_*.mat"):
        dat = scipy.io.loadmat(df)
        y = dat["yout"][0][0][0] 
        x = (dat["xout"][0][0][0].astype(float) * minutes_per_frame)/60
        xstarttime = (xstart*minutes_per_frame)/60
        axall[i, 0].plot(x, y, linewidth=1.0)

    for col in range(3):
        axall[i, col].text(letter_lab[0], letter_lab[1], axies_labels[i][col], transform=axall[i, col].transAxes, fontsize=8)

    axall[i, 0].set_xlim(left=xstarttime, right=10)
    axall[i, 0].set_ylim(0, 220)
    axall[i, 0].set_title("{0} P$_{{sigB}}$-YFP".format(strain.replace("^B", "B")), y=0.6)
    if i < 3:
        axall[i, 0].set_xticklabels([])
    axall[i, 0].yaxis.set_major_locator(traceticker)
    ytticks = axall[i, 0].yaxis.get_major_ticks()
    #ytticks[-2].label1On=False

    
    #ax.set_title("{0}".format(strain.replace("^B", "ᴮ")))
axall[-1, 0].set_xlabel("Time (hours)")
axall[-1, 1].set_xlabel("RFP fluorescence (AU)")
axall[-1, 2].set_xlabel("YFP fluorescence (AU)")
figall.text(-0.025, 0.45, 'Cell fluorecence (AU)', 
            horizontalalignment='center',
            rotation=90,
            color=rcParams["axes.labelcolor"],
            fontsize=rcParams["xtick.labelsize"])
aximg.text(-0.05, letter_lab[1], "A", transform=aximg.transAxes, fontsize=8)

filename = "pad_movie_sup"
width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=1.1)
figall.set_size_inches(width, height)# common.cm2inch(width, height))
print("request size : ", figure_util.inch2cm((width, height)))
figall.savefig(filename + ".png", dpi=300) 
figall.savefig(filename + ".pdf", dpi=300)
figall.clear()
plt.close(figall)
figure_util.print_pdf_size(filename + ".pdf")
