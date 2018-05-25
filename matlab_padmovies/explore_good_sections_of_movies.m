
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
 
%% Plot the YFP over time 
%v = 8;
schnitz_list = delRU_list;%(v:v);
%schnitz_list = [ sigB_list;  delRU_list];%(v:v);
%schnitz_list = RFPonly_list;%(v:v);
%schnitz_list = delSigB_list;%(v:v);


figure;
labs = []; 
labt = cell(1,length(schnitz_list));
cc = parula(length(schnitz_list));
%cc = rainbow(length(pt.frames));

for s = 1:length(schnitz_list)
    disp(sprintf('about ot load %d', s))
    pt = schnitz_list(s);
    pt.frames = 1:max(pt.frames);
    [pt, st] = compileschnitz(pt, 'load', true);
    YMtrack = zeros(1,length(pt.frames));
    YStrack = zeros(1,length(pt.frames));
    RMtrack = zeros(1,length(pt.frames));
    RStrack = zeros(1,length(pt.frames));
    Ctrack = zeros(1,length(pt.frames));
    for fi = 1:length(pt.frames)
        [Ymean, Rmean] = snapcompress(pt.frames(fi),st);
        YMtrack(fi) = mean(Ymean);
        YStrack(fi) = std(Ymean);
        RMtrack(fi) = mean(Rmean);
        RStrack(fi) = std(Rmean);
        Ctrack(fi) = length(Rmean);
    end
    plot_line = YMtrack; %(2:end);
    goodgen = log2(Ctrack) <= 3;
    fst = find(~goodgen,1);
    %th = atan( (YMtrack(fst) - YMtrack(end)) / (pt.frames(end) - pt.frames(fst)));
    %disp(sprintf('%f / %f', (YMtrack(fst) - YMtrack(end)) , (pt.frames(end) - pt.frames(fst))))
    %dg = 90 - rad2deg(th);
    mdg = atand( ((YMtrack(fst) - YMtrack(end))/1400) / (((pt.frames(end) - pt.frames(fst)))/pt.frames(end)));

    %disp( th);
    %disp(90 - dg)
    disp(mdg)

    
    plot_line(goodgen) = nan;
    mx = max(plot_line);
    mend = max(plot_line(end));
    hold on

    hold on
    p2 = plot(pt.frames, YMtrack);
    hold on 
    p1 = plot(pt.frames, plot_line);
    hold on 

    set(p1,'Color',cc(s,:));
    set(p2,'Color',cc(s,:));
    set(p2, 'linestyle',':');
    
    if mdg > (15);
        set(p1,'Color','r');
        set(p2,'Color','r');
    end
    hold on 

    labs = [ labs; p1]; 
    label = [ pt.movieName sprintf(' %.02f', mdg)];
    labt(s) =  {label};
    disp([' my name is ' label ' ' sprintf('%f',sum(YMtrack))])
end
legend(labs, labt, 'interpreter','none');

%%
p =  delRU_list(6)
%p = manualcheckseg(p, 'override', 1, 'manualRange',  p.frames, 'view_channel', 'y');
% p.trackRange = p.frames;
% p = trackcomplete(p);
[p,schnitzcells] = compileschnitz(p);
% %agg_hist_of_multiplesnaps(delRU_list(5:5), '', 20, false);
%%
         
delQP_list = [ 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-B_1', 1:20 )  % SIC
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-B_3', 1:25 ) % SIC
       make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-delRU_3', 1:25) % SIC
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_1' , 1:29)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_2' , 11:33) % ignored a cell
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_5' , 1:35) %ignored a bright cell
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_6' , 1:29)
       %make_schitzd('sigB_biofilmfinal-DelQP_7' , 1:36)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_9' , 12:33)
 ];

% p =  delQP_list(7)
% p = manualcheckseg(p, 'override', 1, 'manualRange',  p.frames(1:end), 'view_channel', 't');
% p.trackRange = p.frames;
% p = trackcomplete(p);
% [p,schnitzcells] = compileschnitz(p);

%%     
sigB_list = [ 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-QP_1', 25:55) %SIC
    %make_schitz('sigB_biofilmfinal-B_2',  1:45) Where is this?
    make_schitz('2015-11-03', 'sigB_biofilmfinal-B_3',  21:42)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_4',  1:39)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_6',  21:37)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_7',  1:37)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_8',  1:35)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_9',  14:37 )
    ]
p =  sigB_list(2)
p = manualcheckseg(p, 'override', 1, 'manualRange',  p.frames(1:end), 'view_channel', 'y');
p.trackRange = p.frames;
p = trackcomplete(p);
[p,schnitzcells] = compileschnitz(p);
%%

RFPonly_list = [ 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-RFP_3', 1:50)
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-RFP_3', 1:27)
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-RFP_8', 1:24)
    ] 

%  
delSigB_list = [
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_2', 1:19) % SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_3', 1:26)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_4', 1:23)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_5', 1:24)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_6', 1:25)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_7', 1:27)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_8', 1:15)% SIC
]

agg_hist_of_multiplesnaps(delRU_list, 'delRU', 80,true);


agg_hist_of_multiplesnaps(delQP_list, 'delQP', 80, true);
agg_hist_of_multiplesnaps(sigB_list, 'sigB', 80,true);
agg_hist_of_multiplesnaps(delSigB_list, 'delSigB', 89, true);


indiv = delRU_listq
for i = 1:length(indiv)
    [ fg, rhandle, yhandle] = agg_hist_of_multiplesnaps(indiv(i:i), '', 50, true);
    disp(i)
    set(fg,'numbertitle','off','name',indiv(i:i).movieName) % See the help for GCF
    xlim(rhandle, [0,500]) 
    xlim(yhandle, [0,1000]) 
end

