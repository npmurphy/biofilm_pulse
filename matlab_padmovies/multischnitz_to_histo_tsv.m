function [] = multischnitz_to_histo_tsv( strain_list , datafilename, filemapname)

fileID = fopen(filemapname, 'w');
for sn = 1:length(strain_list) 
    schnitz = strain_list(sn);
    fprintf(fileID, sprintf('%d\t%s\t%s\n', sn, schnitz.movieName,schnitz.movieDate));

    [R_cells, Y_cells, R_cells_mn, Y_cells_mn, report] = good_sections_of_movies([schnitz], 3, 15, 1400);
    schnitz_vals.MR = R_cells;
    schnitz_vals.MY = Y_cells;
    schnitz_vals.Number = ones(size(R_cells))*sn;

    struct_to_tsv(datafilename, schnitz_vals, sn==1);

end    

fclose(fileID);

end

