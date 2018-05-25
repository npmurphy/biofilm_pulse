run file_lists.m

rback = mean([174, 173, 191, 191, 174, 173, 174, 172, 174, 173, 174, 172, 178, 176, 176, 174, 172, 173]);
yback = mean([250, 252, 228, 225, 226, 223, 226, 223, 227, 224, 226, 223, 226, 223, 227, 223, 222, 223]);
% for each files in the all_files list, load the mat file.
for j = 1:length(all_list)
    p = all_list(j);
    p.lineageName = [p.tracksDir,p.movieName,'_lin.mat'];

    %ppath = [ st.tracksDir '/' st.movieName '-Schnitz.mat' ];
    w=load(p.lineageName);
    schnitzcells=w.schnitzcells;
    trackRange = sort(unique([schnitzcells.frames])) - 1;
    for i = 1:length(trackRange)
        currFrameNum = trackRange(i);
        spath = [p.segmentationDir,p.movieName,'seg', str3(currFrameNum) '.mat'];
        %% commented out in case this is run again and we lose the previous stucts.
        %[status, message, messageId] = copyfile(spath, [spath '_wrongbgsub'] , 'f');
        if status ~= 1 
            disp(message)
            break
        else 
            %s = load(spath) %, 'schnitzcells')
            m = matfile(spath, 'Writable', true);
            m.rback = rback;
            m.yback = yback;
        end 
    end
end        
%         if any(strcmp('yback',fieldnames(schnitzcells)))
%                         disp(schnitzcells.rback) % = rback;
%         end
%         i;

%             %m = matfile(spath, 'Writable', true);
%             load(spath, 'schnitzcells')
%             if any(strcmp('yback',fieldnames(schnitzcells)))
%                 disp(schnitzcells.rback) % = rback;
%             end
%             %schnitzcells.yback = yback;
%             %save(spath, 'schnitzcells')
%         end

% % copy the file to a new name. 
% %Modify the values. save the mat file. 
% x = 10
% y = 49
% pathf = '/tmp/test.m';
% save(pathf,'x', 'y');
% 
% [status,message,messageId] = copyfile('myfile1.m', 'restricted\myfile2.m', 'f')
% m = matfile(pathf, 'Writable', true);
% m.x
% m.y
% m.x = 11


