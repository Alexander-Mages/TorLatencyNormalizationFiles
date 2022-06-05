from numpy import array
from numpy import sum as vecSum
from numpy import add as vecAdd
import numpy as np
import random

def randomVec():
    return array([random.uniform(0,400),random.uniform(0,400),random.uniform(0,400),random.uniform(0,400)])

def vectorLength(a):
    sqrt(vecSum(np.power(a,2)))

def vectorDist(a,b):
    vectorLength(vecAdd(a, b*-1))

def initCoordinates():
