import os.path

import pandas as pd
import numpy as np
#import data.bio_film_data.strainmap as strainmap
import lib.strainmap as strainmap
from lib import filedb

#dataset_dir = "datasets/LSM780_10x_sigb/"
dataset_dir = "/media/nmurphy/BF_Data_Orange/datasets/lsm700_live20x_newstrain1"
#gradient_df = pd.read_hdf(dataset_dir + "gradient_data.h5", "data")
gradient_df = pd.read_hdf(os.path.join(dataset_dir, "gradient_data_distmap.h5"), "data")
#gradient_df["ratio"] = gradient_df["green_bg_mean"]/gradient_df["red_bg_mean"]
gradient_df["ratio"] = gradient_df["green_raw_mean"]/gradient_df["red_raw_mean"]
output_dir = os.path.join(dataset_dir , "gradient_summary")

file_df = filedb.get_filedb(os.path.join(dataset_dir, "file_list.tsv"))


time = 48.0
#strain_map, des_strain_map = strainmap.load()
strain_to_type, type_to_strain = strainmap.load()
cell_types = np.unique([ t[0] for t in strain_to_type.values()])
strain_to_type = {s:t[0] for s,t in strain_to_type.items() }
type_to_strain = dict(zip(cell_types, [[]]*len(cell_types)))
for strain, typel in strain_to_type.items():
    type_to_strain[typel] =  type_to_strain[typel] + [strain]

def get_strain(name):
    fids = file_df[(file_df["time"] == time) &
                   (file_df["strain"].isin(type_to_strain[name]))].index
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
for c, (strain) in enumerate(type_to_strain.keys()):
#for c, (strain) in enumerate(["wt_sigar_sigby","delru_sigar_sigby" ,"delqp_sigar_sigby"]): # ,"2xqp_sigby" ,"delsigb_sigby"]
    df = get_strain(strain)
    if len(df) == 0:
        continue
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