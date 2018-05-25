# Hacky and terrible way of getting SDSS-querying code in here
import sys
sys.path.append("./data/")
import querySDSS

import pickle
import csv

rowLimit = -1
radiusLimit = 0.25 # In arcminutes

# Will need to change this with any change to the SDSS request
sdssFields = ['objid','type','distance','ra','dec','u','g','r','i','z','obj','run','rerun','field','camcol']

sdssFieldPositions = {sdssFields[i]: i for i in range(len(sdssFields))}
sdssHeaders = list(map(lambda s: "SDSS "+s, sdssFields))

def getHostRow(host):
	if host == None: return []
	hostRow = ["" for i in range(len(sdssFields))]
	for key in host.keys():
		hostRow[sdssFieldPositions[key]] = host[key]
	return hostRow

fin = open("exploratory/TNScatalog_type_filtered.csv")
fout = open("exploratory/TNS_SDSS_raw.csv", "w")
reader = csv.reader(fin)
writer = csv.writer(fout)

isHeaderRow = True
currRow = 1

for row in reader:
	if isHeaderRow:
		isHeaderRow = False
		writer.writerow(row + sdssHeaders)
		continue
	ra, dec = row[2:4]
	host = querySDSS.searchNearestHost(ra, dec, radiusLimit)
	
	print(currRow, "--" if host==None else host['distance'])
	
	hostRow = getHostRow(host)
	writer.writerow(row + hostRow)
	
	currRow += 1
	if currRow == rowLimit: break
