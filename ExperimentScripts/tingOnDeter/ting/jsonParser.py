import json
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("filename")
#parser.add_argument("desiredData") Parsing the calculated RTT is as simple as adding more if statements. Not needed currently.
parser.add_argument("monkeySeeOrMonkeyDo", choices=['see','save'])
parser.add_argument("--outputFile")
parser.add_argument("--jsonLineNumber", default=None)

args = parser.parse_args()

#if len(args) < 4:
#^TypeError, parse_args() returns a namespace, but doesn't depopulate sys.argv[]. Using that instead.
if len(sys.argv) < 3:
    print("syntax: python jsonParser.py filename (data/rtt) (view/save) --output-file outputFile --jsonLineNumber (1/2/3/etc...)\n"
          "note: rtt refers to ting's estimated x<->y latency and --jsonLineNumber is the line # of the json object accessed")
else:
    filename = args.filename
    #desiredData = args.desiredData
    seeOrSave = args.monkeySeeOrMonkeyDo
    outputFile = args.outputFile
    jsonLineNumber = args.jsonLineNumber

#make filename last argument

#read line-by-line to extract multiple json objects
resultList = []
with open(filename, 'rU') as file:
    lines = file.readlines()
    print(lines)
    for jsonObj in lines:
        resultDict = json.loads(jsonObj) #json.loads() reads from string, json.load() reads from file object
        resultList.append(resultDict)
	#DEBUG START
        print("appending line")
	#DEBUG END


#select relevant json object
if (jsonLineNumber is None) & (len(resultList) > 1):
    print("file contains multiple JSON objects. Please specify line-# of intended JSON object via --jsonLineNumber")
elif (jsonLineNumber is not None) & (len(resultList) > 1):
    result = resultList[(int(jsonLineNumber) - 1)]
    print("accessing JSON object on line " + jsonLineNumber)
elif (len(resultList) == 1):
    result = resultList[0]
#elif (seeOrSave == "save") & (jsonLineNumber is None) & (len(resultList) > 1):
    #print("cannot save as there's two json objects")
else:
    print("error")
    print(len(resultList))

if seeOrSave == "save":
    print("saving xy data from " + filename + ". RTTs from circuit " + result["y"]["ip"] + "<-->" + result["x"]["ip"])

    with open(outputFile, 'w') as file:
        for latency in result["trials"][0]["xy"]["measurements"]:
            file.write("%s\n" % latency)
        print("done. Saved to " + outputFile)
elif seeOrSave == "see":
    for result in resultList:
        print("\ny: " + result["y"]["ip"] + "\nx: " + result["x"]["ip"] + "\n")
	#DEBUG START
        print(result)
	#DEBUG END
        print(result["trials"][0]["xy"]["measurements"])
else:
    print("something's wrong")
