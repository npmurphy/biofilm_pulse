function [ frames ] = schnitzes_in_frame( s, f )
%schnitzes_in_frame returns a list of schnitzes that are present in frame f
% %   Detailed explanation goes here
frames = find(arrayfun(@(x)(ismember(f+1, x.frames)), s));
end

%schnitzes_in_frame = @(s, f) find(arrayfun(@(x)(ismember(f+1, x.frames)), s));


