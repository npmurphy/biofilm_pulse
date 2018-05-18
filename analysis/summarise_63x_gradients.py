import os.path

import numpy as np
import pandas as pd
import scipy.stats 
#from lib.cmaps import cmrand
#import scipy.stats

#import data.bio_film_data.strainmap as strainmap
from lib import filedb
from lib.analysis.sliding_windows import sliding_window_indivfiles, sliding_window_errors #sliding_window_distribution


def save_indiv_mean_data(files, alldf, chans, strain, name, savedir):
    base_col_titles = ["distance", "mean", "sem", "std"]
    for c, (chan, title) in enumerate(chans):
        for t, time in enumerate([ 24, 48, 72, 96 ]):
            columns = {}
            column_titles = base_col_titles.copy()
            looking = files[(files["time"]==time) & (files["location"]=="center") & (files["strain"]==strain)]
            these_cells = alldf[alldf["global_file_id"].isin(looking.index)]
            distance, results, fileids = sliding_window_indivfiles(these_cells, (0, 150, 0.5), 1, chan)
            columns["distance"] = distance
            for f, fid in enumerate(fileids):
                columns["file_"+str(fid)] = results["mean"][f,:]
                column_titles += [ "file_" + str(fid)] 
            columns["mean"] = np.nanmean(results["mean"], axis=0)
            columns["sem"] = scipy.stats.sem(results["mean"], axis=0, nan_policy="omit")
            columns["std"] = np.nanstd(results["mean"], axis=0)

            data = pd.DataFrame(columns)
            data.index.name = "i"
            save_path = os.path.join(savedir, "indiv_{0}_{1}_{2}.tsv".format(title, strain, time))
            data.to_csv(save_path, sep="\t", na_rep="nan", columns=column_titles)

def save_error_bar_data(files, alldf, chans, strain, name, savedir):
    base_col_titles = ["distance", "mean", "median", "sem", "std", "quantile75", "quantile90", "quantile95"] 
    for c, (chan, title) in enumerate(chans):
        for t, time in enumerate([ 24, 48, 72, 96 ]):
            #column_titles = base_col_titles.copy()
            looking = files[(files["time"]==time) & (files["location"]=="center") & (files["strain"]==strain)]
            these_cells = alldf[alldf["global_file_id"].isin(looking.index)]
            columns = sliding_window_errors(these_cells, (0, 150, 0.5), 1, chan, base_col_titles)
            data = pd.DataFrame(columns)
            data.index.name = "i"
            save_path = os.path.join(savedir, "error_{0}_{1}_{2}.tsv".format(title, strain, time))
            data.to_csv(save_path, sep="\t", na_rep="nan")#, columns=column_titles)


def main():
    this_dir = os.path.dirname(__file__)
    base = os.path.join(this_dir, "../datasets/LSM700_63x_sigb")
    alldf = pd.read_hdf(os.path.join(base, "single_cell_data.h5"))
    files = filedb.get_filedb(os.path.join(base, "file_list.tsv"))
    alldf["ratio"] = alldf["green_raw_bg_mean"]/alldf["red_raw_bg_mean"]
    
    chans = [("green_raw_bg_mean", "unnormed"), 
            ("green_raw_bg_maxnorm", "maxnorm"), ## normalized by RFP gradient peak
            ("green_raw_bg_meannorm", "meannorm")]
    chans = [("ratio", "ratio")]
    
            
    save_path = os.path.join(base, "gradients")
    try:
        os.mkdir(save_path)
    except FileExistsError as e:
        pass
    
    for strain, name in [("jlb021", "WT"),  ("jlb088","delRU"), ("jlb039","delQP"), ("jlb095", "2xQP")]:
        #save_data_file(files, alldf, chans, strain, name)
        save_indiv_mean_data(files, alldf, chans, strain, name, save_path)
        save_error_bar_data(files, alldf, chans, strain, name, save_path)


if __name__ == "__main__":
    main()
    #view_main()
