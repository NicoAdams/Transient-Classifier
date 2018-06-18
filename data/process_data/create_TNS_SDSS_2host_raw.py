import csv
from multiprocessing.dummy import Pool
from urllib.error import URLError

# Local files
import sys
sys.path.append('.')
import querySDSSHosts
import processUtil

# -- Parameters --

tnsCatalogFile = "process_data/combined_catalogs/TNS_OldPS_Catalog.csv"
outputFile = "process_data/created/TNS_OldPS_SDSS_2host_raw.csv"

raCol, decCol = 2, 3

# In arcminutes
radiusLimit = 2

rowLimit = None
threadNum = 12
requestAttempts = 5

# -- Helper functions --

# This is the order that these items will be written to file 
hostFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']

hostFieldPositions = {hostFields[i]: i for i in range(len(hostFields))}
host1Headers = list(map(lambda s: "SDSS_host1_"+s, hostFields))
host2Headers = list(map(lambda s: "SDSS_host2_"+s, hostFields))
sdssHeaders = host1Headers + host2Headers

reader = csv.reader(open(tnsCatalogFile))
currRowNum = 0

def getHostRow(host1, host2):
	return processUtil.getFieldValues(host1, hostFieldPositions) + processUtil.getFieldValues(host2, hostFieldPositions)

def handleRow(row):
	rowId = row[0]
	ra, dec = processUtil.getTNSRowRaDec(row)
	
	requestFunction = lambda: querySDSSHosts.searchNearestHosts(ra, dec, radiusLimit, 2)
	hosts = processUtil.requestUntilSuccess(requestFunction, limit=requestAttempts, returnOnFailure=[])
	
	global currRowNum
	currRowNum += 1
	print(currRowNum, rowId, "--" if len(hosts)<2 else (round(hosts[0]['offset']*60,1), round(hosts[1]['offset']*60,1)))
	
	if len(hosts) == 2:
		hostRow = getHostRow(hosts[0], hosts[1])
		processUtil.appendRow(row + hostRow, outputFile)
		return True
	return False

# -- Script --

# User prompt
processUtil.confirmOverwrite(outputFile)

# Clears the file
processUtil.createOrClearFile(outputFile)

# Handles the headers
headerRow = reader.__next__()
processUtil.appendRow(headerRow + sdssHeaders, outputFile)

# Reads and filters the catalog rows
rows = [row for row in reader]
if rowLimit: rows = rows[:rowLimit]

# Requests and writes the desired image data
pool = Pool(threadNum)
pool.map(handleRow, rows)