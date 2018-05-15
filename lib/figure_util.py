import subprocess
import re
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import string
import os.path
import matplotlib.pyplot as plt

def apply_style():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    plt.style.use(os.path.join(current_dir, '../figures/figstyle.mpl'))

def save_figures(fig, filename, extensions, base_dir=".", dpi=300):
    #current_dir = os.path.dirname(os.path.realpath(__file__))
    basename = os.path.join(base_dir, filename)
    for ext in extensions: 
        fig.savefig(basename + "." + ext, dpi=dpi)
        #fig.clear()
    if "pdf" in extensions:
        print_pdf_size(basename + ".pdf")


letter_font_size = 8
dpi = 300
#sns.color_palette("Set1", 8, desat=0.6)
red, blue, green, purple, orange, yellow, brown, pink = \
    [(0.73568627450980395, 0.26039215686274508, 0.26509803921568614),
    (0.31686274509803924, 0.483921568627451, 0.62039215686274507),
    (0.37647058823529422, 0.60705882352941176, 0.36941176470588244),
    (0.54666666666666686, 0.37254901960784315, 0.5725490196078431),
    (0.80000000000000004, 0.49882352941176472, 0.19999999999999996),
    (0.83999999999999986, 0.83999999999999997, 0.35999999999999999),
    (0.55215686274509801, 0.36392156862745101, 0.25568627450980397),
    (0.87607843137254915, 0.59843137254901957, 0.74431372549019614)]

hrs24, hrs48, hrs72, hrs96 = [
    (0.85999999999999999, 0.37119999999999997, 0.33999999999999997),
    (0.56880000000000008, 0.85999999999999999, 0.33999999999999997),
    (0.33999999999999997, 0.82879999999999987, 0.85999999999999999),
    (0.63119999999999976, 0.33999999999999997, 0.85999999999999999)]

#sns.hls_palette( 7, l=0.7, s=0.9)
all_times_dict = { 
    12: (0.9700000000000001, 0.46239999999999987, 0.4299999999999998),
    24: (0.9700000000000001, 0.92525714285714289, 0.4299999999999998),
    36: (0.55188571428571398, 0.9700000000000001, 0.4299999999999998),
    48: (0.4299999999999998, 0.9700000000000001, 0.77097142857142864),
    60: (0.4299999999999998, 0.70617142857142845, 0.9700000000000001),
    72: (0.61668571428571362, 0.4299999999999998, 0.9700000000000001),
    96: (0.9700000000000001, 0.4299999999999998, 0.86045714285714303)
}

black = (0, 0, 0)
timecolor = { 24:hrs24, 48:hrs48, 72:hrs72, 96:hrs96 }

custcolor = {"RFP": red, "YFP": green, "CFP": blue }

mean_color = orange
mode_color = green
                
sigb = "σᴮ"

sspb_strains = [('JLB077', "WT",   black),
                ('JLB117', "2×rsbQP", orange),
                ('JLB118', "Δσᴮ",  purple)
                ]

sigb_strains = [('JLB021', "WT", black),
                ("JLB088", "ΔrsbRU", yellow),
                ("JLB039", "ΔrsbQP", brown),
                ('JLB095', "2×rsbQP",orange),
                ("JLB098",  "Δσᴮ", purple),
                 ]

strains = sigb_strains + sspb_strains
strain_color = {st[0] : st[2] for st in strains }
strain_label = {st[0] : st[1] for st in strains }

lower_letters = string.ascii_lowercase
upper_letters = string.ascii_uppercase
letters = upper_letters

def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

def inch2cm(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i*inch for i in tupl[0])
    else:
        return tuple(i*inch for i in tupl)

def shift_legend(ax, leg, xshift=0, yshift=0):
    bb = leg.get_bbox_to_anchor().inverse_transformed(ax.transAxes)
    bb.x0 += xshift
    bb.x1 += xshift
    bb.y0 += yshift
    bb.y1 += yshift
    leg.set_bbox_to_anchor(bb, transform = ax.transAxes)
    return ax, leg


#http://scipy.github.io/old-wiki/pages/Cookbook/Matplotlib/LaTeX_Examples
#http://stackoverflow.com/questions/29187618/matplotlib-and-latex-beamer-correct-size
#246.09686 # pnas column width 
pts2mm = 0.352777777
column_width_pt = 246.09686
fig_width_small_cm = 8.6
fig_width_small_pt = ((fig_width_small_cm *10) / pts2mm)
fig_width_medium_cm = 11.4
fig_width_medium_pt = ((fig_width_medium_cm*10) / pts2mm)
fig_width_big_cm = 17.8 
fig_width_big_pt = (fig_width_big_cm *10) / pts2mm


def get_figsize(columnwidth, wf=0.5, hf=(5.**0.5-1.0)/2.0, ):
    """Parameters:
      - wf [float]:  width fraction in columnwidth units
      - hf [float]:  height fraction in columnwidth units.
                     Set by default to golden ratio.
      - columnwidth [float]: width of the column in latex. Get this from LaTeX 
                             using \showthe\columnwidth
    Returns:  [fig_width,fig_height]: that should be given to matplotlib
    """
    fig_width_pt = columnwidth*wf 
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*hf      # height in inches
    return [fig_width, fig_height]

def get_pdf_size(path):
    result = subprocess.check_output(['pdfinfo', path]).decode()
    for line in result.split('\n'):
        #match = re.match(r"Page size:\s+(\d).*", line)
        match = re.match(r"Page size:\s+(\d+\.\d+) x (\d+\.\d+) .*", line)
        if match is not None:
            width, height = match.groups()
            widthmm = float(width) * pts2mm 
            heightmm = float(height) * pts2mm   
            return widthmm / 10, heightmm /10
            break
    raise Exception("No page size info!")

def print_pdf_size(path):
    width, height = get_pdf_size(path)
    print("{0:.02f}cm wide {1:.02f}cm high".format(width, height))


def draw_scale_bar(img, r, c, scale_length, thickness, legend, fontsize = 40):
    scalebar = int(scale_length) 
    img[r:r+thickness, c:c + scalebar, :] = 255 #white
    
    pilim = Image.fromarray(img)
    draw = ImageDraw.Draw(pilim)
    smallfont = ImageFont.truetype("Arial", fontsize)
    draw.text((c, r+thickness), legend, (255, 255, 255), font=smallfont)
    img = np.array(pilim) 
    return img

def annotate_image(img, r, c, legend, fontsize = 40):
    pilim = Image.fromarray(img)
    draw = ImageDraw.Draw(pilim)
    smallfont = ImageFont.truetype("Arial", fontsize)
    draw.text((c, r), legend, (255, 255, 255), font=smallfont)
    img = np.array(pilim) 
    return img
