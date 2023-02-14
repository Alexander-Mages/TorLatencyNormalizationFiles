import json
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("desiredData")
parser.add_argument("monkeySeeOrMonkeyDo")
parser.add_argument("--outputFile")
parser.add_argument("--jsonLineNumber")

args = parser.parse_args()

#if len(args) < 4:
#^TypeError, parse_args() returns a namespace, but doesn't depopulate sys.argv[]. Using that instead.
if len(sys.argv) < 3:
    print("syntax: python jsonParser.py filename (data/rtt) (view/save) --output-file outputFile --jsonLineNumber (1/2/3/etc...)\n"
          "note: rtt refers to ting's estimated x<->y latency and --jsonLineNumber is the line # of the json object accessed")
else:
    filename = args.filename
    desiredData = args.desiredData
    seeOrSave = args.monkeySeeOrMonkeyDo
    outputFile = args.outputFile
    objInFile = args.objInFile


#read line-by-line to extract multiple json objects
resultList = []
with open(filename) as file:
    for jsonObj in file:
        resultDict = json.loads(jsonObj) #json.loads() reads from string, json.load() reads from file object
        resultList.append(resultDict)

if (jsonLineNumber is None) & (len(resultList) > 1):
    print("file contains multiple JSON objects. Please specify line # of intended JSON object via --jsonLineNumber")
elif (jsonLineNumber is not None) & (len(resultList) > 1):
    result = resultList[(jsonLineNumber - 1)]
elif (seeOrSave == "save") & (jsonLineNumber is None) & (len(resultList) > 1):
    print("cannot save as theres two json objects")


if seeOrSave == "save":
    print("saving xy data from " + filename + ". RTTs from circuit " + result["y"]["ip"] + "<-->" + result["x"]["ip"])
    print(result["trials"][0]["xy"]["measurements"][199])
    print(result["trials"][0]["xy"]["measurements"][0])
    print(outputFile)
else:
    for result in resultList:
        print("\ny: " + result["y"]["ip"] + "\nx: " + result["x"]["ip"])
        print(result["trials"][0]["xy"]["measurements"])
