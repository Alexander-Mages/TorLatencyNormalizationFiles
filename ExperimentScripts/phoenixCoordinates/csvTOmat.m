T=readtable('OldVivaldiDataset.csv');
p=T{:,1};
q=T{:,2};
save('OldVivaldiDataset.mat','p','q')
