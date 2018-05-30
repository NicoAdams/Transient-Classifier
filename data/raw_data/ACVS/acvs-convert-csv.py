import re

f1 = open("ACVS.1.1", "r")
f2 = open("ACVS.1.1.csv", "w+")

# Maps space-sequences in file 1 to commas 
lines = f1.readlines()
newlines = map(lambda l: re.sub(r" +", ",", l), lines)

print len(newlines)

# Writes comma-ed lines to file 2
f2.writelines(newlines)
 