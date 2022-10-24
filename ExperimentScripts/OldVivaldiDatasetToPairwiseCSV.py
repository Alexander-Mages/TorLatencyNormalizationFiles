import os
import numpy as np
import re
#import zarr
import pandas as pd

l = {}
root = "/home/alex/ExperimentData/"
for files in os.listdir("/home/alex/ExperimentData"):
    files = os.path.join(root, files)
    with open(files) as f:
        sourceHost = f.readline().rstrip()
        for line in f.read().splitlines():
            line = line.rstrip()  # removes \n newline
            rttMatch = re.search(r'time=(\d+.\d+)', line)
            destHostMatch = re.search(r'from\s(\d+.\d+.\d+.\d+)', line)
            # extracts the "group" from the match object stored in rttMatch and destHostMatch
            try:
                rtt = rttMatch.group(1)
            except AttributeError:
                print("RTT PARSING FAILED, CONTINUING ANYWAY")
                pass
            try:
                destHost = destHostMatch.group(1)
            except AttributeError:
                print("IP PARSING FAILED, CONTINUING ANYWAY")
                pass

            if (sourceHost, destHost) in l:
                # if the host-pair already has a measurement associated with it, another is appended
                l[(sourceHost, destHost)].append(float(rtt))
                # l[(sourceHost, destHost)].append(pcgRandVec())
            else:
                # if no values have been inserted yet, the item is made into a list, with an item appended to it
                l[(sourceHost, destHost)] = [float(rtt)]
                # l[(sourceHost, destHost)] = [pcgRandVec()]


i,j = zip(*l.keys())
assert len(i) == len(j), "asymmetric matrix"
#a = np.zeros((len(i)+1,len(j)+1), dtype=np.float64)
#a = zarr.zeros((len(i)+1,len(j)+1), dtype=np.float64) #couldn't figure out how to initialize the matrix w/ zeros in zarr
a = np.memmap('/mnt/memmap/memmapedArray.dat', dtype=np.float64, mode='w+', shape=(len(i)+1,len(j)+1))
#mode w+ acts as np.zeros. here's a comment from numpy's memmap.py code:
#When a memmap causes a file to be created or extended beyond its current size in the filesystem, the contents of the new part are
#unspecified. On systems with POSIX filesystem semantics, the extended part will be filled with zero bytes.
x = list(range(len(i)))
y = list(range(len(j)))
i = np.arange(0, 111403, 1)
np.add.at(a, i, tuple(l.values()))

with open('output.csv', newline='', dialect='excel') as csvfile:
    w = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    w.writerows(a)
