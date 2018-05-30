function [ fh , axes] = figure_1_track(p, strain, list_of_cells, nounicodename, channel)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
p.load = 1; % dont recimpile schnitzes 
[p, schnitzcells] = compileschnitz(p);

if isempty(list_of_cells);
    list_of_cells = find(([schnitzcells.D]==0)&([schnitzcells.approved]==1));
    disp(list_of_cells)
end

selection = list_of_cells;
cmap = jet(length(selection));
% 
% for i = 1:length(schnitzcells);
%     ratio = schnitzcells(i).MY./schnitzcells(i).MR;
%     schnitzcells(i).Mratio = ratio;
% end

fh = figure();

for si = 1:length(selection)
    s = selection(si);
    hold on 
    [ h, ~, ~, ~] = plotschnitzme(schnitzcells, 'frames', ['M' channel], s, '-', 'HANDLEBACK');
    [ xout,yout,xavgout,yavgout,stdY, xlabelt,ylabelt] = dumpschnitzme(schnitzcells, 'frames', ['M' channel], s, '');
    savevars = {'xout','yout','xavgout','yavgout','stdY', 'xlabelt','ylabelt'};
    %save(sprintf('/media/nmurphy/BF_Data_Orange/datasets/padmovies_brightfield/traces/%s_%i_%s.mat', nounicodename, si, channel), savevars{:});
 
    h.Color = cmap(si,:);
    plots{si} = h;
    labels{si} = sprintf('%d', s);
    
end
fig = get(fh);
axes = gca; %fig.CurrentAxes;
xlabel(axes, 'Image Frames');
ylabel(axes, 'Fluorescence');

title(axes, [ strain ' YFP expression in selected cells']); 

end

