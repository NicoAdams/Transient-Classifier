# Hacky and terrible way of getting SDSS-querying code in here
import sys
sys.path.append("./data/")
import querySDSS

import csv
from threading import Thread
from time import sleep

requestLimit = -1
concurrentRequestLimit = 10
radiusLimit = 0.25 # In arcminutes

# Will need to change this with any change to the SDSS request
sdssFields = ['objid','type','distance','ra','dec','u','g','r','i','z','redshift','err_u','err_g','err_r','err_i','err_z','err_redshift']

sdssFieldPositions = {sdssFields[i]: i for i in range(len(sdssFields))}
sdssHeaders = list(map(lambda s: "SDSS "+s, sdssFields))

def getHostRow(host):
	if host == None: return []
	hostRow = ["" for i in range(len(sdssFields))]
	for key in host.keys():
		hostRow[sdssFieldPositions[key]] = host[key]
	return hostRow

fin = open("exploratory/TNScatalog_type_filtered.csv")
fout = open("exploratory/Experimental TNS_SDSS_raw.csv", "w")
reader = csv.reader(fin)
writer = csv.writer(fout)

isHeaderRow = True
requestNum = 0
responseNum = 0

def handleRequest(row, ra, dec, currRequestNum):
	global responseNum

	print("Sending request {}".format(currRequestNum))
	
	host = querySDSS.searchNearestHost(ra, dec, radiusLimit)
	
	print(currRequestNum, "--" if host==None else host['distance'])
	if host != None:
		hostRow = getHostRow(host)
		writer.writerow(row + hostRow)
	
	responseNum += 1

for row in reader:
	if isHeaderRow:
		isHeaderRow = False
		writer.writerow(row + sdssHeaders)
		continue
	
	requestNum += 1
	
	ra, dec = row[2:4]
	t = Thread(target=handleRequest, args=(row, ra, dec, requestNum))
	t.start()
	
	# Ends the loop after a given number of requests
	if requestNum == requestLimit: break
	
	# If requests haven't come in yet, wait
	while requestNum - responseNum >= concurrentRequestLimit: sleep(0.1)
	

print("(All requests sent)")