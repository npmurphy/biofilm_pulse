import numpy as np
from scipy.stats.mstats import spearmanr
import scipy.ndimage

def sliding_window_histos(cell_df, depth_info, window_width, channel, valbins, valbinmax=None, blur=0, percentile=99):
    (min_d, max_d, step) = depth_info

    if valbinmax is None:
        valbinmax = cell_df[channel].max()
    bins = np.linspace(0, valbinmax,  valbins)
    rad = window_width/2
    distances = np.arange(min_d+rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    distribu = np.zeros((valbins-1, len(slider)))
    
    #cdists = np.zeros(len(slider)) 
    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)].copy() 
        if percentile > 0:
            percentile_v = np.percentile(cut_df["meannorm_green"], percentile)
            cut_df = cut_df[cut_df["meannorm_green"] < percentile_v].copy()
        ncell = len(cut_df)
        counts, _ = np.histogram(cut_df[channel], bins=bins)#, density=True)
        if blur>0:
            counts = scipy.ndimage.gaussian_filter1d(counts, blur)
        distribu[:, i] = counts/ncell

    return distances, bins, distribu

def sliding_window_histos_with_stats(cell_df, depth_info, window_width, channel, valbins, 
                                     valbinmin=0, valbinmax=None, blur=0, percentile=99, calc_stats={}):
    (min_d, max_d, step) = depth_info

    if valbinmax is None:
        valbinmax = cell_df[channel].max()
    bins = np.linspace(valbinmin, valbinmax,  valbins)
    sbins = bins[:-1] + (bins[1] - bins[0])/2
    rad = window_width/2
    distances = np.arange(min_d+rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    distribu = np.zeros((valbins-1, len(slider)))
    if calc_stats:
        stats = {k: np.zeros(len(distances)) for k in calc_stats.keys()} 
    else:
        stats = {}
    
    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed) 
                         & (cell_df[channel]>=valbinmin)].copy()  # to reduce ncell
        if percentile > 0:
            percentile_v = np.percentile(cut_df["meannorm_green"], percentile)
            cut_df = cut_df[cut_df["meannorm_green"] < percentile_v].copy()
        counts, _ = np.histogram(cut_df[channel], bins=bins)#, density=True)
        if blur>0:
            counts = scipy.ndimage.gaussian_filter1d(counts, blur)
        if calc_stats:
            for k, v in calc_stats.items():
                f = v[2]
                stats[k][i] = f(cut_df[channel], counts, sbins)
        ncell = len(cut_df)
        distribu[:, i] = counts/ncell

    return distances, sbins, distribu, stats

# Pearson 
def sliding_window_correlation(cell_df, depth_info, window_width, channels):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    correlation = np.zeros(len(slider))
    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)] 
        if len(cut_df) == 0:
            correlation[i] = np.nan 
        else:
            correlation[i] = np.corrcoef(cut_df[channels[0]], cut_df[channels[1]])[0,1]
    return distances, correlation

# Spearman
def sliding_window_correlation_Spearman(cell_df, depth_info, window_width, channels):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    correlation = np.zeros(len(slider))
    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)] 
        if len(cut_df) < 3:
            correlation[i] = np.nan 
        else:
            coe, pval = spearmanr(cut_df[channels[0]], cut_df[channels[1]])
            correlation[i] = coe
    return distances, correlation

def sliding_window_distribution(cell_df, depth_info, window_width, channel, percentile=99):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(min_d + rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    keys = ["mean", "median", "std", "skew", "cv", "sem"]
    distribu = np.zeros((len(keys), len(distances)))

    #cdists = np.zeros(len(slider)) 
    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)]
        if percentile > 0:
            percentile_v = np.percentile(cell_df["meannorm_green"], percentile)
            cut_df = cut_df[cut_df["meannorm_green"] < percentile_v].copy()
        distribu[0, i] = cut_df[channel].mean()
        distribu[1, i] = cut_df[channel].median()
        distribu[2, i] = cut_df[channel].std()
        distribu[3, i] = cut_df[channel].skew()
        distribu[4, i] = cut_df[channel].mean() / cut_df[channel].std()
        distribu[5, i] = cut_df[channel].sem()

    return (distances, distribu.T,
            dict([ (n, i) for (i, n) in enumerate(keys)]))

def sliding_window_errors(cell_df, depth_info, window_width, channel, error_methods, cuttoff=100):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(min_d + rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances ]
    just_quantile = [s for s in error_methods if "quantile" in s]
    quantiles = [ int(s.replace("quantile", ""))/100 for s in just_quantile]
    updowns = [ f for f in error_methods if f not in ["mean", "median", "distance"]]
    stat_cols = [ "up_" + k for k in updowns ] + [ "dn_" + k for k in updowns ]
    statvals = { k : np.zeros(len(distances)) for k in stat_cols }
    statvals["mean"] = np.zeros(len(distances))
    statvals["median"] = np.zeros(len(distances))
    statvals["distance"] = distances

    for i, (sd, ed) in enumerate(slider):
        cut_df = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)]
        if len(cut_df) < cuttoff: 
            cut_df[channel] = np.nan 
        statvals["mean"][i] = cut_df[channel].mean()
        statvals["median"][i] = cut_df[channel].median()
        if "std" in error_methods:
            val = cut_df[channel].std()
            #print(val)
            statvals["dn_std"][i] = statvals["mean"][i] - val 
            statvals["up_std"][i] = statvals["mean"][i] + val
        elif "sem" in error_methods:
            val = cut_df[channel].sem()
            statvals["dn_sem"][i] = statvals["mean"][i] - val
            statvals["up_sem"][i] = statvals["mean"][i] + val
        for label, quant in zip(just_quantile, quantiles): 
            statvals["dn_" + label][i] = cut_df[channel].quantile(q=(1 - quant))
            statvals["up_" + label][i] = cut_df[channel].quantile(q=quant)
    return statvals

def sliding_window_indivfiles(cell_df, depth_info, window_width, channel, cuttoff=20):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(min_d + rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    keys = [("mean", np.nanmean)] #,  ("std", np.std), ("sem", lambda x: x.sem() ) ]
    #print(cell_df.columns)
    fileids = cell_df["global_file_id"].unique()
    
    results = { k: np.zeros((len(fileids), len(distances))) for k, _ in keys}

    for f, fid in enumerate(fileids):
        filedf = cell_df[cell_df["global_file_id"] == fid]
        for i, (sd, ed) in enumerate(slider):
            cut_df = filedf[(filedf["distance"]>sd) & (filedf["distance"]<=ed)] 
            for k, func in keys:
                if len(cut_df) > cuttoff: 
                    results[k][f, i] = func(cut_df[channel].values)
                else:
                    results[k][f, i] = np.nan

    return distances, results, fileids

def sliding_window_indivfiles_min_samples(cell_df, depth_info, window_width, channel):
    (min_d, max_d, step) = depth_info
    rad = window_width/2
    distances = np.arange(min_d + rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    #keys = [("mean", np.mean),  ("std", np.std) ]
    print(cell_df.columns)
    fileids = cell_df["global_file_id"].unique()
    
    #result = { k: np.zeros(len(fileids), len(distances)) for k, _ in keys }
    means = np.zeros((len(fileids), len(distances)))

    counts = np.zeros((len(fileids), len(distances)), dtype=np.int)
    min_samples = np.zeros(len(distances), dtype=np.int)

    for f, fid in enumerate(fileids):
        filedf = cell_df[cell_df["global_file_id"] == fid]
        for i, (sd, ed) in enumerate(slider):
            cut_df = filedf[(filedf["distance"]>sd) & (filedf["distance"]<=ed)] 
            counts[f, i] = len(cut_df)

    for i in range(counts.shape[1]):
        non_zero = (counts[:,i][counts[:,i]>0])
        print(non_zero)
        if len(non_zero) > 0:
            min_samples[i] = non_zero.min(axis=0)
        min_samples[i] = 0
    print(min_samples)

    for f, fid in enumerate(fileids):
        filedf = cell_df[cell_df["global_file_id"] == fid]
        for i, (sd, ed) in enumerate(slider):
            cut_df = filedf[(filedf["distance"]>sd) & (filedf["distance"]<=ed)] 
            if len(cut_df) > 0: 
                sample = cut_df.sample(n=min_samples[i])
                means[f, i] = sample[channel].mean()
            else: 
                means[f, i] = np.nan

    return distances, means, min_samples

def sliding_window_counts(spore_df, cell_df, depth_info, window_width):
    (min_d, max_d, step) = depth_info
    rad = window_width / 2
    distances = np.arange(min_d +rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    result = np.zeros((2, len(slider)))
    for i, (sd, ed) in enumerate(slider):
        cut_df_c = cell_df[(cell_df["distance"]>sd) & (cell_df["distance"]<=ed)] 
        cut_df_s = spore_df[(spore_df["distance"]>sd) & (spore_df["distance"]<=ed)] 
        result[0, i] = len(cut_df_s)
        result[1, i] = len(cut_df_c)
    return distances, result, ["spore", "cell"]

#import time
def sliding_window_pixel_counts(distmap, depth_info, window_width):
    (min_d, max_d, step) = depth_info
    rad = window_width / 2
    distances = np.arange(min_d +rad, max_d-rad, step)
    slider = [ (d-rad, d+rad) for d in distances]
    result = np.zeros((1, len(slider)))
    for i, (sd, ed) in enumerate(slider):
        
        #t0 = time.time()
        # this was 10x faster than the where method
        px = np.count_nonzero((distmap>sd) & (distmap<=ed))
        #t1 = time.time()
        # print("CNZ", t1 - t0)
        # print(px)
        result[0, i] = px
        
        # t0 = time.time()
        # locs = np.where((distmap>sd) & (distmap<=ed))
        # px2 = len(locs[0])
        # t1 = time.time()
        # print("Where", t1 - t0)
        # print(px2)

    return distances, result, ["pixel_areas"]