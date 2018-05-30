run file_lists.m

fontsize = 4.5; %pts
width = 4; %cm
height = 2; %cm

% rback and yback are now part of the original schnitz file
%% Calculate the RFP only YFP signal
% [rfp_only_r, rfp_only_y] = good_sections_of_movies(RFPonly_list, 3, 15, 1400);
% yfp_blank = mean(rfp_only_y)
yfp_blank = 9.6431; 
[all_list.yfpOffset]=deal(yfp_blank);

%p_delRU = delRU_list(5); % what we used initially
%delRU_tracks = [33 54 61 66 73 74 87 98 99 104 111]; % 11
%xlim(ax, [10, 32])
p_delRU = delRU_list(5);
delRU_tracks = [];
[fg, ax] = figure_1_track(p_delRU, 'ΔRU', delRU_tracks, 'delru', 'Y');
[fg, ax] = figure_1_track(p_delRU, 'ΔRU', delRU_tracks, 'delru', 'R');

%[fg, ax] = figure_1_track(p_delRU, 'ΔRU', delRU_tracks, 'delru', 'Y');

xlim(ax, [10, 40]);
ylim(ax, [0, 220]);
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/pulsecompete/figure_padmovies/matlabfig/delru_track.pdf', width, height, fontsize)

p_delQP = delQP_list(8);
delQP_tracks = []; %[ 53    55    57    87    90   101   117   124   129   134]; %10
[fg, ax] = figure_1_track(p_delQP, 'ΔQP', delQP_tracks, 'delqp', 'Y');
[fg, ax] = figure_1_track(p_delQP, 'ΔQP', delQP_tracks, 'delqp', 'R');
xlim(ax, [15, 35])
ylim(ax, [0, 4])
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/pulsecompete/figure_padmovies/matlabfig/delqp_track.pdf', width,height,fontsize )

p_sigB =  sigB_list(3);

sigb_tracks = [];%[145 137 159 139 153 120 95]; %7
[fg, ax] = figure_1_track(p_sigB, 'WT', sigb_tracks, 'wt', 'Y');
ylim(ax, [0, 220])
xlim(ax, [10, 40])
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/pulsecompete/figure_padmovies/matlabfig/sigb_track.pdf', width,height,fontsize )

% 
% sigb_tracks = [145 137 159 139 153 120 95]; %7
[fg, ax] = figure_1_track(p_sigB, 'WT', sigb_tracks, 'wt', 'R');
ylim(ax, [0, 220])
xlim(ax, [10, 40])
% %my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/pulsecompete/figure_padmovies/matlabfig/sigb_track.pdf', width,height,fontsize )
% 
% 
% p_delsigb = delSigB_list(5);
% delsigb_tracks = [83    92    94    96   102   111   117   129   139   156];
% [fg, ax] = figure_1_track(p_delsigb, 'Δσ^B', delsigb_tracks, 'delsigb', 'Y');
% ylim(ax, [0, 220])
% xlim(ax, [1, 26])
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/pulsecompete/figure_padmovies/matlabfig/delsigb_track.pdf', width, height,fontsize )
