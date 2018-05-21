import os.path
import re

import numpy as np
import pandas as pd


def parse_filename(filename):
    fn = os.path.basename(filename)
    fn = os.path.splitext(fn)[0]
    prams = fn.split("|")[1]
    glist = re.findall(r'([^=]+)=([^=]+)(?:,|$)', prams)
    return {k: float(v) for k, v in glist}



def get_into_plotform(df, params, max_distance, spore_time_hours):
    #print(params)
    df["stress_10"] = np.log10(df["stress"])
    min_stress = df["stress_10"].min()
    max_min = np.max(df["stress_10"] - min_stress)
    df["dist"] = abs(((df["stress_10"] - min_stress) / max_min) - 1.0) * max_distance
    df["resp_a"] = params["pscale_a"] * df["stress"] * params["b0"] #+ params["ascale_a"]
    df["resp_b"] = params["pscale_b"] * df["stress"] * params["b0"] #+ params["ascale_b"]
    #threshold  = ss.gamma.ppf(0.2, params["resp_b"]/5e-3, 0, 0.05/0.005)
    df["spore"] = df["Atime"] > (spore_time_hours * 3600)
    #print(df.columns)
    return df


def get_dataset(filep, max_distance, spore_time_hours):
    filename_parms = parse_filename(filep)
    biofilm_df = pd.read_csv(filep, sep="\t")
    biofilm_df = get_into_plotform(biofilm_df, filename_parms, max_distance, spore_time_hours)
    return biofilm_df
