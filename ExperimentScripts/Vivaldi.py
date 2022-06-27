from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import pandas as pd
import numpy as np
import random
import sys
positions = {} #dictionary
latencies = {} #dictionary keyed as follows latencies[(sourceHost, destHost)] = [rtt]
hosts = set() # set object: same interface as HashSet

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
    parseData(files)
    for host in hosts:
        positions[host] = randomVec()


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
                #if a value exists for the host pair tuple it's turned into a list and the new value is appended
                    latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]]
                    latencies.append(rtt)
                    #does this: latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]], rtt]
                else:
                    latencies[(sourceHost, destHost)] = rtt

                #take a look at this^

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
            for dest in hosts:
                if (source == dest) or (((source, dest) not in latencies) and ((dest, source) not in latencies)):
                    continue
                elif (source, dest) in latencies:
                    l = latencies[(source, dest)]
                elif (dest, source) in latencies:
                    l = latencies[(dest, source)]
                else:
                    raise Exception("baby's first hashtable")
            delta = vecAdd(positions[source], np.multiply(positions[dest], -1))
            dist = vectorLength(delta)
            e = pd.to_numeric(l) - dist #iterate through l's, it can be a list. Make sure l is always treated as list
            f = vecAdd(f, np.multiply(delta, e/dist))
            positions[source] = vecAdd(positions[source], np.multiply(f, 0.002))
        newErr = error()

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
    print(positions)
    findCoordinates()
    print(positions)
    print(latencies)
if __name__ == "__main__":
    main()
