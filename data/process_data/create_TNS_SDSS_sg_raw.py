import csv
from threading import Thread
from time import sleep

# Local files
import sys
sys.path.append('.')
import querySDSSHosts

# -- Parameters --

tnsCatalogFile = "raw_data/TNS/TNScatalog_processed.csv"
outputFile = "raw_data/TNS_SDSS_sg_raw_NEW.csv"

# In arcminutes
starRadiusLimit = 2
galaxyRadiusLimit = 2

requestLimit = None
concurrentRequestLimit = 10
sleepTime = 0.05 # Seconds

# This is the order that these items will be written to file 
# -- EDIT THIS -- if any changes are made to the results of "querySDSSHosts.searchNearest[Star/Galaxy]"
starFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']
galaxyFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']

starFieldPositions = {starFields[i]: i for i in range(len(starFields))}
galaxyFieldPositions = {galaxyFields[i]: i for i in range(len(galaxyFields))}
starHeaders = list(map(lambda s: "SDSS_star_"+s, starFields))
galaxyHeaders = list(map(lambda s: "SDSS_galaxy_"+s, galaxyFields))

def getFieldValues(objectDict, fieldPositions):
	values = ["" for i in range(len(fieldPositions))]
	if objectDict == None: return values
	for key in fieldPositions.keys():
		values[fieldPositions[key]] = objectDict[key]
	return values

reader = csv.reader(open(tnsCatalogFile))

# Clears the file
with open(outputFile, 'w') as f: pass

# Writes a line "atomically" (cannot write at the same time as another thread)
def appendRow(row):
	with open(outputFile, 'a') as f:
		writer = csv.writer(f)
		writer.writerow(row)


isHeaderRow = True
requestNum = 0
responseNum = 0

def handleRowRequests(row, ra, dec, currRequestNum):
	global responseNum
	
	# Makes the "star" and "galaxy" requests one at a time (these are not concurrent requests)
	star = querySDSSHosts.searchNearestStar(ra, dec, starRadiusLimit)
	galaxy = querySDSSHosts.searchNearestGalaxy(ra, dec, galaxyRadiusLimit)
	
	print(currRequestNum, "-" if star==None else 'S', "-" if galaxy==None else 'G')
	
	if star != None and galaxy != None:
		starValues = getFieldValues(star, starFieldPositions)
		galaxyValues = getFieldValues(galaxy, galaxyFieldPositions)
		appendRow(row + starValues + galaxyValues)
	
	responseNum += 1

for row in reader:
	if isHeaderRow:
		isHeaderRow = False
		appendRow(row + starHeaders + galaxyHeaders)
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

