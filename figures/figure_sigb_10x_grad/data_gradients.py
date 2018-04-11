import os.path

import pandas as pd

import data.bio_film_data.strainmap as strainmap
from lib import filedb

dataset_dir = "datasets/LSM780_10x_sigb/"
gradient_df = pd.read_hdf(dataset_dir + "gradient_data.h5", "data")
gradient_df["ratio"] = gradient_df["green_bg_mean"]/gradient_df["red_bg_mean"]
output_dir = os.path.join(dataset_dir , "gradient_summary")

file_df = filedb.get_filedb(dataset_dir + "filedb.tsv")


time = 48.0
location = "center"
strain_map, des_strain_map = strainmap.load()

def get_strain(name):
    fids = file_df[(file_df["time"] == time) &
                   (file_df["location"] == location) &
                   (file_df["strain"] == des_strain_map[name])].index
    print(name, " has ", len(fids))
    df = gradient_df[gradient_df["file_id"].isin(fids)]
    return df


# stp, width = 5, 1
# wt_sigby        jlb021
# delru_sigby     jlb088
# delqp_sigby     jlb039
# 2xqp_sigby      jlb095
# delsigb_sigby   jlb098
#fig.figimage(skimage.io.imread("10x_delqp_48_image_crop.jpg"))
columns = {}
try:
    os.mkdir(output_dir)
except FileExistsError as e:
    pass
for c, (strain) in enumerate(["wt_sigar_sigby","delru_sigar_sigby" ,"delqp_sigar_sigby"]): # ,"2xqp_sigby" ,"delsigb_sigby"]
    df = get_strain(strain)
    df = df[df["cdist"]>2.0]
    df_mean = df.groupby("cdist").mean()
    df_sem = df.groupby("cdist").sem()
    columns["mean"] = df_mean["ratio"].values 
    columns["upsem"] = columns["mean"] + df_sem["ratio"].values 
    columns["downsem"] = columns["mean"] - df_sem["ratio"].values 
    columns["distance"] = df_mean.index
    data = pd.DataFrame(columns)
    data.index.name = "i"
    data.to_csv(os.path.join(output_dir, strain + ".tsv"), sep="\t")