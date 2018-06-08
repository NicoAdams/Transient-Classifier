import csv
from threading import Thread
from time import sleep

# Local files
import sys
sys.path.append('.')
import querySDSSHosts

# -- Parameters --

tnsCatalogFile = "raw_data/TNS/TNScatalog_processed.csv"
outputFile = "raw_data/TNS_SDSS_2host_raw.csv"

# In arcminutes
hostRadiusLimit = 2

requestLimit = None
concurrentRequestLimit = 10
sleepTime = 0.05 # Seconds

# The names of the fields from "querySDSSHosts.searchNearestHosts"
# This is the order that these items will be written to file 
hostFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']

hostFieldPositions = {hostFields[i]: i for i in range(len(hostFields))}
host1Headers = list(map(lambda s: "SDSS_host1_"+s, hostFields))
host2Headers = list(map(lambda s: "SDSS_host2_"+s, hostFields))

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
	
	hosts = querySDSSHosts.searchNearestHosts(ra, dec, hostRadiusLimit, 2)
		
	if len(hosts) == 2:
		host1Values = getFieldValues(hosts[0], hostFieldPositions)
		host2Values = getFieldValues(hosts[1], hostFieldPositions)
		appendRow(row + host1Values + host2Values)
	
	print(currRequestNum, "--" if len(hosts)<2 else host1Values[2], host2Vales[2])
	
	responseNum += 1

for row in reader:
	if isHeaderRow:
		isHeaderRow = False
		appendRow(row + host1Headers + host2Headers)
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

