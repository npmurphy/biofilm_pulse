function [ figrefs ] = plot_schnitzes( p, want_frames )
% this function draws the frames of the movie and colors each cell the same
% in each frame (except if the cell divides), numbers are overlaid to make
% to help find that schnitz later
%% Plot centroids over segmented image
[p,s] = compileschnitz(p);
cmap = [ [0, 0, 0]; rand(length(s),3); [1, 1, 1]];
figrefs = [];
for want_frame = want_frames
    fr = figure('name',sprintf('Frame %d', want_frame));

    segpath = [p.segmentationDir filesep p.movieName 'seg' sprintf('%03d', want_frame) '.mat'];
    load(segpath);
    
    shnum = schnitzes_in_frame(s, want_frame);
    xx = [];
    yy = [];
    sch_seg = Lc;
    niall = 0;
    for si = shnum
        subind = find(s(si).frames==(want_frame+1));
        x = s(si).cenx(subind);
        y = s(si).ceny(subind);
        xx = [xx x];
        yy = [yy y];
        niall = niall +1
        if niall == 29
            disp('yo')
        end
        if ~isnan(y)  
            oldcol = Lc(floor(y), floor(x));
            mask = Lc==oldcol;
            sch_seg(mask) = si;
        end
    end
    
    imshow(sch_seg, cmap)
    hold on
    scatter( xx, yy)
    hold on
    shnum_str = cellstr(num2str(shnum'));
    dx = 0.1; dy = 0.1; % displacement so the text does not overlay the data points
    text(xx+dx, yy+dy, shnum_str, 'color', 'w');
    hold on %off
    pause(1)
    figrefs = [figrefs fr];
end

end

