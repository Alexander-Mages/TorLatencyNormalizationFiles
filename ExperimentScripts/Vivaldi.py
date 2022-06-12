from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import numpy as np
import random
import sys

positions = {} #dictionary
latencies = {} #dictionary keyed as follows latencies[(sourceHost, destHost)] = [rtt]
hosts = set() # set object: same interface as HashSet

def randomVec():
    return array([random.uniform(0,400),random.uniform(0,400),random.uniform(0,400),random.uniform(0,400)])

def vectorLength(a):
    np.\
        sqrt(vecSum(np.power(a,2)))

def vectorDist(a,b):
    vectorLength(vecAdd(a, b*-1))

def error():
    if not latencies: #< ensures not null
        parseData()
    err = sum = count = 0
    for (source, dest) in latencies:
        dist = latencies[(source, dest)] - vectorDist(positions[source], positions[dest])
        err += dist ^ 2
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
            for line in f.readlines():
                (destHost, rtt) = line.split(":")
                hosts.add(destHost) #adds destination to hosts hashset
                if (sourceHost, destHost) in latencies:
                #if a value exists for the host pair tuple it's turned into a list and the new value is appended
                    latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]]
                    latencies.append(rtt)
                    #does this: latencies[(sourceHost, destHost)] = [latencies[(sourceHost, destHost)]], rtt]
                else:
                    latencies[(sourceHost, destHost)] = rtt

def findCoordinates():
    err = error()
    newErr = err - 1000

    if not hosts:
        getHosts()

    for a in range(0,200):
        err = newErr
        for source in hosts:
            f = randomVec()
            for dest in hosts:
                if source == dest:
                    continue
                l = latencies[(source, dest)]
                if not l:
                    l = latencies[(dest, source)]
                if not l:
                    continue
            delta = addvec(positions[source], scale(-1, positions[dest]))
            dist = vectorLength(delta)
            e = l - dist
            f = addvec(f, scale(e/dist, delta))
        positions[source] = addvec(positions[source], scale(0.002, f))

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
    initCoords([sys.argv[1]]) #file input format: Vivaldi.py file1 file2 file3 (I tried putting [0], but it reads the script name as an argument
    print(latencies)
    print(positions)
    findCoordinates()
    print(positions)
if __name__ == "__main__":
    main()
