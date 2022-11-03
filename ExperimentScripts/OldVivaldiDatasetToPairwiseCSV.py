import os
import numpy as np
import re
#import zarr
import csv
import pandas as pd
import sys

l = {}
root = "/home/alex/ExperimentData/"

def parseData():
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


def memEfficientToCSV(memmappedArray, csvWriter, length): #csv writer being the one returned by csv.writer()

    #https://stackoverflow.com/questions/45132940/numpy-memmap-memory-usage-want-to-iterate-once
    chunk_size = 1000 #size of the temporary buffer - I think it's in Mb?
    #empty array to hold this chunk
    holder = np.zeros([chunk_size, length])

    #iterate through array
    for i in range(memmappedArray.shape[0]):
        if i % chunk_size == 0:
            holder[:] = memmappedArray[i:i+chunk_size] #read the chunk
            csvWriter.writerows(holder) #write the chunk to csv




def writeMemmappedArray():
    i, j = zip(*l.keys())
    assert len(i) == len(j), "asymmetric matrix"
    # a = np.zeros((len(i)+1,len(j)+1), dtype=np.float64)
    # a = zarr.zeros((len(i)+1,len(j)+1), dtype=np.float64) #couldn't figure out how to initialize the matrix w/ zeros in zarr
    a = np.memmap('/mnt/memmap/memmapedArray.dat', dtype=np.float64, mode='w+', shape=(len(i) + 1, len(j) + 1))
    # mode w+ acts as np.zeros. here's a comment from numpy's memmap.py code:
    # When a memmap causes a file to be created or extended beyond its current size in the filesystem, the contents of the new part are
    # unspecified. On systems with POSIX filesystem semantics, the extended part will be filled with zero bytes.
    print(len(j))
    print("the above should be 111403, if so, then it should be used as a variable in the np.arange call.")
    np.add.at(a, np.arange(0, 111403, 1), tuple(l.values()))

def readMemmappedArray():
    i, j = zip(*l.keys())
    assert len(i) == len(j), "asymmetric matrix"
    a = np.memmap('/mnt/memmap/memmapedArray.dat', dtype=np.float64, mode='r', shape=(len(i) + 1, len(j) + 1))
    return a, j


def main():
    parseData()
    #writeMemmappedArray()
    filename = "/mnt/memmap/OldVivaldiDataOutput.csv"
    #filename = sys.argv[1]

    #a, j = readMemmappedArray()
    writeMemmappedArray()
    print("writing to csv.. I guess")
    np.savetxt(filename, a, delimiter=',')
    #with open('/mnt/memmap/OldVivaldiDataOutput.csv', newline='', mode='w') as csvfile:
        #w = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        #memEfficientToCSV(a, w, len(j)+1)


if __name__ == "__main__":
    main()