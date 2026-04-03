%% har laget denne funksjonen til parsing av data fra python til matlab
%% Mac students use version 2016b which doesn't support normal parsing
function [data] = ParseData(filename)
    file = strcat( '../Data/',filename);
    opts = detectImportOptions(file);
    opts.VariableNamesLine = 1;
    opts.DataLine = 3;
    T = readtable(file,opts);
    header = importdata(file,',',1);
    header = char(header);
    header = erase(header,'=meas');
    header = erase(header,'=calc');
    header = textscan(header,'%s','Delimiter',',')';
    header = header{:}';
    Data = T.Variables;
    for i = 1:length(header)
       c = Data(:,i);
       verdier = c(~isnan(c));
       key = char(header(i));
       data(1).(key) = verdier;
    end
end