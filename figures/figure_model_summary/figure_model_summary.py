import pandas as pd
import numpy as np
import os.path
import filedb
import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
from glob import glob
import subfig_sig_pulse_gradient
import subfig_spore_gradient
import simulation_processor
import subfig_traces
#import subfig_network
import svgutils.compose as sc

plt.style.use('../figstyle.mpl')
import figure_util
from figure_util import dpi

fig, all_axes = plt.subplots(4, 1)
#all_axes = np.atleast_2d(all_axes)

network_ax = all_axes[0]
apulse_ax = all_axes[1]
sigb_pulse_ax = all_axes[2]
spor_pulse_ax = all_axes[3]
# sigb_bistb_ax = all_axes[1, 2] 
# spor_bistb_ax = all_axes[1, 3] 

#################
## Network drawing 
##############
network_ax.spines['top'].set_visible(True)
network_ax.spines['bottom'].set_visible(True)
network_ax.spines['left'].set_visible(True)
network_ax.spines['right'].set_visible(True)
network_ax.axes.get_xaxis().set_ticks([])
network_ax.axes.get_yaxis().set_ticks([])

runf = "../../algo/luna/final_sweeps/"

pulse_wt_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0]
pulse_2x_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=0.7*,pscale_b=0.5*.tsv")[0]
bistb_wt_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=2.0*.tsv")[0]
bistb_2x_info = glob(runf + "movethresh3/bfsim_b_qp|*pscale_a=3.6*,pscale_b=4.0*.tsv")[0]

trace_wt_pulse = glob(runf + "movethresh3/bfsim_b_trace_seed16222|*pscale_a=0.7*,pscale_b=0.25*.tsv")[0]

pulse_wt_df = simulation_processor.get_dataset(pulse_wt_info, max_distance=140.0,  spore_time_hours=0.5)
pulse_2x_df = simulation_processor.get_dataset(pulse_2x_info, max_distance=140.0,  spore_time_hours=0.5)
# bistb_wt_df = simulation_processor.get_dataset(bistb_wt_info, max_distance=140.0,  spore_time_hours=0.5)
# bistb_2x_df = simulation_processor.get_dataset(bistb_2x_info, max_distance=140.0,  spore_time_hours=0.5)

traces = pd.read_csv(trace_wt_pulse, sep="\t")
apulse_ax, traces = subfig_traces.get_figure(apulse_ax, traces)
apulse_ax.set_xlim(2, 5)
apulse_ax.set_xlabel("Hours (simulated)")
apulse_ax.set_ylabel("Species counts")

sigb_pulse_ax, sb_p_plots = subfig_sig_pulse_gradient.get_figure(sigb_pulse_ax, pulse_wt_df, pulse_2x_df)
sigb_pulse_ax.set_ylabel("Mean final $B$ value")
#sigb_pulse_ax.set_xlabel("Distance from top of biofilm (simulated)")
#sigb_bistb_ax, sb_b_plots = subfig_sig_pulse_gradient.get_figure(sigb_bistb_ax, bistb_wt_df, bistb_2x_df)
# for a in [ sigb_pulse_ax, sigb_bistb_ax]:
#     a.set_ylim(top = 40)

spor_pulse_ax, sp_p_plots = subfig_spore_gradient.get_figure(spor_pulse_ax, pulse_wt_df, pulse_2x_df)
spor_pulse_ax.set_ylabel("% spores")
spor_pulse_ax.set_xlabel("Distance top of biofilm (simulated)")
#spor_bistb_ax, sp_b_plots = subfig_spore_gradient.get_figure(spor_bistb_ax, bistb_wt_df, bistb_2x_df)

# for a in [ spor_pulse_ax, spor_bistb_ax]:
#     a.set_ylim(top = 0.5)
letter_pos = (-0.075, 1.0)
for a, l in zip(all_axes, figure_util.letters):
    a.text(*letter_pos, l,
            transform=a.transAxes,
            va="top", ha="right", fontsize=figure_util.letter_font_size)

filename = "model_summary_figure"
width, height = figure_util.get_figsize(figure_util.fig_width_medium_pt, wf=1.0, hf=1.0 )
#fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.06, hspace=0.25, wspace=0.25)
fig.set_size_inches(width, height)# common.cm2inch(width, height))
fig.tight_layout()
print("request size : ", figure_util.inch2cm((width, height)))
fig.savefig(filename + ".pdf") #, bbox_inches="tight"  )
fig.savefig(filename + ".png") #, bbox_inches="tight"  )

# Tikz is easier
# fig.savefig(filename + ".svg") #, bbox_inches="tight"  )

# sc.Figure("{0}cm".format(width), "{0}cm".format(height),
#             sc.Panel(sc.SVG(filename+".svg")),
#             sc.Panel(sc.SVG("network.svg")).move(10,10)
#             ).save("figure_combine.svg")


figure_util.print_pdf_size(filename + ".pdf")