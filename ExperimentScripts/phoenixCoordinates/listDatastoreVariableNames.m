
clear

ds = tabularTextDatastore('/mnt/memmap/OldVivaldiDataOutput.csv');

% ds.TreatAsMissing = '0';



DATA = tall(ds);

preview(DATA);