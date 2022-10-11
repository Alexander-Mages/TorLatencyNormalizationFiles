%uses relative paths, only works in it's current position at TorLatencyNormalizationFiles/ExperimentScripts/phoenixCoordinates/matTOcsv.m,
%given that data_matrix.mat is @ TorLatencyNormalizationFiles/ExperimentScripts/phoenixCoordinates/NCSim/data_matrix.mat
load('NCSim/data_matrix.mat');
DATA = Toread;
disp(DATA);
%csvwrite('data_matrix.csv', Toread);
