function  [Rcells, Ycells, RcellsMeanNorm, YcellsMeanNorm, report] = last_cells_of_movie(schnitz_list)
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
    % PT is meta info about the movie.
    % st has an entry for every cell, including what frames it appears in
    % we have to go through every cell and check what 
    last_frame = pt.frames(end);
    [Ymeans, Rmeans] = snapcompress_frames([last_frame], st);
    
    num_frames = num_frames + 1; 
    Ycells = [ Ycells Ymeans];
    Rcells = [ Rcells Rmeans];
    YcellsMeanNorm = [ YcellsMeanNorm (Ymeans/mean(Ymeans))];
    RcellsMeanNorm = [ RcellsMeanNorm (Rmeans/mean(Rmeans))];

end
report = sprintf(' looked at %i files with %i total frames\n \t there were %i cells ', length(schnitz_list), num_frames, length(Ycells));
%disp(report)
end

