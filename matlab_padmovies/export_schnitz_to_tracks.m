function p = export_schnitz_to_tracks(p, outfile) 

%p.load = 1; % dont recimpile schnitzes 
[p, schnitzcells] = compileschnitz(p);

list_of_cells = find(([schnitzcells.D]==0)&([schnitzcells.approved]==1));

record_fields = {'frames','MY','MR'};
blanks = {[],[],[]};

for si = 1:length(list_of_cells)
    original_daughter = list_of_cells(si);
    
    cell_data = cell2struct(blanks, record_fields, 2);
    cell_data.cells = [];
    
    for field = record_fields
        thisone = list_of_cells(si); % will change to subsequent parents
        X = [];
        done = 0;
        while ~done, 
            x = getfield(schnitzcells(thisone), field{:});
            x = x(end:-1:1);
            X = cat(2,X,x);

            thisone = schnitzcells(thisone).P;
            done = (thisone <=0);
        end;
        X = X(end:-1:1);
        cell_data = setfield(cell_data, field{:}, X);
    end
    cell_data = setfield(cell_data, 'cells', ones(size(X))*original_daughter);
    struct_to_tsv(outfile, cell_data, si==1);
end


end