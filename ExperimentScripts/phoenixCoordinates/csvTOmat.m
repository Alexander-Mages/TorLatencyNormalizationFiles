T=readtable('OldVivaldiDataOutput.csv');
p=T{:,1};
q=T{:,2};
save('OldVivaldiDataset.mat','p','q')
