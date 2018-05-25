function [goodframes, Ctrack, RMtrack, YMtrack ] = get_good_frames_of_movie_rfp(pt, st, cell_num, RFP_var_thresh)
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
    mask = Ctrack>cell_num;
    var = std(RMtrack(mask))^2;
    if var > RFP_var_thresh 
        goodframes = [];
    else 
        goodframes = find(mask);
    end
end

function [ outputs ] = test_get_good_frames_of_movie()
%%
run file_lists.m
 
schnitz_list = all_list; %(5:5);
schnitz_list = delRU_list;


figure;
labs = []; 
labt = cell(1,length(schnitz_list));
cc = winter(length(schnitz_list));

for s = 1:length(schnitz_list)
    pt = schnitz_list(s);
    pt.frames = 1:max(pt.frames);
    [pt, st] = compileschnitz(pt, 'load', true);
    
    [good_frames, Ctrack, RMtrack, YMtrack ] = get_good_frames_of_movie_rfp(pt, st, 20, 40);

    plot_line = RMtrack;
    masked_line = plot_line;
    goodframe = ismember(pt.frames, good_frames);
    rawmask = Ctrack > 20;
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
    label = [ pt.movieName ' ' sprintf('%f', std(plot_line(rawmask),'omitnan')^2)];
    labt(s) =  {label};
    %disp([' my name is ' label ' ' sprintf('%f',sum(YMtrack))])
    disp(good_frames)

end
legend(labs, labt{:}, 'interpreter','none');
%%
 
end

