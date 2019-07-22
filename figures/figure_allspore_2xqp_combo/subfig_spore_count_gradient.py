# import os.path

import matplotlib.pyplot as plt
import numpy as np

import lib.figure_util as figure_util
import pandas as pd
import seaborn as sns

def get_figure_peaks(
    ax, file_df, gradient_data, strains, chan, min_sample_size=None, kwargs={}
):
    distances = gradient_data["distance"].values

    df = pd.DataFrame(columns=["strain", "peak", "file"])
    print(strains)
    print(pd.__version__)
    for strain in strains:
        print(strain)
        st_files = file_df.index[(file_df.strain == strain)]
        data_columns = ["file_{0}_{1}".format(s, chan) for s in st_files]
        total_columns = ["file_{0}_total_counts".format(s) for s in st_files]

        if min_sample_size:
            for dc, tc in zip(data_columns, total_columns):
                gradient_data.loc[gradient_data[tc] < min_sample_size, dc] = np.nan
                #print(gradient_data[dc])
        smooth_data = gradient_data[data_columns].rolling(window=5).mean()

        strain_grads = smooth_data[data_columns].values

        name = figure_util.strain_label[strain]
        for l in range(strain_grads.shape[1]):
            i = len(df)
            max_i = np.nanargmax(strain_grads[:, l])
            df.loc[i] = {"strain": name, "peak": distances[max_i], "file": l}
            # max_l += [max_i]
    print(df)

    # sns.v
    # iolinplot(x="strain", y="peak", data=df, ax=ax)
    alpha = 1
    my_pal = {figure_util.strain_label[s]: (*figure_util.strain_color[s], alpha) for s in strains}
    my_pal["WT"] = "gray"
    print(my_pal)
    ax = sns.boxplot(y="strain", x="peak", data=df, ax=ax, palette=my_pal, linewidth=1)#, boxprops={"alpha":.3})
    #ax = sns.swarmplot(y="strain", x="peak", data=df, ax=ax, s=3, color="black", alpha=0.7)
    ax.set_xlabel("")
    #ax.legend()
    return ax

def get_figure_individual(
    ax, file_df, gradient_data, strain, chan, min_sample_size=None, kwargs={}
):
    distances = gradient_data["distance"].values
    if "label" not in kwargs:
        label = figure_util.strain_label[strain]
    else:
        label = kwargs["label"]

    st_files = file_df.index[(file_df.strain == strain)]
    data_columns = ["file_{0}_{1}".format(s, chan) for s in st_files]
    total_columns = ["file_{0}_total_counts".format(s) for s in st_files]

    if min_sample_size:
        for dc, tc in zip(data_columns, total_columns):
            gradient_data.loc[gradient_data[tc] < min_sample_size, dc] = np.nan
    
    smooth_data = gradient_data[data_columns].rolling(window=5).mean()

    strain_grads = smooth_data.values

    for l in range(strain_grads.shape[1]):
        ax.plot(
            distances, strain_grads[:, l], color=plt.cm.Set3(l / 12), linewidth=1
        
        )  # , label=l)

    ax.set_ylim(bottom=0)
    return ax


def get_figure(
    ax, file_df, gradient_data, strain, chan, min_sample_size=None, kwargs={}
):
    distances = gradient_data["distance"].values
    if "color" not in kwargs:
        color = figure_util.strain_color[strain]
    else:
        color = kwargs["color"]

    if "label" not in kwargs:
        label = figure_util.strain_label[strain]
    else:
        label = kwargs["label"]

    st_files = file_df.index[(file_df.strain == strain)]
    data_columns = ["file_{0}_{1}".format(s, chan) for s in st_files]
    total_columns = ["file_{0}_total_counts".format(s) for s in st_files]

    if min_sample_size:
        for dc, tc in zip(data_columns, total_columns):
            gradient_data.loc[gradient_data[tc] < min_sample_size, dc] = np.nan

    # doesnt work
    # gradient_data.loc[(gradient_data[total_columns]<min_sample_size).values, data_columns] = np.nan
    strain_grads = gradient_data[data_columns]

    mean_trace = strain_grads.mean(axis=1)
    sem_trace = strain_grads.sem(axis=1)
    ax.plot(distances, mean_trace, color=color, label=label)
    ax.fill_between(
        distances,
        mean_trace - sem_trace,
        mean_trace + sem_trace,
        color=color,
        alpha=0.3,
    )

    ax.set_ylim(bottom=0)
    return ax


def main():
    import pandas as pd
    import lib.filedb as filedb
    import os.path

    base = os.path.join(
        os.path.dirname(__file__), "../../datasets/LSM700_63x_sspb_giant/"
    )

    file_df = filedb.get_filedb(os.path.join(base, "file_list.tsv"))
    file_df = file_df[
        ~(
            (file_df["name"] == "JLB077_48hrs_center_1_1")
            & (file_df["dirname"] == "Batch1")
        )
    ]
    individual = pd.read_csv(
        os.path.join(base, "spore_cell_individual.tsv"), sep="\t", index_col="index"
    )

    fig, ax = plt.subplots(3, 1)

    sspb_strains = [
        ("JLB077", "WT"),
        ("JLB117", "2x$\mathit{rsbQP}$"),
        ("JLB118", "ΔσB"),
    ]

    chan_axes = {
        "area_norm_spore_counts": 0,
        "area_norm_cell_counts": 1,
        "area_norm_total_counts": 2,
    }

    # Some images had little tiny regions at the end with <10 cell spores in them
    # that produced huges spikes of 100% spores etc.
    # to ignore this we are using 100 as a minimum sample size.
    # 10 does the job, 500, 100 look good at the top but introduce more artifacts later.
    # 100 is just a big enough number.

    for strain, _ in sspb_strains:
        for chan, a in chan_axes.items():
            ax[a] = get_figure(ax[a], file_df, individual, strain, chan, 100)
    plt.show()


if __name__ == "__main__":
    main()
