function [ fg,  Rhandle, Yhandle] = agg_hist_of_good_snaps( strain_list ,  strain_name, bins)
%HIST_OF_MULTIPLESNAPS Summary of this function goes here
%   Detailed explanation goes here

fg = figure();%;
Rhandle = subplot(1, 2, 1);
hold on
Yhandle = subplot(1, 2, 2);
hold on

for h = [ Rhandle Yhandle ] 
    ylabel(h, '% of cells');
    xlabel(h, 'Mean Intensity');
end

hold on
title(Yhandle, [ strain_name ' : YFP cells']);
title(Rhandle, [ strain_name ' : RFP cells']);

[R_cells, Y_cells] = good_sections_of_movies(strain_list, 3, 15, 1400);

histogram(Rhandle, R_cells, bins, 'Normalization', 'probability','FaceColor','r' );
histogram(Yhandle, Y_cells, bins, 'Normalization', 'probability','FaceColor','g' );


xlim(Rhandle, [0, max(R_cells)]);
xlim(Yhandle, [0, max(Y_cells)]);

dim = [.6 .7 .4 .3];
Rstr = sprintf('# Cells %d\n RFP Mean %.02f\nRFP CV %.02f\nYFP Mean %.02f\n YFP CV %.02f', length(R_cells), mean(R_cells), std(R_cells)/mean(R_cells),mean(Y_cells), std(Y_cells)/mean(Y_cells));
annotation( 'textbox',dim,'String',Rstr)

end

