run file_lists.m

%%
fig = figure ();
hold on;
this_list =  RFPonly_list
%this_list =  [ delSigB_list; RFPonly_list]


colors = {'b', 'k', 'm', 'g', 'r'}

count = 1;
plots = {};
labels = {};
%c = colors{li};
cm = jet(length(this_list));

totalR = [];
totalY = [];

for pn = 1:length(this_list)
    p = this_list(pn);
    [p s] = compileschnitz(p, 'load', 1);
    meanR = zeros(1,max(p.frames));
    meanY = zeros(1,max(p.frames));
    numC = zeros(1,max(p.frames));
    for f = 1:max(p.frames)
        [My Mr] = snapcompress(f, s);
        meanR(f) = mean(Mr);
        meanY(f) = mean(My);
        numC(f) = length(Mr);
    end
    
    mask = numC>20;
    plotchan = meanY;
    
    totalY = [totalY meanY(mask)];
    totalR = [totalR meanR(mask)];

    
    fram = 1:max(p.frames);
    c = cm(pn,:);
    plot(fram, plotchan, ':', 'Color', c)
    pl = plot(fram(mask), plotchan(mask), 'o-', 'Color', c);
    
%     plot(numC, plotchan, ':', 'Color',c); % cm(pn,:));
%     pl = plot(numC(mask), plotchan(mask), 'o-', 'Color', c);

    plots{1,count} = pl;
    labels{1,count} = [ p.movieName ];
    count = count+1;
end
legend([plots{:}], labels{:}, 'Interpreter', 'none');

figure()
histogram(totalY, 'FaceColor','g');
figure()
histogram(totalR, 'FaceColor','r');


disp(mean(totalchan))

%%