# Hacky and terrible. This should eventually be fixed by setting up a python environment more carefully
import sys
sys.path.append('.')
import querySDSSHosts

import csv
from threading import Thread
from time import sleep

# -- Parameters --

tnsCatalogFile = "raw_data/TNS/TNScatalog_processed.csv"
outputFile = "raw_data/TNS_SDSS_host_galdist_raw NEW.csv"

# In arcminutes
hostRadiusLimit = 0.1
galaxyRadiusLimit = 2

requestLimit = 200
concurrentRequestLimit = 10
sleepTime = 0.05 # Seconds

# This is the order that these items will be written to file 
# -- EDIT THIS -- if any changes are made to the results of "querySDSSHosts.searchNearestHost"
hostFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']
galaxyFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']

hostFieldPositions = {hostFields[i]: i for i in range(len(hostFields))}
galaxyFieldPositions = {galaxyFields[i]: i for i in range(len(galaxyFields))}
hostHeaders = list(map(lambda s: "SDSS_host_"+s, hostFields))
galaxyHeaders = list(map(lambda s: "SDSS_galaxy_"+s, galaxyFields))

def getFieldValues(objectDict, fieldPositions):
	values = ["" for i in range(len(fieldPositions))]
	if objectDict == None: return values
	for key in fieldPositions.keys():
		values[fieldPositions[key]] = objectDict[key]
	return values

reader = csv.reader(open(tnsCatalogFile))
writer = csv.writer(open(outputFile, "w"))

isHeaderRow = True
requestNum = 0
responseNum = 0

def handleRowRequests(row, ra, dec, currRequestNum):
	global responseNum
	
	# Makes the "host" and "galaxy" requests one at a time (these are not concurrent requests)
	host = querySDSSHosts.searchNearestHost(ra, dec, hostRadiusLimit)
	galaxy = querySDSSHosts.searchNearestGalaxyByDistance(ra, dec, galaxyRadiusLimit)
	
	print(currRequestNum, "-" if host==None else 'H', "-" if galaxy==None else 'G')
	
	if host != None or galaxy != None:
		hostValues = getFieldValues(host, hostFieldPositions)
		galaxyValues = getFieldValues(galaxy, galaxyFieldPositions)
		writer.writerow(row + hostValues + galaxyValues)
	
	responseNum += 1

for row in reader:
	if isHeaderRow:
		isHeaderRow = False
		writer.writerow(row + hostHeaders + galaxyHeaders)
		continue
	
	requestNum += 1
	
	ra, dec = row[2:4]
	t = Thread(target=handleRowRequests, args=(row, ra, dec, requestNum))
	t.start()
	
	# Ends the loop after a given number of rows
	if requestNum == requestLimit: break
	
	# If requests haven't come in yet, wait
	while requestNum - responseNum >= concurrentRequestLimit: sleep(sleepTime)
	
print("(All requests sent)")

