function [ output_args ] = my_pdf_save(fig, file_name, width, height, fontsize )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
fig = gcf;
fig.Units = 'centimeters';
fig.PaperUnits = 'centimeters';
fig.PaperPositionMode = 'manual';
fig.PaperSize = [width height];
fig.PaperPosition = [0 0 fig.PaperSize(1:2)];
fig.Position = [0 0 fig.PaperSize(1:2)];
fig.PaperType = '<custom>';

allAxesInFigure = findall(fig,'type','axes');
for a = 1:length(allAxesInFigure)
    axes = allAxesInFigure(a);
    axes.FontUnits = 'points';
    axes.FontWeight = 'normal';
    axes.FontSize = fontsize;
    %fig.FontName = 'Times'
end
dpi = 300;
print(fig,'-dpdf',file_name, sprintf('-r%d',dpi));

end

