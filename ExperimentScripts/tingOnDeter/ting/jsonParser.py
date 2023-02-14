import json

print("syntax: python jsonParser.py (filename)")

filename = sys.argv[1]

f = open(filename)

data = json.load(f)

print(data["trials"][xy])
