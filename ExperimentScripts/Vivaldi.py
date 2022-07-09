from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import pandas as pd
import numpy as np
import random
import sys
from numpy.random import Generator, PCG64, SeedSequence
import re #regex

positions = {} #dictionary
latencies = {} #dictionary keyed as follows latencies[(sourceHost, destHost)] = [rtt]
hosts = set() # set object: same interface as HashSet

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
        parseData()
    err = sum = count = 0
    for (source, dest) in latencies:
        dist = pd.to_numeric(latencies[(source, dest)]) - vectorDist(positions[source], positions[dest])
        err += dist ** 2
        count += 1
        sum += abs(dist)
    return err/count

def initCoords(files):
    global hosts
    global positions
    parsePingData(files)
    for host in hosts:
        positions[host] = randomVec()


def parsePingData(files):
    global hosts
    global latencies
    for file in files:
        with open(file) as f:
            sourceHost = f.readline().rstrip()
            hosts.add(sourceHost)
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

                hosts.add(destHost)
                if (sourceHost, destHost) in latencies:
                #if the host-pair already has a measurement associated with it, another is appended
                    latencies[(sourceHost, destHost)].append(rtt)
                else:
                    #if no values have been inserted yet, the item is made into a list, with an item appended to it
                    latencies[(sourceHost, destHost)] = [rtt]

def parseData(files):
    #Dictionaries are python's hashtables. This is the creation of one:
    #latencies = {
    #    (sourceHost, destHost): [latency, latency', latency'']
    #}
    global hosts
    global latencies
    for file in files:
        with open(file) as f:
            #opens file and adds host
            sourceHost = f.readline()
            hosts.add(sourceHost) #adds source host to hosts hashset
            #read timing measurements, assuming same format as Parse/ProcessVC.java
            for line in f.read().splitlines():
                (destHost, rtt) = line.split(":")
                hosts.add(destHost) #adds destination to hosts hashset
                if (sourceHost, destHost) in latencies:
                #if the host-pair already has a measurement associated with it, another is appended
                    latencies.append(rtt)
                else:
                    #if no values have been inserted yet, the item is made into a list, with an item appended to it
                    latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]]
                    latencies.append(rtt)


def findCoordinates():
    global positions
    global hosts
    global latencies
    err = error()
    newErr = err - 1000

    if not hosts:
        getHosts()

    for a in range(0,200):
        err = newErr
        for source in hosts:
            f = randomVec()
            if pd.isna(f.any()):
                print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
            for dest in hosts:
                if (source == dest) or (((source, dest) not in latencies) and ((dest, source) not in latencies)):
                    continue
                elif (source, dest) in latencies:
                    l = latencies[(source, dest)]
                    if pd.isna(l):
                        print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
                elif (dest, source) in latencies:
                    l = latencies[(dest, source)]
                    if pd.isna(l):
                        print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
                else:
                    raise Exception("baby's first hashtable")
                if pd.isna(positions[source].any()) or pd.isna(positions[dest].any()):
                    print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
                delta = vecAdd(positions[source], np.multiply(positions[dest], -1))
                if pd.isna(delta.any()):
                    print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
                dist = vectorLength(delta)
                if pd.isna(dist):
                    print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
                e = pd.to_numeric(l) - dist #iterate through l's, it can be a list. Make sure l is always treated as list
                firstDebug = e/dist
                debugVariable = np.multiply(delta, firstDebug)
                f = vecAdd(f, debugVariable)
                positions[source] = vecAdd(positions[source], np.multiply(f, 0.002))
                if pd.isna(positions[source].any()):
                    print("NAAAAAAAAAAAAAAAAAAAAAAAAAA")
        newErr = error()
        print(newErr)

def findClosest(node):
    minDist = 1000000
    for host in positions:
        dist = vectorDist(positions[host], positions[x])
        if dist < minDist:
            minDist = dist
            closest = host
    return host


def main():
    global positions
    global latencies
    global hosts
    initCoords([sys.argv[1]]) #file input format: Vivaldi.py file1 file2 file3 (I tried putting [0], but it reads the script name as an argument
    #print(positions)
    findCoordinates()
    print(positions)
    print(latencies)
if __name__ == "__main__":
    main()
