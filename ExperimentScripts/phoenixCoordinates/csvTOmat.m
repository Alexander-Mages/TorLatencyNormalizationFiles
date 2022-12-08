ds = tabularTextDatastore('OldVivaldiDataOutput.csv');
tt = tall(ds);
write('/mnt/memmap/result',tt);
%writeall(ds,'OldVivaldiDataset.mat','OutputFormat','mat');
%save('OldVivaldiDataset.mat','p','q')
