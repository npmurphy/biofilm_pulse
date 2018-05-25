run file_lists.m

%%
fig = figure ();
c = 0 
hold on;
joint_lists = { delRU_low_mean delSigB_list delQP_list sigB_list RFPonly_list}
%joint_lists = {  RFPonly_list}

colors = {'b', 'k', 'm', 'g', 'r'}
%colors = {'r'}
vars = []; 

count = 1;
plots = {};
labels = {};
for li = 1:length(joint_lists) 
    %li = 2;
    this_list = joint_lists{li};
    %this_list = delRU_high_mean
    c = colors{li};
    cm = jet(length(this_list));
    %plots = cell(1,length(this_list));
    %labels = cell(1,length(this_list));
    for pn = 1:length(this_list) %(1:1)
        p = this_list(pn);
        [ p s] = compileschnitz(p, 'load', 1);
        disp(sprintf('%s', p.movieName));
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
        var = std(meanR(mask))^2;
        vars = [vars var];
        %plot(numC, meanR, '--', 'Color', c)
        %disp(sprintf('%d %d', length(p.frames), length(meanY)))
        fram = 1:max(p.frames);
        plot(fram, meanR, ':', 'Color', c)
        if (var) > 40
            pl = plot(fram(mask), meanR(mask), 'o-', 'Color', c);
            plots{1,count} = pl;
            labels{1,count} = [ p.movieName sprintf('%f', var)];
            count = count+1;

        end
        %pl = plot(numC, meanR, 'o-', 'Color', cm(pn,:));

    end
end
legend([plots{:}], labels{:}, 'Interpreter', 'none');

%%
