import csv
from multiprocessing.dummy import Pool
from urllib.error import URLError

# Local files
import sys
sys.path.append('.')
import querySDSSHosts
import processUtil
import processTNSUtil

# -- Parameters --

tnsCatalogFile = "raw_data/TNS/TNScatalog_processed.csv"
outputFile = "process_data/created/TNS_SDSS_120arcsec_raw test.csv"

radiusLimit = 2 # In arcminutes

rowLimit = 10
threadNum = 12
requestAttempts = 5

# -- Helper functions --

# This is the order that these items will be written to file 
sdssFields = ['objid','type','offset','ra','dec','redshift','u','g','r','i','z','err_u','err_g','err_r','err_i','err_z','err_redshift']

sdssFieldPositions = {sdssFields[i]: i for i in range(len(sdssFields))}
sdssHeaders = list(map(lambda s: "SDSS "+s, sdssFields))

reader = csv.reader(open(tnsCatalogFile))
currRowNum = 0

def getHostRow(host):
	return processUtil.getFieldValues(host, sdssFieldPositions)

def handleRow(row):
	rowId = row[0]
	ra, dec = processTNSUtil.getRowRaDec(row)
	
	requestFunction = lambda: querySDSSHosts.searchNearestHost(ra, dec, radiusLimit)
	host = processUtil.requestUntilSuccess(requestFunction, limit=requestAttempts, returnOnFailure=None)
	
	global currRowNum
	currRowNum += 1
	print(currRowNum, rowId, "--" if host==None else host['offset'])
	
	if host != None:
		hostRow = getHostRow(host)
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