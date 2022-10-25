import sys
import os
import re
#https://pypi.org/project/shove/
#from shove import Shove
import shelve
#import gc

#parses the dataset at https://zenodo.org/record/4911583

paths = sys.argv[1]
relayInfo = sys.argv[2]
probedRelays = sys.argv[3]
outputDirectory = sys.argv[4]


#remove lines with data marked 3 (theoretic estimation)
#noTheoreticPathsFile = []
# with open(paths) as paths:
#     searchstr = re.compile(r"^\d{1,4}\s\d{1,4}\s(\d+)")
#     linecount = 0
#     for line in paths:
#         if linecount % 20 == 0:
#             print(linecount)
#         linecount += 1
#         searchResult = re.search(searchstr, line)
#         num = searchResult.group(1)
#         if re.search(searchstr, line).group(1) == '3':
#             noTheoreticPathsFile.append(line)
#
#     paths.close()
#with open(paths) as paths:
#    noTheoreticPathsFile = paths.readlines()
#paths.close()

relayInfoDict = {}
with open(relayInfo) as relayInfo:
    searchstr2 = re.compile(r"^([^\s]+)\s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})")
    for line in relayInfo:
        searchResult = re.search(searchstr2, line)
        fingerprint = searchResult.group(1)
        IPaddr = searchResult.group(2)
        relayInfoDict[fingerprint] = IPaddr
#    relayInfo.close() #I don't think this is needed when using "with"


#associate relayid in paths file with fingerprint.
probedRelaysDict = {}
with open(probedRelays) as probedRelays:
    searchstr3 = re.compile(r"^(\d{1,4})\s(.+)")
    for line in probedRelays:
        searchResult = re.search(searchstr3, line)
        relayId = searchResult.group(1)
        fingerprint = searchResult.group(2)

        probedRelaysDict[relayId] = relayInfoDict[fingerprint]
    #probedRelays.close() #I don't think this is needed when using "with"

del relayInfoDict
#gc.collect()


#noTheoreticDict = {}
with shelve.open((os.path.join(outputDirectory, "../", "noTheoreticDictBackingStore.shelved"))) as noTheoreticDict:
    searchstr4 = re.compile(r"^(\d{1,4})\s(\d{1,4})\s\d\s(.+)")
    with open(paths) as paths:
        for entry in paths.readlines():
    #for entry in noTheoreticPathsFile:
            searchResult = re.search(searchstr4, entry)
            sourceRelayId = searchResult.group(1)
            destRelayId = searchResult.group(2)
            latencies = searchResult.group(3)

            #replace relayID with fingerprint
            sourceRelayIP = probedRelaysDict[sourceRelayId]
            destRelayIP = probedRelaysDict[destRelayId]

            key = sourceRelayIP + "," + destRelayIP
            noTheoreticDict[key] = latencies.split(",")
            #noTheoreticDict.sync() if using "Writeback=True" as a shelve option
    #paths.close() #I don't think this is needed when using "with"
    del probedRelaysDict
    #del noTheoreticPathsFile

    #gc.collect()

    #outputDirectory
    i, j = zip(*noTheoreticDict.keys())
    assert len(i) == len(j), "asymmetric matrix"
    a = np.zeros((len(i)+1,len(j)+1), dtype=np.float64)
    # a = zarr.zeros((len(i)+1,len(j)+1), dtype=np.float64) #couldn't figure out how to initialize the matrix w/ zeros in zarr
    a = np.memmap('/mnt/memmap/memmapedArrayVOIP.dat', dtype=np.float64, mode='w+', shape=(len(i) + 1, len(j) + 1))
    # mode w+ acts as np.zeros. here's a comment from numpy's memmap.py code:
    # When a memmap causes a file to be created or extended beyond its current size in the filesystem, the contents of the new part are
    # unspecified. On systems with POSIX filesystem semantics, the extended part will be filled with zero bytes.
    print(len(j))
    print("the above should be 111403 (for old vivaldi data), if so, then it should be used as a variable in the np.arange call.")
    np.add.at(a, np.arange(0, 111403, 1), tuple(l.values()))

    #for key in noTheoreticDict:
        #source = key.split(",")[0]
        #dest = key.split(",")[1]

        #filePath = os.path.join(outputDirectory, source + ".txt")
        # #if not os.path.exists(filePath):
        # try:
        #     with open(filePath, "x") as f:
        #         #f = open(filePath, "x") #will error if file exists
        #         f.write(source + "\n") #writes source IP to top of file
        #         for latency in noTheoreticDict[key]:
        #             latencyInMilliseconds = int(latency)/1000
        #             f.write("64 bytes from " + dest + ": icmp_seq=0 ttl=50 time=" + str(latencyInMilliseconds) +  " ms\n")
        # #else:    #append to it
        # except FileExistsError:
        #     with open(filePath, "a") as f: #will not error if the file exists, will append
        #         #f = open(filePath, "a") #will not error if the file exists, will append
        #         for latency in noTheoreticDict[key]:
        #             latencyInMilliseconds = int(latency)/1000
        #             f.write("64 bytes from " + dest + ": icmp_seq=0 ttl=50 time=" + str(latencyInMilliseconds) +  " ms\n")
        #f.close() #I don't think this is needed when using "with"

#noTheoreticDict.close() #I don't think this is needed when using "with"
