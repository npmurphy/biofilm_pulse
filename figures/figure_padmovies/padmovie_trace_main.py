
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import scipy.io
import scipy.stats
import glob
#import data.bio_film_data.strainmap as strainmaper
import skimage.io
from lib import figure_util
import matplotlib.gridspec as gs
import matplotlib as mpl
import os

figure_util.apply_style()

this_dir = os.path.dirname(__file__)

figall = plt.figure()

gridmain = gs.GridSpec(5, 2,
             height_ratios=[3.5, 1, 1, 1, 1])
gridtracehist = gs.GridSpecFromSubplotSpec(4, 2,
                    width_ratios=[0.5, 0.5],
                    subplot_spec=gridmain[1:5,0:2], wspace=0.35)

aximg = plt.subplot(gridmain[0, 0:2])
#movie = skimage.io.imread("sigB_biofilmpad6-O001_3_1_strip.png")
movie = skimage.io.imread(os.path.join(this_dir, "sigB_biofilmfinal-B_4_strip.png"))
aximg.imshow(movie, rasterized=True, interpolation="none")
aximg.grid(False)
aximg.axis('off')


axall = np.empty((4, 2), dtype=plt.Axes)
for r in range(0, 4): #grid.shape[0]-1):
    for c in range(0, 2): #grid.shape[1]):
        axall[r,c] = plt.subplot(gridtracehist[r,c])


plots_st = [ ("WT",     "WT",  figure_util.strain_color["JLB021"], "R_cells" , 280)
            ,("WT",     "WT",  figure_util.strain_color["JLB021"], "Y_cells", 180)
            ,("ΔrsbRU", "DRU",  figure_util.strain_color["JLB088"], "Y_cells", 180)
            ,("ΔrsbQP", "DQP",  figure_util.strain_color["JLB039"], "Y_cells", 180)]

#,("ΔsigB", "DSB",   figure_settings.strain_color["JLB098"])]

def make_histogram(ax, dat_dict, chan, color):
    fp = dat[chan][0]
    fp = fp[~np.isnan(fp)]
    width = 10
    nbins = np.arange(-10, 240, width)
    bar_width = ((nbins[1] - nbins[0]) ) * 0.8
    counts, bins = np.histogram(fp, nbins)
    print("strain:", strain, chan,  "Skew:", scipy.stats.skew(fp), "CV:", scipy.stats.variation(fp), "mean", fp.mean())

    scaled = (counts / len(fp)) * 100
    ax.bar(bins[:-1], scaled, color=color, width=bar_width )
    return ax


minutes_per_frame = 15
histticker = mticker.MaxNLocator(nbins=4)

# Histograms 
for i, (strain, dat_file, color, chan, xlim) in enumerate(plots_st):
    dat = scipy.io.loadmat(os.path.join(this_dir, "data", dat_file+".mat"))
    ylim = 30

    #for j, chan in enumerate(["R_cells", "Y_cells"]):
    make_histogram(axall[i, 1], dat, chan, color)

    axall[i, 1].set_ylim(0, ylim)
    axall[i, 1].set_xlim(-10, xlim) #fpd.max() + xlim_buffer)
    reporter = "P$_{sigA}$-RFP" if chan == "R_cells" else "P$_{sigB}$-YFP"
    axall[i, 1].set_title("{0}: {1}".format(strain, reporter), y=0.6)

    #axall[i, 1].set_ylabel("% of cells")
    axall[i, 1].yaxis.set_major_locator(histticker)
    yticks = axall[i, 1].yaxis.get_major_ticks()
    #yticks[-1].label1On=False
    #yticklabels[-1].visible = False
    #axall[i, 1].set_yticklabels([])

    if i < 3:
        axall[i, 1].set_xticklabels([])


tracestrains = [ ("WT", "wt", 10, "R")
                ,("WT", "wt", 10, "Y")
                ,("ΔrsbRU", "delru", 10, "Y")
                ,("ΔrsbQP", "delqp", 10, "Y")]

traceticker = mticker.MaxNLocator(nbins=3)
selected = {"wt": [1,2,3], #,4,5,6,7],
            "delru": [1,2,3], #,4,5,6,7,8,9,10,11],
            "delqp": [1,2,3], #,4,5,6,7,8,9,10],
             }

for i, (strain, fname, xstart, chan) in enumerate(tracestrains): 
    filename_pattern = os.path.join(this_dir, "data", fname)
    for df in glob.glob(filename_pattern + "_*_" + chan + ".mat"):
        print(df)
        dat = scipy.io.loadmat(df)
        #print(dat.keys())
        y = dat["yout"][0][0][0] 
        x = (dat["xout"][0][0][0].astype(float) * minutes_per_frame)/60
        xstarttime = (xstart*minutes_per_frame)/60
        axall[i, 0].plot(x, y, linewidth=0.5, color="gray")
        #re.match(df, os."")
        #axall[i, 0].plot(x, y, linewidth=1.0, color="gray")
        fnum = int(df.replace(filename_pattern, "").replace("_"+chan+".mat", "").replace("_", ""))
        if fnum in selected[fname]:
            axall[i, 0].plot(x, y, linewidth=1.0)
            


    #endtime=10
    endtime = (31 * minutes_per_frame)/60
    xstarttime = (15 * minutes_per_frame)/60
    axall[i, 0].set_xlim(left=xstarttime, right=endtime)
    if i == 0:
        ylim = 320
    elif i in [2,3]:
        ylim = 200
    elif i == 1:
        ylim=300
    axall[i, 0].set_ylim(0, ylim)
    title = "P$_{sigA}$-RFP" if chan == "R" else "P$_{sigB}$-YFP"
    title = "P$_{sigA}$-RFP" if chan == "R" else "P$_{sigB}$-YFP"
    axall[i, 0].set_title(strain + " " + title, y=0.6)
    if i < 3:
        axall[i, 0].set_xticklabels([])
    axall[i, 0].yaxis.set_major_locator(traceticker)
    ytticks = axall[i, 0].yaxis.get_major_ticks()
    #ytticks[-2].label1On=False

for a in axall.flatten():
    a.tick_params(axis="both", length=2, direction="out")
    
axall[-1, 0].set_xlabel("Time (hours)")
axall[-1, 1].set_xlabel("Fluorescence (AU)")
axall[1,0].annotate("Fluorescence (AU)", 
                 xy=(0,0),
                 xytext=(0.07, 0.35),  
                 xycoords='figure fraction',
                 textcoords='figure fraction',
                 horizontalalignment='center', verticalalignment='center',
                 rotation=90,
                 fontsize="medium", color=mpl.rcParams['axes.labelcolor']
                 )
axall[1, 1].set_ylabel("")
axall[1,1].annotate("Percentage total cells", 
                 xy=(0,0),
                 xytext=(-0.18, 0.0),  
                 xycoords='axes fraction',
                 textcoords='axes fraction',
                 horizontalalignment='center', verticalalignment='center',
                 rotation=90,
                 fontsize="medium", color=mpl.rcParams['axes.labelcolor']
                 )

letter_settings = { 
           "horizontalalignment": 'left',
           "verticalalignment": 'top',
           "fontsize": figure_util.letter_font_size, 
           "color": "black"}

aximg.text(-0.05, 1.0, "A", transform=aximg.transAxes, **letter_settings)
for a, l in zip(axall[:,0].flatten(), figure_util.letters[1:5]):
    #a.annotate(l, xy=(0,0), xytext=(-0.05, 1.),  **letter_settings)
    a.text(-0.36, 1., l, transform=a.transAxes, **letter_settings)

for a, l in zip(axall[:,1].flatten(), figure_util.letters[5:]):
    a.text(-0.34, 1., l,  transform=a.transAxes, **letter_settings)
    ##a.annotate(l, xy=(0,0), xytext=(-0.1, 1.), **letter_settings)


filename = "pad_movie_tracemain"

width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=1.0)
figall.set_size_inches(width, height)
figall.subplots_adjust(left=0.15,
                       right=0.99,
                       top=1.0,
                       bottom=0.1, 
                       hspace=0.1)

print("request size : ", figure_util.inch2cm((width, height)))
figure_util.save_figures(figall, filename, ["png", "pdf"], this_dir)
