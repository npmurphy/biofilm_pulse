import scipy.stats
#from scipy.stats import skew
import numpy as np

# def plot_hist(ax, df, column, inbins, slice_info, percentile=0, kwargs={}):
#     histo_res = make_indivfile_histogram(df, column, inbins, slice_info, percentages=True, percentile=percentile)
#     cbins, indiv_hists, mean_indiv, histo_of_all, unique_files, ncells, (meanval, stdval, mskewval, pskewval, modeval, cvval) = histo_res

#     min_extents = np.min(indiv_hists, axis=0)
#     max_extents = np.max(indiv_hists, axis=0)
#     try: 
#         bgcolor = kwargs["extcolor"] 
#         bgalpha = kwargs["extalpha"] 
#     except:
#         bgcolor = "gray"
#         bgalpha = 1.0
#     ax.fill_between(cbins, max_extents, min_extents, color=bgcolor, alpha=bgalpha)

#     # print individual image plots
#     #for f in range(indiv_hists.shape[0]):
#     #    #ax.plot(cbins, indiv_hists[f, :], alpha=0.4, color="black", linewidth=0.5)
#     #    ax.plot(cbins, indiv_hists[f, :], alpha=0.4, color=kwargs["indivcolor"], linewidth=0.5)
#     #ax.plot(cbins, histo_all, color=kwargs["color"])
#     #cvval = df[column].std()/df[column].mean()
#     #skewval = skew(df[column])
#     ## if "console_stats" not in kwargs:
#     ##    kwargs["console_stats"] = False
#     ##if kwargs["console_stats"] == True:
#     #print("CV: {0:0.2f}".format(cvval))
#     #print("skew: {0:0.2f}".format(skewval))
#     #print("Samples: {0}".format(indiv_hists.shape[0]))
#     #print("Cells: {0}".format(n))
#     # else:
#     #     ax.annotate("CV: {0:0.2f}".format(cvval), xy=(0, 0), xytext=cv_loc, textcoords="axes fraction")
#     #     ax.annotate("Samples: {0}".format(indiv_hists.shape[0]), xy=(0, 0), xytext=samp_loc, textcoords="axes fraction")
#     #     ax.annotate("Cells: {0}".format(n), xy=(0, 0), xytext=cell_loc, textcoords="axes fraction")

#     return ax


def make_indivfile_histogram(df, column, inbins, slice_info, percentages=False, percentile=99, print_out_stats=False):
    unique_files = df["global_file_id"].unique()
    num_files = len(unique_files)
    individual_histos = np.zeros((num_files, len(inbins)-1))

    start, stop = slice_info
    in_range = df[(df["distance"] > start) & (df["distance"] <= stop)]

    if percentile > 0:
        percentile_v = np.percentile(in_range["meannorm_green"], percentile)
        in_range = in_range[in_range["meannorm_green"] < percentile_v].copy()
    

    for i, fnum in enumerate(unique_files):
        this_file = in_range[in_range["global_file_id"] == fnum]
        counts, out_bins = np.histogram(this_file[column].values, inbins, normed=(not percentages))
        individual_histos[i, :] = counts
        if percentages:
            #area = np.trapz(counts, out_bins[1:], dx=(out_bins[1] - out_bins[0]))
            individual_histos[i, :] /= len(this_file)
            individual_histos[i, :] *= 100

    mean_of_individual = np.mean(individual_histos, axis=0)
    histo_of_all, bins = np.histogram(in_range[column].values, inbins, normed=(not percentages))
    meanval = in_range[column].mean()
    stdval =  in_range[column].std()
    cvval = stdval/meanval
    maxi = histo_of_all.argmax()
    modeval = bins[maxi]
    mskewval = scipy.stats.skew(in_range[column], bias=False)
    mskurosisval = scipy.stats.kurtosis(in_range[column], bias=False)

    pskewval = (meanval - modeval)/stdval
    if print_out_stats:
        print("mean: {0:0.2f}".format(meanval))
        print("std: {0:0.2f}".format(stdval))
        print("CV: {0:0.2f}".format(cvval))
        print("Moment skew: {0:0.2f}".format(mskewval))
        #print("Pearson mode skew: {0:0.2f}".format(pskewval))
        print("Kurtosis {0:0.2f}".format(mskurosisval))
        print("Number of files: {0}".format(num_files))
        print("Cells: {0}".format(len(in_range)))
        print("------------------------")
    

    ncells = len(in_range)
    if percentages:
        #area = np.trapz(histo_of_all, bins[1:], dx=(bins[1] - bins[0]))
        histo_of_all = (histo_of_all / ncells) * 100
    cbins = bins[:-1] + (bins[1:] - bins[:-1])/2
    return cbins, individual_histos, mean_of_individual, histo_of_all, \
            unique_files, ncells, (meanval, stdval, mskewval, pskewval, modeval, cvval)


# def plot_indivfile_histograms(ax, df, column, inbins, slice_info, 
#                                 show_indivfiles, show_extents, 
#                                 globed_file_histo, indivfiles_mean_histo, kwargs):

#     cbins, indiv_hists, mean_indiv, histo_all, uniques, _ = make_indivfile_histogram(df, column, inbins, slice_info)

#     min_extents = np.min(indiv_hists, axis=0)
#     max_extents = np.max(indiv_hists, axis=0)
#     if show_indivfiles:
#         ax.fill_between(cbins, max_extents, min_extents, color="gray")

#     if show_indivfiles:
#         for f in range(indiv_hists.shape[0]):
#             ax.plot(cbins, indiv_hists[f, :], alpha=0.4, color="black")

#     if globed_file_histo:
#         ax.plot(cbins, histo_all, color="red")

#     if indivfiles_mean_histo:
#         ax.plot(cbins, mean_indiv, color="orange")

#     return ax
