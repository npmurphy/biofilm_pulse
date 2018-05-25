function [ output_args ] = longest_good_runs( total_list )
%longest_good_runs  Longest run of each strain

st = '';
for pi = 1:length(total_list)
    p = total_list(pi);
    p.load = 1;
    [p, s] = compileschnitz(p); %, 'load', true);
    [goodframes, cell_counts, ~, ~ ] = get_good_frames_of_movie(p, s, 3, 15, 1400);
    
    st = [st sprintf('%s\t %d\t %d\n', [ p.dateDir ' ' p.movieName], length(goodframes),cell_counts(end))];
end
disp(st)

end

