from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import pandas as pd
import numpy as np
import random
import sys
from numpy.random import Generator, PCG64, SeedSequence
import re #regex

positions = {}  # dictionaryhow
latencies = {}  # dictionary keyed as follows latencies[(sourceHost, destHost)] = [rtt]
hosts = set()  # set object: same interface as HashSet


def PCGRandomVec():
    sg = SeedSequence

def randomVec():
    return array([random.uniform(1,400),random.uniform(1,400),random.uniform(1,400),random.uniform(1,400)])

def vectorLength(a):
    return np.sqrt(vecSum(np.power(a,2)))

def vectorDist(a,b):
    return vectorLength(vecAdd(a, b*-1))

def error():
    global latencies
    if not latencies: #< ensures not null
        print("test")
        raise Exception('somethings wrong')
    err = sum = count = 0
    for (source, dest) in latencies:
        #print((latencies[source,dest][0]))
        #print((pd.to_numeric(latencies[(source, dest)][0])))
        dist = latencies[(source, dest)] - vectorDist(positions[source], positions[dest])
        #print(dist)
        err += dist ** 2
        count += 1
        sum += abs(dist)
    return err/count

def initCoords(files):
    global hosts
    global latencies
    global positions
    hosts, latencies = parsePingData(files)
    for host in hosts:
        positions[host] = randomVec()
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
                    #l[(sourceHost, destHost)].append(float(rtt))
                    l[(sourceHost, destHost)].append(random.uniform(0.1,300.0))
                else:
                    #if no values have been inserted yet, the item is made into a list, with an item appended to it
                    #l[(sourceHost, destHost)] = [float(rtt)]
                    l[(sourceHost, destHost)] =  [random.uniform(0.1, 300.0)]
    return (h, l)


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
    for a in range(0,200):
        for source in hosts:
            f = randomVec()
            for dest in hosts:
                if (source == dest) or (((source, dest) not in latencies) and ((dest, source) not in latencies)):
                    continue
                elif (source, dest) in latencies:
                    l = latencies[(source, dest)]
                elif (dest, source) in latencies:
                    l = latencies[(dest, source)]
                else:
                    print((source,dest))
                    raise Exception("baby's first hashtable")
                delta = vecAdd(positions[source], np.multiply(positions[dest], -1))
                dist = vectorLength(delta)
                e = pd.to_numeric(l) - dist #iterate through l's, it can be a list. Make sure l is always treated as list
                firstDebug = e/dist
                debugVariable = np.multiply(delta, firstDebug)
                f = vecAdd(f, debugVariable)
                positions[source] = vecAdd(positions[source], np.multiply(f, 0.002))
        newErr = error()
        print(newErr)

def findClosest(x):
    minDist = 1000000
    for host in positions:
        dist = vectorDist(positions[host], positions[x])
        if dist < minDist:
            minDist = dist
            closest = host
    return host


def main():
    initCoords(sys.argv[1:]) #file input format: Vivaldi.py file1 file2 file3 (I tried putting [0], but it reads the script name as an argument
    #print(positions)
    findCoordinates()
    findClosest('204.56.0.138') #source host in archive/FILENEW1
    print(positions)
if __name__ == "__main__":
    main()
