
import skimage.io
import matplotlib.pyplot as plt
import matplotlib.patches as mplp
import numpy as np
from mpl_toolkits.axes_grid.anchored_artists import AnchoredAuxTransformBox
import figure_util

plt.style.use('../figstyle.mpl')

def get_figure(ax, tgt_shape):
    (ys, xs) = tgt_shape
    circa, radax, raday = (0.10 * xs, 0.5 * ys), 0.1 * xs, 0.1 * ys
    circb, radbx, radby = (0.90 * xs, 0.5 * ys), 0.1* xs, 0.1 * ys
    estxt = (0.5*xs, 0.9*ys)
    spore = (0.1*xs, 0.1*ys)

    blue = figure_util.blue
    green = figure_util.green
    # box = AnchoredAuxTransformBox(ax.transData, loc=2)
    
    ann = ax.annotate("Energy\n Stress",
        xy=circa, xycoords='data',
        xytext=estxt, textcoords='data',
        va="center", ha="center",
        #bbox=dict(boxstyle="round4", fc="w"),
        arrowprops=dict(arrowstyle="-|>",
                        shrinkB=radax, # how short of the target point it is 
                        connectionstyle="arc3,rad=0.2",
                        relpos=(0., 0.5),
                        fc="black", 
                        ec="black"), 
        )

    ann = ax.annotate("Energy\n Stress",
        xy=circb, xycoords='data',
        xytext=estxt, textcoords='data',
        #size=20, va="center", ha="center",
        va="center", ha="center",
        #bbox=dict(boxstyle="round4", fc="w"),
        arrowprops=dict(arrowstyle="-|>",
                        shrinkB=radbx, # how short of the target point it is 
                        connectionstyle="arc3,rad=-0.2",
                        relpos=(1., 0.5),
                        fc="black", 
                        ec="black"), 
        )
 


    ax.annotate("test", circb, circa, 
                #xycoords="figure fraction", textcoords="figure fraction",
                #ha="right", va="center",
                #size=fontsize,
                arrowprops=dict(arrowstyle="|-|",
                                #patchB=nodeA,
                                shrinkA=radax, # how short of the target point it is 
                                shrinkB=0, #radbx, # maybe we need connectionsytyle clip
                                #clipB=radbx, # maybe we need connectionsytyle clip
                                fc="k", ec="k",
                                connectionstyle="arc3,rad=-0.2",
                                #width=10,
                                ),
                #bbox=dict(boxstyle="square", fc="w"),
                zorder=0)
    
    ann = ax.annotate("Spore",
        xy=circa, xycoords='data',
        xytext=spore, textcoords='data',
        va="center", ha="center",
        bbox=dict(boxstyle="round,pad=0.1,rounding_size=0.2", fc=blue),
        arrowprops=dict(arrowstyle="<|-",
                        shrinkB=radbx, # how short of the target point it is 
                        #connectionstyle="arc3,rad=-0.2",
                        #relpos=(1., 0.5),
                        fc="black", 
                        ec="black"), 
        )
    
    nodeA = mplp.Circle(circa, radax, color=blue, edgecolor="black", linewidth=4)
    nodeB = mplp.Circle(circb, radbx, color=green)
    ax.add_artist(nodeA)
    ax.add_artist(nodeB)
    # box.drawing_area.add_artist(nodeA)
    # box.drawing_area.add_artist(nodeB)
    ax.annotate("A", xy=circa , ha ="center", va="center")
    ax.annotate("B", xy=circb , ha ="center", va="center")
    ax.grid(False)
    ax.axis('off')
    return ax

def get_figure_lazy(ax):
    im = skimage.io.imread("network.png")
    im = np.rot90(im)
    ax.imshow(im, interpolation="bicubic")
    ax.grid(False)
    ax.axis('off')
    return ax

def main():
    fig, ax = plt.subplots(1,1)

    im = skimage.io.imread("network.png")
    
    ax.imshow(im, alpha=0.1)
    ax = get_figure(ax, im.shape[:2])

    plt.show()


if __name__ == '__main__':
    main()