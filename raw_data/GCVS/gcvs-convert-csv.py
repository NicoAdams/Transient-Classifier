import re

f1 = open("gcvs5.txt", "r")
f2 = open("GCSV5 2.csv", "w+")

lines = f1.readlines()
newlines = map(lambda l: ",".join(map(lambda item: item.strip(), l.split("|")))+"\n", lines)

f2.writelines(newlines)