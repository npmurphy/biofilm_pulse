%% 
p = delRU_list(5);
[p schintzcells] = compileschnitz(p, 'load', 1);
most_spiky_schnitz = [33 54 61 62 65 66 73 74 75 85 87 93 95 96 97 98 99 104 107 109 110 111 112 117 120 ];
more_unique = [33 54 61 66 73 74 87 98 99 104 111];

%%
p =  sigB_list(4);
[p schintzcells] = compileschnitz(p, 'load', 1);
most_spiky_schnitz = [62 89 90 104 106 108 110 127 142 164 166 167 ];
more_unique = [62 90 106 110 127 142 164 166 167 ];
%%
p =  sigB_list(3);
[p schintzcells] = compileschnitz(p, 'load', 1);

most_spiky_schnitz = [81 83 88 91 93 95 99 104 105 108 110 111 113 116 118 120 121 123 124 126 128 129 131 133 134 136 137 138 139 141 143 145 146 148 149 150 151 153 154 155 156 157 158 159 160 161 163 164 166 168 170 172 173 174 175 176 177 178 179 181 182 184 186 187 188 191 198 ];
more_unique = [81 88 91 93 99 104 105 108 111 113 116 118 120 123 124 128 129 131 133 134 136 137 143 145 148 149 150 151 153 154 156 157 159 160 161 166 170 172 174 175 176 186 191 ];
good = [145 137 159 139 153 120 95];
%%
selection = datasample(more_unique, 5, 'Replace', false);
%selection =good; % datasample(more_unique, 5, 'Replace', false);

%%
p = delQP_list(8);
[p schintzcells] = compileschnitz(p, 'load', 1);
final_schnitz = schnitzes_in_frame(schintzcells, max(p.frames));
nice = [ 53    55    57    87    90   101   117   124   129   134]

%%
p = delSigB_list(5);
[p schintzcells] = compileschnitz(p, 'load', 1);
final_schnitz = schnitzes_in_frame(schintzcells, max(p.frames));
selection = datasample(final_schnitz, 10, 'Replace', false);

%selection = nice; %datasample(final_schnitz, 20, 'Replace', false);

disp(selection)
cmap = jet(length(selection));

figure()
plots = cell(1,length(selection));
labels = cell(1,length(selection));

for si = 1:length(selection)
    s = selection(si);
    hold on 
    [ h, ~, ~, ~] = plotschnitzme(schintzcells, 'frames', 'MY', s, '-', 'HANDLEBACK');
    hold on 
    h.Color = cmap(si,:);
    plots{si} = h;
    labels{si} = sprintf('%d', s);
    
end
legend([plots{:}], labels{:})


%% generate images of all spike trails 
final_schnitz = schnitzes_in_frame(schintzcells, max(p.frames));
cm = jet(length(final_schnitz));
for si = 1:length(final_schnitz)
    sk = final_schnitz(si);
    fg = single_cell_traces(p, sk)
%     sk = final_schnitz(si);
%     figure('name',sprintf('Schnitz %d', sk));
%     [ h, ~, ~, ~] = plotschnitzme(s, 'frames', 'MY', sk, '-', 'HANDLEBACK');
%     h.Color = cm(si,:);
    saveas(fg, sprintf('/tmp/fig1_movie_sigb_%d.png', sk), 'png')    
    close(fg)
end
%%

%% Images that we consider 
[p schintzcells] = compileschnitz(p, 'load', 1);
[goodframes, ~, ~, ~ ] = get_good_frames_of_movie(p, schintzcells, 3, 15, 1400);

for f = 1:length(goodframes)
    gf = goodframes(f);
    %subplot(2,length(goodframes), f);
    %segpath = [p.segmentationDir filesep p.movieName 'seg' sprintf('%03d', gf) '.mat'];
    impath = [p.imageDir filesep p.movieName sprintf('-y-%03d', gf) '.tif'];
    disp(impath)
    %load(segpath);
    %im = imread(impath, 'tif');
    %imshow(im, []);
    %title(sprintf('Frame %d', gf));
end