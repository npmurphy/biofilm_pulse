run file_lists.m

width = 4; % cms
height = 2; % cms
fontsize = 4.5;

rback = mean([174, 173, 191, 191, 174, 173, 174, 172, 174, 173, 174, 172, 178, 176, 176, 174, 172, 173]);
yback = mean([250, 252, 228, 225, 226, 223, 226, 223, 227, 224, 226, 223, 226, 223, 227, 223, 222, 223]);

%% Calculate the RFP only YFP signal
% [RFPonly_list.rback]=deal(rback);
% [RFPonly_list.yback]=deal(yback);
%[rfp_only_r, rfp_only_y] = good_sections_of_movies(RFPonly_list, 3, 15, 1400);
%yfp_blank = mean(rfp_only_y)

yfp_blank = 9.6431; 
%yfp_blank = 0; 
[sigB_list.yfpOffset]=deal(yfp_blank);

[delRU_list.yfpOffset]=deal(yfp_blank);

[delSigB_list.yfpOffset]=deal(yfp_blank);

[delQP_list.yfpOffset]=deal(yfp_blank);


[fg, ~,~] = figure_1_hist(delRU_list, 'ΔRU', 'DRU', 10);
%saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delru_hist.pdf', 'pdf')
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delru_hist.pdf', width,height,fontsize );

[fg, ~,~] = figure_1_hist(delQP_list, 'ΔQP', 'DQP', 10);
%saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delru_hist.pdf', 'pdf')
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delqp_hist.pdf', width,height,fontsize );

[fg, ~,~] = figure_1_hist(sigB_list, 'WT', 'WT', 10);
%saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delru_hist.pdf', 'pdf')
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/sigb_hist.pdf', width,height,fontsize );

[fg, ~,~] = figure_1_hist(delSigB_list, 'Δσ^B', 'DSB', 10);
%saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delru_hist.pdf', 'pdf')
%my_pdf_save(fg, '/home/nmurphy/work/projects/stochastic/paper/figure1/delsigb_hist.pdf', width, height,fontsize);

