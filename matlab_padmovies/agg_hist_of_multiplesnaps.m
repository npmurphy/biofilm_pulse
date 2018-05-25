function [ fg,  Rhandle, Yhandle] = agg_hist_of_multiplesnaps( strain_list ,  strain_name, bins, final_frame_only)
%HIST_OF_MULTIPLESNAPS Summary of this function goes here
%   Detailed explanation goes here
edges_to_bins = @(edges) edges(2:end) - ((edges(2) - edges(1))/2);

fg = figure()%;
Rhandle = subplot(2, 2, 1);
hold on
Yhandle = subplot(2, 2, 2);
hold on
RNhandle = subplot(2, 2, 3);
hold on
YNhandle = subplot(2, 2, 4);
hold on


for h = [ Rhandle Yhandle ] 
    ylabel(h, '% of cells');
    xlabel(h, 'Mean Intensity');
end
% for h = [ RNhandle YNhandle ] 
%     ylabel(h, '% of cells');
%     xlabel(h, 'Mean Normed Intensity');
% end
hold on
title(Yhandle, [ strain_name ' : YFP cells']);
title(Rhandle, [ strain_name ' : RFP cells']);
title(YNhandle, [ strain_name ' : YFP Norm']);
title(RNhandle, [ strain_name ' : RFP Norm']);

Y_cells = [];
R_cells = [];
YN_cells = [];
RN_cells = [];
for m = 1:length(strain_list)
    [p, s] = compileschnitz(strain_list(m), 'load', true);
    if final_frame_only
         [Ymean, Rmean] = snapcompress(max(p.frames), s);
    else
        [Ymean, Rmean] = frame_snapcompress(p.frames, s);
        %[Ymean, Rmean] = totalsnapcompress(s);
    end
    Y_cells = [ Y_cells Ymean ];
    R_cells = [ R_cells Rmean ];
    YN_cells = [ YN_cells Ymean/mean(Ymean) ];
    RN_cells = [ RN_cells Rmean/mean(Rmean) ];
end
histogram(Rhandle, R_cells, bins, 'Normalization', 'probability','FaceColor','r' );
histogram(Yhandle, Y_cells, bins, 'Normalization', 'probability','FaceColor','g' );
histogram(RNhandle, RN_cells, bins, 'Normalization', 'probability','FaceColor','r' );
histogram(YNhandle, YN_cells, bins, 'Normalization', 'probability','FaceColor','g' );

xlim(Rhandle, [0, max(R_cells)]);
xlim(Yhandle, [0, max(Y_cells)]);
xlim(RNhandle, [0, max(RN_cells)]);
xlim(YNhandle, [0, max(YN_cells)]);

%annotation(Rhandle, 
dim = [.6 .7 .4 .3];
Rstr = sprintf('# Cells %d\n RFP Mean %.02f\nRFP CV %.02f\nYFP Mean %.02f\n YFP CV %.02f', length(R_cells), mean(R_cells), std(R_cells)/mean(R_cells),mean(Y_cells), std(Y_cells)/mean(Y_cells));
annotation( 'textbox',dim,'String',Rstr)
%annotation(Yhandle, 'textbox',dim,'String',Ystr)
%output_args = [];
end

