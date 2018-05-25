function [ fh , axes] = figure_1_track(p, strain, list_of_cells, nounicodename, channel)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
p.load = 1; % dont recimpile schnitzes 
[p schintzcells] = compileschnitz(p);

selection = list_of_cells;
cmap = jet(length(selection));

fh = figure();

for si = 1:length(selection)
    s = selection(si);
    hold on 
    [ h, ~, ~, ~] = plotschnitzme(schintzcells, 'frames', ['M' channel], s, '-', 'HANDLEBACK');
    [ xout,yout,xavgout,yavgout,stdY, xlabelt,ylabelt] = dumpschnitzme(schintzcells, 'frames', ['M' channel], s, '')
    savevars = {'xout','yout','xavgout','yavgout','stdY', 'xlabelt','ylabelt'};
    save(sprintf('../../paper/pulsecompete/figure_padmovies/data/%s_%i_%s.mat', nounicodename, si, channel), savevars{:})
    hold on 
    h.Color = cmap(si,:);
    %plots{si} = h;
    %labels{si} = sprintf('%d', s);
    
end
%fig = get(fh);
axes = gca; %fig.CurrentAxes;
xlabel(axes, 'Image Frames');
ylabel(axes, 'Fluorescence');

title(axes, [ strain ' YFP expression in selected cells']); 

end

