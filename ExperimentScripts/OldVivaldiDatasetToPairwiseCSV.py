import os

l = {}

for file in os.listdir("/home/alex/ExperimentData"):
    with open(file) as f:
        sourceHost = f.readline().rstrip()
        h.add(sourceHost)
        for line in f.read().splitlines():
            line = line.rstrip()  # removes \n newline
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

            if (sourceHost, destHost) in l:
                # if the host-pair already has a measurement associated with it, another is appended
                l[(sourceHost, destHost)].append(float(rtt))
                # l[(sourceHost, destHost)].append(pcgRandVec())
            else:
                # if no values have been inserted yet, the item is made into a list, with an item appended to it
                l[(sourceHost, destHost)] = [float(rtt)]
                # l[(sourceHost, destHost)] = [pcgRandVec()]
