function  [Rcells, Ycells, RcellsMeanNorm, YcellsMeanNorm, report] = good_sections_of_movies(schnitz_list, log_cell_num, ang, YFP_scale_var)
%% Schnitz_list is a list of schnitz objects, each corresponding to 1 movie and its frames, 
Ycells = []; 
Rcells = [];
YcellsMeanNorm = [];
RcellsMeanNorm = [];

num_frames = 0;
for s = 1:length(schnitz_list)
    pt = schnitz_list(s);
    %pt.autoYFL = 37.9373;
    %pt.yfpOffset= 37.9373;
    [pt, st] = compileschnitz(pt);%, 'load', true);
    
    %[ good_frames, ~, ~, ~ ] = get_good_frames_of_movie_rfp(pt, st, cell_num, RFP_var_th);
    [ good_frames, ~, ~, ~ ] = get_good_frames_of_movie(pt, st, log_cell_num, ang, YFP_scale_var);
    num_frames = num_frames + length(good_frames);
    [ Ymeans, Rmeans] = snapcompress_frames(good_frames, st);
    Ycells = [ Ycells Ymeans];
    Rcells = [ Rcells Rmeans];
    disp(sprintf('Mean %f', nanmean(Ycells)));
    disp(sprintf('STD %f', nanstd(Ycells)));
    YcellsMeanNorm = [ YcellsMeanNorm (Ymeans/mean(Ymeans))];
    RcellsMeanNorm = [ RcellsMeanNorm (Rmeans/mean(Rmeans))];

end
report = sprintf(' looked at %i files with %i total frames\n \t there were %i cells ', length(schnitz_list), num_frames, length(Ycells));
%disp(report)
end

