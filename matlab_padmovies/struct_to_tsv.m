function [] = struct_to_tsv(filename, data, header)
    
    raw = cell2mat(struct2cell(data(:)))';

    if header
        fd = fopen(filename, 'w');

        if fd == -1
            error(['Could not open ' filename ' for writing.']);
        end
        labels = fieldnames(data(1));

        if nargin < 3 || header
            fprintf(fd, '%s\n', strjoin(labels, '\t'));
        end
        fclose(fd);
    end

    dlmwrite(filename, raw, '-append', 'delimiter','\t');

    
end 