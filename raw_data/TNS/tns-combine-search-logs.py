# Get header row

fout = open("TNSsample.csv", "w")

f1 = open("tns_search (1).csv").read()
headers = f1[:f1.index("\n")]
fout.write(headers)

for i in range(5):
	f = open("tns_search ("+str(i+1)+").csv").read()
	f = f[f.index("\n"):] # Strips first row
	f = f[:-1] # Strips final newline
	fout.write(f)

