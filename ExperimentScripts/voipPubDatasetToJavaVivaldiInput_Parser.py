import sys
import os
import re
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
    relayInfo.close()


#associate relayid in paths file with fingerprint.
probedRelaysDict = {}
with open(probedRelays) as probedRelays:
    searchstr3 = re.compile(r"^(\d{1,4})\s(.+)")
    for line in probedRelays:
        searchResult = re.search(searchstr3, line)
        relayId = searchResult.group(1)
        fingerprint = searchResult.group(2)

        probedRelaysDict[relayId] = relayInfoDict[fingerprint]
    probedRelays.close()

del relayInfoDict
#gc.collect()


noTheoreticDict = {}
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

        noTheoreticDict[(sourceRelayIP, destRelayIP)] = latencies.split(",")
paths.close()
del probedRelaysDict
del noTheoreticPathsFile

#gc.collect()

#outputDirectory
filePath = os.path.join(outputDirectory, source + ".txt")
for key in noTheoreticDict:
    source, dest = key
    filePath = os.path.join(outputDirectory, source + ".txt")
    if not os.path.exists(filePath):
        f = open(filePath, "x") #will error if file exists
        f.write(source + "\n") #writes source IP to top of file
        for latency in noTheoreticDict[key]:
            latencyInMilliseconds = latency/1000
            f.write("64 bytes from " + dest + ": icmp_seq=0 ttl=50 time=" + latencyInMilliseconds +  " ms\n")
    else:    #append to it
        f = open(filePath, "a") #will not error if the file exists, will append
        for latency in noTheoreticDict[key]:
            latencyInMilliseconds = latency/1000
            f.write("64 bytes from " + dest + ": icmp_seq=0 ttl=50 time=" + latencyInMilliseconds +  " ms\n")
    f.close()
