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
outputFile = "process_data/created/TNS_SDSS_sg_raw test.csv"

# In arcminutes
starRadiusLimit = 2
galaxyRadiusLimit = 2

rowLimit = 10
threadNum = 12
requestAttempts = 5

# -- Helper functions --

# This is the order that these items will be written to file 
starFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']
galaxyFields = ['objid','type','offset','redshift','ra','dec','u','g','r','i','z']

starFieldPositions = {starFields[i]: i for i in range(len(starFields))}
galaxyFieldPositions = {galaxyFields[i]: i for i in range(len(galaxyFields))}

starHeaders = list(map(lambda s: "SDSS_star_"+s, starFields))
galaxyHeaders = list(map(lambda s: "SDSS_galaxy_"+s, galaxyFields))
sdssHeaders = starHeaders + galaxyHeaders

reader = csv.reader(open(tnsCatalogFile))
currRowNum = 0

def getHostRow(star, galaxy):
	return processUtil.getFieldValues(star, starFieldPositions) + processUtil.getFieldValues(galaxy, galaxyFieldPositions)

def handleRow(row):
	rowId = row[0]
	ra, dec = processTNSUtil.getRowRaDec(row)
	
	starRequestFunction = lambda: querySDSSHosts.searchNearestStar(ra, dec, starRadiusLimit)
	galaxyRequestFunction = lambda: querySDSSHosts.searchNearestGalaxy(ra, dec, galaxyRadiusLimit)

	star = processUtil.requestUntilSuccess(starRequestFunction, limit=requestAttempts, returnOnFailure=None)
	galaxy = processUtil.requestUntilSuccess(galaxyRequestFunction, limit=requestAttempts, returnOnFailure=None)
	
	global currRowNum
	currRowNum += 1
	print(currRowNum, rowId, "-" if star==None else 'S', "-" if galaxy==None else 'G')
	
	if star != None and galaxy != None:
		hostRow = getHostRow(star, galaxy)
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