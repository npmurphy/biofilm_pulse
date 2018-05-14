import os.path

import matplotlib.pyplot as plt
#import matplotlib.ticker as mticker
import pandas as pd

import lib.strainmap as strainmap
import lib.filedb as filedb
import lib.figure_util as figure_util



def get_figure(ax, file_df, gradient_df):
    time = 48.0
    location = "center"
    strain_map, des_strain_map = strainmap.load()
    print(des_strain_map)

    # stp, width = 5, 1
    # wt_sigby        jlb021
    # delru_sigby     jlb088
    # delqp_sigby     jlb039
    # 2xqp_sigby      jlb095
    # delsigb_sigby   jlb098
    #fig.figimage(skimage.io.imread("10x_delqp_48_image_crop.jpg"))
    for c, (strain) in enumerate(["wt_sigar_sigby","2xqp_sigar_sigby"]): # , ,"delsigb_sigby"]
        
        fids = file_df[(file_df["time"] == time) &
                        (file_df["location"] == location) &
                        (file_df["strain"] == des_strain_map[strain])].index
        print(strain, " has ", len(fids))
        df = gradient_df[gradient_df["file_id"].isin(fids)]

        df = df[df["cdist"]>2.0] # ignore top 2um for consistency
        df_mean = df.groupby("cdist").mean()
        df_sem = df.groupby("cdist").sem()
        #df_mean[df]
        print(len(df))
        color = figure_util.strain_color[des_strain_map[strain].upper()]
        label = figure_util.strain_label[des_strain_map[strain].upper()]
        ax.plot(df_mean.index, df_mean["ratio"], color=color, label=label)#/df["mean_red"])
        ax.fill_between(df_mean.index, df_mean["ratio"]-df_sem["ratio"],df_mean["ratio"]+df_sem["ratio"],color=color, alpha=0.4 )#/df["mean_red"])
        # ax[c].plot(df_mean.index, df_mean["ratio"], color="purple")#/df["mean_red"])
        # ax[c].fill_between(df_mean.index, df_mean["ratio"]-df_sem["ratio"],df_mean["ratio"]+df_sem["ratio"],color="purple", alpha=0.4 )#/df["mean_red"])
        # ax[c].set_xlim(left=0, right=200)

    #leg = ax.legend(loc="upper right")
    #leg.get_frame().set_alpha(1.0)

    #ax.set_ylim(0, 0.2700)
    ax.set_ylim(0, 0.4500)
    ax.set_xlim(left=0, right=150)
    #ax.set_xlabel("Distance from air interface (μm)")
    ax.set_ylabel("Ratio of P$_{sigB}$-YFP to P$_{sigA}$-RFP")
    #ax.text(-0.05, letter_lab[1], "D", transform=ax.transAxes, fontsize=8)
    return ax

def main():
    tenx_basepath = "../../datasets/biofilm_cryoslice/LSM780_10x_sigb/"
    gradient_df = pd.read_hdf(os.path.join(tenx_basepath, "gradient_summary.h5"), "data")
    #gradient_df["ratio"] = gradient_df["mean_green"]/gradient_df["mean_red"]
    gradient_df["ratio"] = gradient_df["mean_green"]/gradient_df["mean_red"]

    file_df = filedb.get_filedb(os.path.join(tenx_basepath, "filedb.tsv"))

    fig, ax = plt.subplots()
    ax = get_figure(ax, file_df, gradient_df)
    plt.show()


if __name__ == "__main__":
    main()