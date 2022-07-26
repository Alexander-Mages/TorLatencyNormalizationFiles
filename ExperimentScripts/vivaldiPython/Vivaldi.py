from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import pandas as pd
import numpy as np
import random
import sys
from numpy.random import Generator, SeedSequence, default_rng, PCG64
import re #regex

positions = {}  # dictionary
latencies = {}  # dictionary keyed as follows latencies[(sourceHost, destHost)] = [rtt]
hosts = set()  # set object: same interface as HashSet

def initializePCGGen():
    global pcgGen
    if not 'pcgGen' in globals():
        #seed = SeedSequence([1,2])
        #pcgGen = default_rng(seed)
        pcgGen = Generator(PCG64(seed=[1, 2]))
        return pcgGen
    else:
        raise Exception('cannot initialize PRNG more than once')

def pcgRandVec():
    global pcgGen
    return array([pcgGen.uniform(0.01,400),pcgGen.uniform(0.01,400),pcgGen.uniform(0.01,400),pcgGen.uniform(0.01,400)])
    #0.00 is okay, default_rng().uniform(a,b) is constrained by (a,b]

#def randomVec():
#    return array([random.uniform(0.01,400),random.uniform(0.01,400),random.uniform(0.01,400),random.uniform(0.01,400)])

def vectorLength(a):
    return np.sqrt(vecSum(np.power(a,2)))

def vectorDist(a,b):
    return vectorLength(vecAdd(a, b*-1))

def error():
    global latencies
    global positions
    if not latencies: #< ensures not null
        print("test")
        raise Exception('somethings wrong')
    err = sum = count = 0
    for key in positions:
        if (positions[key] < 0).any():
            print("err", positions[key])
    for (source, dest), latency in latencies.items():
        #print((latencies[source,dest][0]))
        #print((pd.to_numeric(latencies[(source, dest)][0])))
        dist = latency - vectorDist(positions[source], positions[dest])
        #if dist < 0:
            #print(dist)
        #print(dist)
        err += dist ** 2
        count += 1
        sum += abs(dist)

    if err < 0:
        print("end of err debug 2 vals:", err, err/count)
    return err/count

def initCoords(files):
    global hosts
    global latencies
    global positions
    hosts, latencies = parsePingData(files)
    for host in hosts:
        positions[host] = pcgRandVec()
    for key in positions:
        if (positions[key] < 0).any():
            print("initcoords", positions[key])
    #print(positions,"\n\n\n\n\n\n\n")
    #print(latencies,"\n\n\n\n\n\n\n")
    #print(hosts)

def parsePingData(files):
    h = set()
    l = {}
    for file in files:
        with open(file) as f:
            sourceHost = f.readline().rstrip()
            h.add(sourceHost)
            for line in f.read().splitlines():
                line = line.rstrip() #removes \n newline
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

                h.add(destHost)
                if (sourceHost, destHost) in l:
                #if the host-pair already has a measurement associated with it, another is appended
                    l[(sourceHost, destHost)].append(float(rtt))
                    #l[(sourceHost, destHost)].append(pcgRandVec())
                else:
                    #if no values have been inserted yet, the item is made into a list, with an item appended to it
                    l[(sourceHost, destHost)] = [float(rtt)]
                    #l[(sourceHost, destHost)] = [pcgRandVec()]
    return (h,l)


# def parseData(files):
#     #Dictionaries are python's hashtables. This is the creation of one:
#     #latencies = {
#     #    (sourceHost, destHost): [latency, latency', latency'']
#     #}
#     global hosts
#     global latencies
#     for file in files:
#         with open(file) as f:
#             #opens file and adds host
#             sourceHost = f.readline()
#             hosts.add(sourceHost) #adds source host to hosts hashset
#             #read timing measurements, assuming same format as Parse/ProcessVC.java
#             for line in f.read().splitlines():
#                 (destHost, rtt) = line.split(":")
#                 hosts.add(destHost) #adds destination to hosts hashset
#                 if (sourceHost, destHost) in latencies:
#                 #if the host-pair already has a measurement associated with it, another is appended
#                     latencies.append(rtt)
#                 else:
#                     #if no values have been inserted yet, the item is made into a list, with an item appended to it
#                     latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]]
#                     latencies.append(rtt)
#

def findCoordinates():
    global positions
    global hosts
    global latencies
    #err = error()
    #newErr = err - 1000
    if not hosts:
        raise Exception("somethings up")
        #initCoords(sys.argv[1:])
    debugCount = 0
    for a in range(0,200):
        print(".5% interval reached. Error: ", error())
        for source in hosts:
            for key in positions:
                if (positions[key] < 0).any():
                    print(positions[key])
            newErr = error()
            print("find coordinates error", newErr)
            debugCount += 1
            #f = pcgRandVec()
            for dest in hosts:
                #if (source == dest) or (((source, dest) not in latencies) and ((dest, source) not in latencies)):
                if source == dest:
                    continue
                elif (source, dest) in latencies:
                    l = latencies[(source, dest)]
                elif (dest, source) in latencies:
                    l = latencies[(dest, source)]
                else:
                    #print((source,dest))
                    #When the latency values are parsed instead of generated, this error is generally hit. I believe
                    #this isn't an issue, unless latency values are supposed to exist for every possible (host,dest) pair
                    #raise Exception("baby's first hashtable")
                    continue
                #if l is a list,
                # looking at my original Java code, it doesn't seem like there should be situations with multiple values. Detect them:
                #if (((source, dest) in latencies) and ((dest, source) in latencies) and (latencies[(dest, source)] != latencies[(source, dest)])):
                #    print(source, dest, " have more than one latency")
                    #raise Exception("this I did not expect")
                if (len(l) > 1):
                    print(source, dest, " have more than one latency ", l)
                    raise Exception("or this")
                #else:
                #    l = l[0]
                for latency in l:
                    f = np.array([0.00, 0.00, 0.00, 0.00])
                    delta = vecAdd(positions[source], np.multiply(positions[dest], -1))
                    dist = vectorLength(delta)
                    e = pd.to_numeric(latency) - dist  # iterate through l's, it can be a list. Make sure l is always treated as list
                    x = np.multiply(delta, e/dist)
                    f = vecAdd(f, x)
                    positions[source] = vecAdd(positions[source], np.multiply(f, 0.002))
                    if (positions[source] < 0).any():
                        print("the culprit.", positions[source])

def findClosest(x):
    minDist = 1000000
    for host in positions:
        dist = vectorDist(positions[host], positions[x])
        if dist < minDist:
            minDist = dist
            closest = host
    return host


def main():
    #print(vectorLength(np.array([192.1,32.2,4.2839,8.2])))
    print(vecAdd(np.array([192.1,32.2,4.2839,8.2]), np.array([174.2,82.1,110.4,9.5])))
    global pcgGen
    pcgGen = initializePCGGen()
    initCoords(sys.argv[1:]) #file input format: Vivaldi.py file1 file2 file3 (I tried putting [0], but it reads the script name as an argument
    #print(positions)
    print("ERR", error())
    findCoordinates()
    findClosest('204.56.0.138') #source host in archive/FILENEW1
    print(positions)
if __name__ == "__main__":
    main()
