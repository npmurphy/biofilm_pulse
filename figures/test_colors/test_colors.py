
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

import figure_util


custcolor = {"Sig A": figure_util.red,
             "Sig B": figure_util.green,
             "Spoii D": figure_util.blue,
             "Sspb (not used in plots)" :matplotlib.colors.to_rgb("cyan") 
             }

reporter_names = custcolor.keys()

# (0.87607843137254915, 0.59843137254901957, 0.74431372549019614)]

# sspb_strains = [('JLB077', "WT",   "#4C72B0"),
#                 ('JLB117', "2xQP", "#55A868"),
#                 ('JLB118', "ΔσB",  "#C44E52")
#                 ]

#https://github.com/mwaskom/seaborn/blob/master/seaborn/palettes.py
#SEaborn deep palate
# sigb_strains = [('JLB021', "WT", (0.54666666666666686, 0.37254901960784315, 0.5725490196078431)), 
#                 ("JLB088", "ΔrsbRU", (0.80000000000000004, 0.49882352941176472, 0.19999999999999996)),
#                 ("JLB039", "ΔrsbQP", (0.87607843137254915, 0.59843137254901957, 0.74431372549019614)), 
#                 ("JLB095", r"2$\times$rsbQP", (0.83999999999999986, 0.83999999999999997, 0.35999999999999999)),
#                 ("JLB098",  "ΔσB", (0.55215686274509801, 0.36392156862745101, 0.25568627450980397)),
#                 (" ", "median", figure_util.pink),
#                 (" ", "mode", figure_util.orange)
#                  ]

strains = figure_util.strain_color
strains = {st[1] : st[2] for st in figure_util.strains }

strains["median"] = figure_util.pink
strains["mode"] = figure_util.orange
strain_names = strains.keys()#reporter_names = custcolor.keys()

fig, ax =  plt.subplots(1,1)

for i, name in enumerate(strain_names):
    color = strains[name]
    ax.plot([0,1], [1+i, 1+i], label=name, color=color, linewidth=3) 

for i, fp in enumerate(reporter_names):
    color = custcolor[fp]
    ax.plot([0,1], [5*i, 5-(5*i)], label=fp, color=color,linewidth=3)

ax.legend()
filename = "figure_colors"
width, height = figure_util.cm2inch((12, 12))
fig.set_size_inches(width, height)
fig.tight_layout()
fig.savefig(filename + ".png", dpi=300) 
fig.savefig(filename + ".pdf") 
plt.show()