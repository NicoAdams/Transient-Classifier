# Get header row

fout = open("TNScatalog_raw_NEW.csv", "w")

f1 = open("searches/tns_search (0).csv").read()
headers = f1[:f1.index("\n")]
fout.write(headers)

# Stitch together the data into a single file

firstFile = 0
lastFile = 21
for fileNum in range(firstFile, lastFile+1):
	f = open("searches/tns_search ({}).csv".format(fileNum)).read()
	f = f[f.index("\n"):] # Strips first row
	fout.write(f)

