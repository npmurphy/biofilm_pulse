# This was originally the ggplot style from matplotlib
# from http://www.huyng.com/posts/sane-color-scheme-for-matplotlib/

savefig.dpi : 300
patch.linewidth: 0.5
patch.facecolor: 348ABD  # blue
patch.edgecolor: EEEEEE
patch.antialiased: True

font.size: 6.0
font.family: DejaVu Sans #Arial # specifiying this because Bitstream doesnt show unicode
#text.latex.unicode: True
#mathtext.default : regular
mathtext.fontset : custom
#mathtext.fontset : dejavusans
mathtext.rm : DejaVu Sans
mathtext.it : DejaVu Sans:italic
mathtext.bf : DejaVu Sans:bold

# Font Sizes
# xx-small, x-small, small, medium, large, x-large, xx-large, smaller, larger.
axes.facecolor: white # E5E5E5
#axes.edgecolor: white
axes.edgecolor: black
axes.spines.right : False
axes.spines.top : False
axes.linewidth: 0.5
axes.grid: False
axes.titlesize: large
axes.labelsize: medium 
axes.labelcolor: 555555
axes.axisbelow: True       # grid/ticks are below elements (e.g., lines, text)

axes.prop_cycle: cycler('color', ['E24A33', '348ABD', '988ED5', '777777', 'FBC15E', '8EBA42', 'FFB5B8'])
                   # E24A33 : red
                   # 348ABD : blue
                   # 988ED5 : purple
                   # 777777 : gray
                   # FBC15E : yellow
                   # 8EBA42 : green
                   # FFB5B8 : pink

xtick.color: 555555
xtick.major.width: 0.5
xtick.direction: in

ytick.color: 555555
ytick.major.width: 0.5
ytick.direction: in


#grid.color: white
grid.color: lightgray
grid.linestyle: :    # solid line

figure.facecolor: FFFFFF #white
figure.edgecolor: 0.50

figure.subplot.wspace  : 0.2


