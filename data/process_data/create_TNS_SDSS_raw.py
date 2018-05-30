# Hacky and terrible. This should eventually be fixed by setting up a python environment more carefully
import sys
sys.path.append('.')
import querySDSS

import csv
from threading import Thread
from time import sleep

# -- Parameters --

tnsCatalogFile = "raw_data/TNS/TNScatalog_processed.csv"
outputFile = "raw_data/TNS_SDSS_raw NEW.csv"

radiusLimit = 0.1 # In arcminutes

requestLimit = None
concurrentRequestLimit = 10
sleepTime = 0.05 # Seconds

# This is the order that these items will be written to file 
# -- EDIT THIS -- if any changes are made to the results of "querySDSS.searchNearestHost"
sdssFields = ['objid','type','offset','ra','dec','u','g','r','i','z','redshift','err_u','err_g','err_r','err_i','err_z','err_redshift']

sdssFieldPositions = {sdssFields[i]: i for i in range(len(sdssFields))}
sdssHeaders = list(map(lambda s: "SDSS "+s, sdssFields))

def getHostRow(host):
	if host == None: return []
	hostRow = ["" for i in range(len(sdssFields))]
	for key in host.keys():
		hostRow[sdssFieldPositions[key]] = host[key]
	return hostRow

reader = csv.reader(open(tnsCatalogFile))
writer = csv.writer(open(outputFile, "w"))

isHeaderRow = True
requestNum = 0
responseNum = 0

def handleRequest(row, ra, dec, currRequestNum):
	global responseNum

	host = querySDSS.searchNearestHost(ra, dec, radiusLimit)
	
	print(currRequestNum, "--" if host==None else host['offset'])
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
	while requestNum - responseNum >= concurrentRequestLimit: sleep(sleepTime)
	

print("(All requests sent)")