function [ fg,  Rhandle, Yhandle] = agg_hist_of_good_snaps_comp_james( strain_list ,  strain_name, bins)
%HIST_OF_MULTIPLESNAPS Summary of this function goes here
%   Detailed explanation goes here

fg = figure();%;
Rhandle = subplot(2, 2, 1);
hold on
Yhandle = subplot(2, 2, 2);
hold on
RJhandle = subplot(2, 2, 3);
hold on
YJhandle = subplot(2, 2, 4);
hold on

for h = [ Rhandle Yhandle ] 
    ylabel(h, '% of cells');
    xlabel(h, 'Mean Intensity');
end

hold on
title(Yhandle, [ strain_name ' : YFP cells'], 'Interpreter', 'none');
title(Rhandle, [ strain_name ' : RFP cells'],  'Interpreter', 'none');

[R_cells, Y_cells] = good_sections_of_movies(strain_list, 3, 15, 1400);

histogram(Rhandle, R_cells, bins, 'Normalization', 'probability','FaceColor','r' );
histogram(Yhandle, Y_cells, bins, 'Normalization', 'probability','FaceColor','g' );

hist(RJhandle, R_cells);
hist(YJhandle, Y_cells);

if length(R_cells) > 0
    xlim(Rhandle, [0 max(R_cells)+50]);
    xlim(Yhandle, [0 max(Y_cells)+50]);
end

dim = [0.8 0.6 0.1 0.3];
msg = '# Cells %d\nRFP Mean %.02f\nRFP CV %.02f\nRFP skew %.02f\nYFP Mean %.02f\nYFP CV %.02f\nYFP skew %.02f';
Rstr = sprintf(msg, length(R_cells), ...
               mean(R_cells), (std(R_cells)/mean(R_cells)), skewness(R_cells),...
               mean(Y_cells), (std(Y_cells)/mean(Y_cells)), skewness(Y_cells));
annotation( 'textbox',dim,'String',Rstr)

end

