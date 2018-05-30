
function [lineage] = get_cell_ancestors(schnitzcells, thisone)
    lineage = [];
    done = 0;
    while ~done,
        lineage = [ thisone, lineage,  ]; 
        thisone = schnitzcells(thisone).P;
        done = (thisone <=0);
    end;   
end