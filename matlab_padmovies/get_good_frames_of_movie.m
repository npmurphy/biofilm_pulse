function [all_enough_gens, Ctrack, RMtrack, YMtrack ] = get_good_frames_of_movie(pt, st, logcell_num, angle, YFP_scale)
%% This function tries to be really smart about which movies and frames to consider. 
%% a movie should have experienced enough generations (logcell_num)
%% Then it tries to detect the YFP mean intensity dropping due to bleaching 
%% or something and discards movies with a sharp decline. 
    % To avoid calculating indexes for frames we care about and 
    % the arrays we store them in, I just create an array of the full size.
    RMtrack = zeros(1,max(pt.frames));
    YMtrack = zeros(1,max(pt.frames));
    Ctrack = zeros(1,max(pt.frames));
    
    for fi = pt.frames
        [Ymean, Rmean] = snapcompress(fi, st);
        YMtrack(fi) = mean(Ymean);
        RMtrack(fi) = mean(Rmean);
        Ctrack(fi) = length(Rmean);
    end
    enough_gens = log2(Ctrack) > logcell_num;
    fst = find(enough_gens,1);
    all_enough_gens = find(enough_gens);
    yfp_drop = ((YMtrack(fst) - YMtrack(end))/YFP_scale);
    time_span = ((pt.frames(end) - fst))/pt.frames(end);
    mdg = atand(yfp_drop/time_span);
    
    if mdg > angle; 
        all_enough_gens = []; 
    end
end

function [ outputs ] = test_get_good_frames_of_movie()
%%
basedir = '/media/nmurphy/giant_ext4/biofilm_fig1/';
make_schitz = @(date, name, frames) create_new_schnitzobj(basedir, date, name, frames);

delRU_list = [ %make_schitz('2015-10-29', 'sigB_biofilmpad6-O001_2', 25 ) 
       make_schitz('2015-10-29', 'sigB_biofilmpad6-O001_3', 3:32 ) 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_1', 1:36); 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_2', 21:36); %(ignoring bright cell) 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_6', 1:31); %(ignoring bright) 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_8', 22:31); 
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_1', 25:41) %(bright cell until frame 25)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_3', 21:38)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_4', 1:41) % (bright cells, left alone)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_5', 21:36)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_10' , 1:40) % slow few cells, some very bright
     ];
 
schnitz_list = delRU_list; %(5:5);

figure;
labs = []; 
labt = cell(1,length(schnitz_list));
cc = parula(length(schnitz_list));

for s = 1:length(schnitz_list)
    pt = schnitz_list(s);
    pt.frames = 1:max(pt.frames);
    [pt, st] = compileschnitz(pt, 'load', true);
    
    [good_frames, Ctrack, RMtrack, YMtrack ] = get_good_frames_of_movie(pt, st, 3, 15, 1400);

    plot_line = YMtrack;
    masked_line = YMtrack;
    goodframe = ismember(pt.frames, good_frames);
    masked_line(~goodframe) = nan;

    %fst = find(goodframe,1);
    
    hold on
    ppl = plot(pt.frames, plot_line);
    hold on 
    pml = plot(pt.frames, masked_line);
    hold on 

    set(ppl,'Color',cc(s,:));
    set(pml,'Color',cc(s,:));
    set(ppl, 'linestyle',':');
    
    labs = [ labs; pml]; 
    label = [ pt.movieName];
    labt(s) =  {label};
    disp([' my name is ' label ' ' sprintf('%f',sum(YMtrack))])
    disp(good_frames)

end
legend(labs, labt{:}, 'interpreter','none');
%%
 
end

