import pandas as pd
import os.path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from glob import glob
import subfig_sig_pulse_gradient
import subfig_spore_gradient
import simulation_processor
import subfig_traces
#import subfig_network
#import svgutils.compose as sc

from lib import figure_util
figure_util.apply_style()

this_dir = os.path.dirname(__file__)


fig = plt.figure()
# outer_gs = gridspec.GridSpec(2, 2, wspace=0.30, hspace=0.3, )# , widthight_ratios=[0.7, 0.3])
# grad_gs  = gridspec.GridSpecFromSubplotSpec(1, 2, 
#                                   width_ratios=[1,1],
#                                   subplot_spec = outer_gs[1:3,:],
#                                   hspace=0.03)
ax = fig.subplots(2,2)

# network_ax = plt.subplot(outer_gs[0, 0])
# apulse_ax = plt.subplot(outer_gs[0,1])
# sigb_pulse_ax  = plt.subplot(grad_gs[0])
# spor_pulse_ax  = plt.subplot(grad_gs[1])
network_ax    = ax[0,0]
apulse_ax     = ax[0,1]
sigb_pulse_ax = ax[1,1]
spor_pulse_ax = ax[1,0]

all_axes = [network_ax, apulse_ax, sigb_pulse_ax, spor_pulse_ax]

#################
## Network drawing 
##############
network_ax.spines['top'].set_visible(True)
network_ax.spines['bottom'].set_visible(True)
network_ax.spines['left'].set_visible(True)
network_ax.spines['right'].set_visible(True)
network_ax.axes.get_xaxis().set_ticks([])
network_ax.axes.get_yaxis().set_ticks([])

runf = os.path.join(this_dir, "../../datasets/model_results/movethresh3/")

pulse_wt_info = glob(runf + "bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0]
pulse_2x_info = glob(runf + "bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.5*.tsv")[0]
# bistb_wt_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=2.0*.tsv")[0]
# bistb_2x_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=4.0*.tsv")[0]

trace_wt_pulse = glob(runf + "bfsim_b_trace_seed16222|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0]

pulse_wt_df = simulation_processor.get_dataset(pulse_wt_info, max_distance=140.0,  spore_time_hours=0.5)
pulse_2x_df = simulation_processor.get_dataset(pulse_2x_info, max_distance=140.0,  spore_time_hours=0.5)
# bistb_wt_df = simulation_processor.get_dataset(bistb_wt_info, max_distance=140.0,  spore_time_hours=0.5)
# bistb_2x_df = simulation_processor.get_dataset(bistb_2x_info, max_distance=140.0,  spore_time_hours=0.5)

traces = pd.read_csv(trace_wt_pulse, sep="\t")
apulse_ax, traces = subfig_traces.get_figure(apulse_ax, traces)
apulse_ax.set_xlim(2, 5)
lab = apulse_ax.set_xlabel("Hours (simulated)")
apulse_ax.set_ylabel("Species counts")

sigb_pulse_ax, sb_p_plots = subfig_sig_pulse_gradient.get_figure(sigb_pulse_ax, pulse_wt_df, pulse_2x_df)
#sigb_pulse_ax.xaxis.labelpad = -20
lines, labels = sigb_pulse_ax.get_legend_handles_labels()
sigb_pulse_ax.set_ylabel("Mean final $B$ value")
sigb_pulse_ax.legend(lines, ["$s_B$", "2$\\times s_B$"])
#sigb_pulse_ax.set_xlabel("Distance from top of biofilm (simulated)")
#sigb_bistb_ax, sb_b_plots = subfig_sig_pulse_gradient.get_figure(sigb_bistb_ax, bistb_wt_df, bistb_2x_df)
# for a in [ sigb_pulse_ax, sigb_bistb_ax]:
#     a.set_ylim(top = 40)

spor_pulse_ax, sp_p_plots = subfig_spore_gradient.get_figure(spor_pulse_ax, pulse_wt_df, pulse_2x_df)
lines, labels = spor_pulse_ax.get_legend_handles_labels()
spor_pulse_ax.legend(lines, ["$s_B$", "2$\\times s_B$"])
spor_pulse_ax.set_ylabel("Fraction of spores")

print(lab.get_font_properties())
spor_pulse_ax.text(0.5, 0.005, "Distance top of biofilm (simulated)",
                    fontproperties=lab.get_font_properties(),
                    ha="center",
                    va="bottom",
                    color= lab.get_color(),
                    transform=fig.transFigure )

#ylabelx = -0.06

# for a in [ spor_pulse_ax, spor_bistb_ax]:
#     a.set_ylim(top = 0.5)
topy=0.98
boty=0.51
lefx=0.025
rigx=0.525

#bot_pos = (-0.08, 1.0)
#for a, l, p in zip(all_axes, figure_util.letters, [top_pos, top_pos, bot_pos, bot_pos]):
figsets = {"transform": fig.transFigure,
            "va":"top",
            "ha":"right",
            "fontsize": figure_util.letter_font_size}
ax[0,0].text(lefx, topy, "A", **figsets)
ax[0,0].text(rigx, topy, "B", **figsets)
ax[0,0].text(lefx, boty, "C", **figsets)
ax[0,0].text(rigx, boty, "D", **figsets)
    
# for a in all_axes[2:]:
#     a.yaxis.set_label_coords(ylabelx, 0.5)

#all_axes[-2].tick_params(labelbottom='off')  
fig.align_labels(all_axes)  

filename = "model_summary_figure"
width, height = figure_util.get_figsize(figure_util.fig_width_small_pt, wf=1.0, hf=0.75 )
fig.set_size_inches(width, height)
fig.subplots_adjust(left=0.10, right=0.98, top=0.98, bottom=0.11, hspace=0.26, wspace=0.25)
print("request size : ", figure_util.inch2cm((width, height)))
figure_util.save_figures(fig, filename, ["png", "pdf"], this_dir)
# Tikz is easier
# fig.savefig(filename + ".svg") #, bbox_inches="tight"  )

# sc.Figure("{0}cm".format(width), "{0}cm".format(height),
#             sc.Panel(sc.SVG(filename+".svg")),
#             sc.Panel(sc.SVG("network.svg")).move(10,10)
#             ).save("figure_combine.svg")
