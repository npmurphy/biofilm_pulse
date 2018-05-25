function [ output_args ] = hist_of_multiplesnaps( strain_list ,  strain_name, bins)
%HIST_OF_MULTIPLESNAPS Summary of this function goes here
%   Detailed explanation goes here
edges_to_bins = @(edges) edges(2:end) - ((edges(2) - edges(1))/2);

fg = figure()%;
Rhandle = subplot(1, 2, 1);
hold on
Yhandle = subplot(1, 2, 2);
for h = [ Rhandle Yhandle ] 
    ylabel(h, '% of cells');
    xlabel(h, 'Mean Intensity');
end

title(Yhandle, [ strain_name ' : YFP cells']);
title(Rhandle, [ strain_name ' : RFP cells']);

colors = 'rgb';
for m = 1:length(strain_list)
    [p, s] = compileschnitz(strain_list(m), 'load', true);
    [Ymean, Rmean] = snapcompress(p.hist_frames, s);
    
    [Rcounts, Redges] = histcounts(Rmean,bins, 'Normalization', 'probability' );
    Rbins = edges_to_bins(Redges);
    hold on
    plot(Rhandle, Rbins, Rcounts,'Color','r'); %, 'trans', 0.5);
    %hold off

    [Ycounts,Yedges] = histcounts(Ymean,'Normalization', 'probability');
    Ybins = edges_to_bins(Yedges);
    hold on
    plot(Yhandle, Ybins, Ycounts, 'Color','g');%, 'alpha', 0.5);
    %hold off

end
hold off

end

