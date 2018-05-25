function [ fg ] = single_cell_traces(p, cellnum)

fg = figure('name',sprintf('Schnitz %d', cellnum));
[ p, s ] = compileschnitz(p, 'load', true);

[goodframes, ~, ~, ~ ] = get_good_frames_of_movie(p, s, 3, 15, 1400);



% sh = 54;
% subplot(2,length(goodframes),length(goodframes)+(1:length(goodframes)));
rectangle('Position',[goodframes(1), 0, goodframes(end) - goodframes(1), 200], 'FaceColor', [0.98 0.98, 0.86]);
hold on 
[yfpp, yfplotcell, ~, ~] = plotschnitzme(s, 'frames', 'MY',cellnum, 'go-', 'HANDLEBACK');
yfp = yfplotcell{1};
hold on 
rfpp = plotschnitzme(s, 'frames', 'len',cellnum, 'ko-', 'HANDLEBACK');
hold on 
lenp = plotschnitzme(s, 'frames', 'MR',cellnum, 'ro-', 'HANDLEBACK');
title(sprintf('Cell %d', cellnum));
end