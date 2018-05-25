
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import matplotlib.ticker as mticker
from matplotlib import rcParams
import numpy as np
import scipy.io
import scipy.stats
import skimage.io

from make_movie_strip import process_fp
from make_movie_strip import process_phase
from make_movie_strip import add_no_over
import figure_util
import data.bio_film_data.strainmap as strainmaper

plt.style.use('../figstyle.mpl')

figall = plt.figure()
#gs = gs.GridSpec(2, 3, width_ratios=[0.4, 0.25, 0.25])
#plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1 )

gs = gs.GridSpec(2, 4, height_ratios=[0.7, 0.3])
#gs.update(left=0.05, right=0.95, wspace=0.15, hspace=0.00)
gs.update(left=0.06, right=0.98, wspace=0.15, hspace=0.05)

aximgr = plt.subplot(gs[0, 0:2])
aximgr.grid(False)
aximgr.axis('off')
aximgy = plt.subplot(gs[0, 2:4])
aximgy.grid(False)
aximgy.axis('off')
axall = [plt.subplot(gs[1, i]) for i in range(4)]

yticks = mticker.MaxNLocator(nbins=4)

## Images 
"""
path = "movie_strip/sigB_biofilmpad6-O001_3-{0}-{1:03d}.tif"
image_num = 31
yfp_image = skimage.io.imread(path.format("y", image_num))
rfp_image = skimage.io.imread(path.format("t", image_num))
phase_image = skimage.io.imread(path.format("p", image_num))
max_yfp = yfp_image.max()
max_rfp = rfp_image.max()
#min_rfp = 255 #(max background)
#min_rfp = 210 #(mean background)
min_rfp = 210 # found it looks better
#min_rfp = 180 #(below mean background)
min_yfp = 329 #(mean off cell)
max_phase = phase_image.max()
min_phase = phase_image.min()
ROI = (slice(340,800), slice(555, 815)) # Row Col
"""
path = "movie_strip/2015-11-03/sigB_biofilmfinal-B_4/images/sigB_biofilmfinal-B_4-{0}-{1:03d}.tif"
image_num = 40
ROI = (slice(225,850), slice(450, 930)) # Row Col
yfp_image = skimage.io.imread(path.format("y", image_num))
rfp_image = skimage.io.imread(path.format("t", image_num))[0,:,:] # this rfp had another dim for some reason
phase_image = skimage.io.imread(path.format("p", image_num))
print("YIM", yfp_image.shape)
print("RIM", rfp_image.shape)
print("phase", phase_image.shape)
letter_lab = (-0.05, 1.0)
max_yfp = yfp_image.max()
max_rfp = rfp_image.max()
#min_rfp = 255 #(max background)
#min_rfp = 210 #(mean background)
min_rfp = 220 # found it looks better
#min_rfp = 180 #(below mean background)
min_yfp = 290 #(mean off cell)
max_phase = phase_image.max()
min_phase = phase_image.min()

proc_yfp = process_fp(yfp_image, ROI, min_yfp, max_yfp)
proc_rfp = process_fp(rfp_image, ROI, min_rfp, max_rfp)
#skimage.io.imsave("my_rfp_rescale.tiff", proc_rfp)
#proc_phase = process_phase(phase_image, ROI, min_phase, max_phase) 
proc_phase = process_phase(phase_image, ROI, min_phase, max_phase) 

print(proc_yfp.shape)
print("RFP", proc_rfp.shape)
print("Phase", proc_phase.shape)

yel_img = np.dstack([ proc_phase, add_no_over(proc_phase, proc_yfp), proc_phase])
red_img = np.dstack([add_no_over(proc_phase, proc_rfp), proc_phase, proc_phase])
#skimage.io.imsave("my_composite.tiff", red_img)
# absolution gray or red max
#red_img = np.dstack([np.max(proc_phase, proc_rfp), proc_phase, proc_phase])

## RED max 
# mixed = proc_phase.copy()
# mixed[proc_rfp>proc_phase] = proc_rfp[proc_rfp>proc_phase]
# red_img = np.dstack([mixed, proc_phase, proc_phase])

aximgr.imshow(np.rot90(red_img), interpolation="bicubic")
aximgy.imshow(np.rot90(yel_img), interpolation="bicubic")
# aximgr.set_title("ΔrsbRU P$_{sigA}$-RFP")
# aximgy.set_title("ΔrsbRU P$_{sigB}$-YFP")
aximgr.set_title("WT P$_{sigA}$-RFP")
aximgy.set_title("WT P$_{sigB}$-YFP")
aximgr.text(letter_lab[0], letter_lab[1], "A", transform=aximgr.transAxes, fontsize=8)
aximgy.text(letter_lab[0], letter_lab[1], "B", transform=aximgy.transAxes, fontsize=8)

#"P$_{sigA}$-RFP"
#plots_st = [ ("WT",  "sigA",  "WT_final", "R_cells_mn", "C",  "#001C7F") # this is the sea born "dark" version of jlb021
#            ,("WT",  "sigB", "WT_final",  "Y_cells_mn",  "D", figure_settings.strain_color["JLB021"])
#            ,("ΔrsbQP", "sigB", "DQP_final", "Y_cells_mn", "E", figure_settings.strain_color["JLB039"])
#            ,("ΔrsbRU", "sigB", "DRU_final", "Y_cells_mn", "F", figure_settings.strain_color["JLB088"])]
#
plots_st = [ ("WT",  "sigA",  "WT", "R_cells", "C",  "#001C7F", 280) # this is the sea born "dark" version of jlb021
            ,("WT",  "sigB", "WT",  "Y_cells",  "D", figure_util.strain_color["JLB021"], 180)
            ,("ΔrsbQP", "sigB", "DQP", "Y_cells", "E", figure_util.strain_color["JLB039"], 180)
            ,("ΔrsbRU", "sigB", "DRU", "Y_cells", "F", figure_util.strain_color["JLB088"], 180)]
letterh_lab = (-0.13, 1.025)

mean_normed = False
# if mean_normed:
#     mfp = np.nanmean(np.hstack([scipy.io.loadmat("data/"+dat_file+".mat")[chan][0] for (_, _, dat_file, chan, _,_) in plots_st[1:]]))
#     print(mfp)
for i, (strain, fname, dat_file, chan, letter, color, xmax) in enumerate(plots_st):
    dat = scipy.io.loadmat("data/"+dat_file+".mat")

    fp = dat[chan][0]
    fp = fp[~np.isnan(fp)]
    # if mean_normed:
    #     mfp = np.min(fp) ## Min
    #     fp = fp /mfp
    if dat_file == "DQP":
        print(fp.min())
    #     fig = plt.figure()
    #     plt.hist(fp, bins=10)
    #     plt.show()
    width = 10
    #nbins = np.arange(0, 250, width)
    ylim = 30
    if mean_normed:
        xlim = 5.0
        xmin = -1
        nbins = np.linspace(xmin, xlim, 25)
    else:
        xlim = xmax #120 #250
        xmin = -10
        nbins = np.arange(-10, 240, width)
    bar_width = ((nbins[1] - nbins[0]) ) * 0.8
    counts, bins = np.histogram(fp, nbins)
    print("strain:", strain, "N:", len(fp), "Skew:", scipy.stats.skew(fp, bias=False))

    scaled = (counts / len(fp)) * 100
    axall[i].bar(bins[:-1], scaled, color=color, width=bar_width )

    axall[i].set_ylim(0, ylim)
    axall[i].set_xlim(xmin, xlim) #fpd.max() + xlim_buffer)

    texty = ylim * 0.8
    textx = xlim * 0.15
    axall[i].set_title("{0}: {1}".format(strain, fname),y=0.6)
    #axall[i].set_xlabel("Mean Fluor. (AU)")
    axall[i].xaxis.set_major_locator(mticker.MaxNLocator(nbins=4))
    axall[i].text(letterh_lab[0], letterh_lab[1], letter, transform=axall[i].transAxes, fontsize=8)

    if i > 0:
        axall[i].set_yticklabels([])
axall[0].set_ylabel("% of cells")
# for k, v in rcParams.items():
#     if "x" in k:
#         print((k, v)) 
#print(axall[1].yaxis.get_label_position()) #-0.1,1.02)
figall.text(0.5, -0.05, 'Mean fluorecence (AU)', 
            horizontalalignment='center',
            color=rcParams["axes.labelcolor"],
            fontsize=rcParams["xtick.labelsize"])
# for l in np.linspace(-0.3, 0.000, 3):
#     figall.text(0.5, l, str(l))

filename = "all_hist"        
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.6 )
figall.set_size_inches(width, height)
figall.savefig(filename + ".pdf", dpi=300, transparent=True) #, bbox_inches='tight' )
figall.savefig(filename + ".png", dpi=300, transparent=True)#, bbox_inches='tight' )
figall.clear()
plt.close(figall)
figure_util.print_pdf_size(filename + ".pdf")
