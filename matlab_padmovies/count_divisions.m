function count = count_generations( s, c )
    if s(c).P == 0
        count = 0;
    else 
        count = 1 + count_generations(s, s(c).P);
    end
end

