ds = tabularTextDatastore('OldVivaldiDataOutput.csv');
tt = tall(ds);
write('/mnt/memmap/result',tt);
