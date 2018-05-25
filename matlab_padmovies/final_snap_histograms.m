run file_lists.m

for i = 1:length(all_list)
    p = all_list(i)
    p.yfpOffset = 37.9373;
    %p.trackUnCheckedFrames=1
    [p,s] = compileschnitz(p);
end

%%%
%  Final delRU
%%%
[fg, ~, ~] = agg_hist_of_good_snaps(delRU_list, 'delRU', 10 );
saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/fig1_pad_delru.pdf', 'pdf')

% Old Measure (YFP slope) of how many good frames there are
% sigB_biofilmfinal-DelRU_1_1	 11	 97
% sigB_biofilmfinal-DelRU_3_1	 8	 63
% sigB_biofilmpadrepeat-delRU_2_1	 8	 51
% sigB_biofilmfinal-DelRU_10_1	 3	 18
% sigB_biofilmpad6-O001_3_1	 10	 59

%  sigB_biofilmfinal-DelRU_1_1 has an ignored cell so we do 
% a full schnitz track on sigB_biofilmpad6-O001_3_1
%p = delRU_list(5);

%%%%%%%%%%%%%%%%%%%%
%%%%%%
%%%%%%  DelQP
%%%%%%
%%%%%%%%%%%%%%%%%%%%
[fg, ~,~] = agg_hist_of_good_snaps(delQP_list, 'delQP', 10);
saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/fig1_pad_delqp.pdf', 'pdf')

%longest_good_runs(delQP_list);
% 2015-10-30/ sigB_biofilmpadrepeat-B_1_1	 8	 25
% 2015-10-30/ sigB_biofilmpadrepeat-B_3_1	 4	 18
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-delRU_3_1	 0	 6
% 2015-11-03/ sigB_biofilmfinal-DelQP_1_1	 9	 50
% 2015-11-03/ sigB_biofilmfinal-DelQP_2_1	 9	 61
% 2015-11-03/ sigB_biofilmfinal-DelQP_5_1	 9	 53
% 2015-11-03/ sigB_biofilmfinal-DelQP_6_1	 5	 21
% 2015-11-03/ sigB_biofilmfinal-DelQP_9_1	 10	 80

% sigB_biofilmfinal-DelQP_9_1 looks perfect, lets shnitz it
%p = delQP_list(8);


%%%%%%%%%%%%%%%%%%%%
%%%%%%
%%%%%%  SigB
%%%%%%
%%%%%%%%%%%%%%%%%%%%
%%     

% Longest good runs 
% sigB_biofilmpadrepeat-QP_1_1	 8	 33
% sigB_biofilmfinal-B_3_1	 0	 87
% sigB_biofilmfinal-B_4_1	 12	 83
% sigB_biofilmfinal-B_6_1	 10	 70
% sigB_biofilmfinal-B_7_1	 6	 32
% sigB_biofilmfinal-B_8_1	 9	 33

% sigB_biofilmfinal-B_4_1 has an ignored bright cell, so going for 
% sigB_biofilmfinal-B_6_1 % This didnt have many spikes. :(

[fg, ~,~] = agg_hist_of_good_snaps(sigB_list, [ 'sigB' ' ' p.movieName], 10);
saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/fig1_pad_sigb.pdf', 'pdf')


%%%%%%%%%%%%%
%%%
%%% DelSigB
%%%
%%%%%%%%%%%%%

[fg, ~,~] = agg_hist_of_good_snaps(delSigB_list, [ 'DelSigB' ' ' p.movieName], 10);
saveas(fg, '/home/nmurphy/work/projects/stochastic/paper/fig1_pad_sigb.pdf', 'pdf')
longest_good_runs(delSigB_list);

% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_2_1	 7	 30
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_3_1	 10	 51
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_4_1	 8	 35
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_5_1	 6	 28
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_6_1	 12	 70 
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_7_1	 8	 40
% 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_8_1	 4	 16
% 2015-11-03/ sigB_biofilmfinal-DelB_1_1	 12	 76 % starts at 21
% 2015-11-03/ sigB_biofilmfinal-DelB_6_1	 8	 35
% 2015-11-03/ sigB_biofilmfinal-DelB_10_1	 12	 98 % we ignore lots of cells

% Lets try tracking this one 2015-10-31/ sigB_biofilmpadrepeatrepeat1-sigB_6_1	 12	 70 


%%%%%%%%%%%%%%%%%%%%%%%%
%%% Full Schnitz track
%%%%%%%%%%%%%%%%%%%%%%%%
% Doing a fill Schnitz track
%p = delRU_list(5);
%p =  sigB_list(3);
%p = delQP_list(8);
p = delSigB_list(5);
p.yfpOffset = 0;
%schnitzes_in_frame(s, max(p.frames))

%
[p,s] = compileschnitz(p);
debugschnitz(s)
find(([s.P]==0)) % IDs of orphans
find(([s.approved]==0)) % IDs of unapproved
[ length(find(([s.approved]==0))), length(s)] % IDs of unapproved

%find([s(([s.D]==0)& ([s.E]==0)).B]<35) % Birth time of barren cells 
plot_schnitzes(p, 25:28)
p = schnitzedit(p)
%%
%%
[p,s] = compileschnitz(p);
%[goodframes, ~, ~, ~ ] = get_good_frames_of_movie(p, s, 3, 15, 1400);
% %p.frames = goodframes;
p.frames
p.trackRange = p.frames;

p = manualcheckseg(p, 'override', 1, 'manualRange', p.frames, 'view_channel', 't');
%p = trackcomplete(p);
p = trackcomplete(p,'override', 1);
[p,s] = compileschnitz(p, 'load', true);

debugschnitz(s)

x = schnitzes_in_frame(s, p.frames(end))

lookat = []
plotschnitzme(s, 'frames', 'MY', lookat, 'go-');
hold on 
plotschnitzme(s, 'frames', 'MR', lookat, 'ro-');
hold on 
plotschnitzme(s, 'frames', 'len', lookat,'ko-');
hold on 

%%




% Check the number of schintzes in each frame
% for pi = 1:length(delRU_list)
    %p = delRU_list(pi);
    %p =  sigB_list(4);
    %[p, s] = compileschnitz(p, 'load', true);
    for frame_number = p.frames
        segpath = [p.segmentationDir filesep p.movieName 'seg' sprintf('%03d', frame_number) '.mat'];
        load(segpath);
        num_cells = length(unique(Lc)) -1; 
        count = length(schnitzes_in_frame(s, frame_number));
        disp(sprintf('%d %d', num_cells, count))
    end 
% end 



%%

%%
%%%%%%%%%%%%%%%
% Remove a frame from schnitz
%%%%%%%%%%%%%%%%%%
% for si = 1:length(s)
%     sch = s(si);
%     if ismember( 33, sch.frames)
%         s(si).frames = setdiff(sch.frames, [33]);
%     end
% end
% save(p.schnitzName, 's','-append');


%%%%%%%%%%%%%%%%
%%%
%%% Check individual files 
%%%
%%%%%%%%%%%%%%%
total_list = RFPonly_list
name = 'sigB'
for pi = 1:length(total_list)
    p = total_list(pi);
    [p, s] = compileschnitz(p, 'load', true);
    [goodframes, ~, ~, ~ ] = get_good_frames_of_movie(p, s, 3, 15, 1400);
    if ~isempty(goodframes)
        [R_cells, Y_cells] = good_sections_of_movies(p, 3, 15, 1400);
        [Ymean, Rmean] = snapcompressrange(s, min(goodframes), max(goodframes));
        disp(sprintf('%s %f', p.movieName, mean(Rmean)))
        [fg, rh, lh] = agg_hist_of_good_snaps_comp_james(p, [ name ' ' p.movieName], 10);
        saveas(fg, [ '/tmp/' name '_' p.movieName  '.png'], 'png');
        
        if all(sort(Ymean) ~= sort(Y_cells)) 
            error('snap schnitz doesnt agree with with snapschnitz range')
        end
    end
end 

%% Another way to look at individual files

indiv = delRU_listq
for i = 1:length(indiv)
    [ fg, rhandle, yhandle] = agg_hist_of_multiplesnaps(indiv(i:i), '', 50, true);
    disp(i)
    set(fg,'numbertitle','off','name',indiv(i:i).movieName) % See the help for GCF
    xlim(rhandle, [0,500]) 
    xlim(yhandle, [0,1000]) 
end
%%




    
%%%%%%%%%%%%
%%% Fixing segmentations
%%%%%%%%%%%%
lookingat = RFPonly_list
p = lookingat(5)
%p.segRange = 15:16
%p = segmoviefluor(p);
p = manualcheckseg(p, 'override', 1, 'manualRange',  p.frames, 'view_channel', 't');
plotschnitzme(s, 'frames', 'MR',[])
plotschnitzme(s, 'frames', 'MY',[])
% p = manualcheckseg(p, 'override', 1, 'manualRange',  p.frames(1:end), 'view_channel', 'y');
% p.trackRange = p.frames;
% p = trackcomplete(p);
% [p,schnitzcells] = compileschnitz(p);
%%

