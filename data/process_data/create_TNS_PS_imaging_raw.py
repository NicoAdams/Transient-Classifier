import csv
from multiprocessing.dummy import Pool
from urllib.error import URLError

# Local files
import sys
sys.path.append('.')
import queryPS1Imaging
import processUtil

# -- Parameters --

tnsCatalogFile = "process_data/combined_catalogs/TNS_OldPS_Catalog.csv"
outputFile = "process_data/created/TNS_OldPS_PS_imaging_10px_raw TEST.csv"

raCol, decCol = 2, 3

imageArcsec = 10
imageOutputSize = 10

rowLimit = None
threadNum = 12
requestAttempts = 5

# -- Helper functions --

imageOutputPixels = imageOutputSize**2
imageOutputData = imageOutputPixels*4

imageHeaders = (
	['g{}'.format(i) for i in range(imageOutputPixels)] +
	['r{}'.format(i) for i in range(imageOutputPixels)] +
	['i{}'.format(i) for i in range(imageOutputPixels)] +
	['z{}'.format(i) for i in range(imageOutputPixels)]
)

reader = csv.reader(open(tnsCatalogFile))
currRowNum = 0

def shouldSkipRow(row):
	ra, dec = processUtil.getTNSRowRaDec(row)
	return dec < -30

def handleRow(row):
	rowId = row[0]
	ra, dec = processUtil.getTNSRowRaDec(row)
	
	requestFunction = lambda: queryPS1Imaging.queryPS1ImageData(ra, dec, imageArcsec, imageOutputSize)
	imageData = processUtil.requestUntilSuccess(requestFunction, limit=requestAttempts, returnOnFailure=[])
		
	global currRowNum
	currRowNum += 1
	
	if len(imageData) == imageOutputData:
		print(currRowNum, rowId, len(imageData))
		processUtil.appendRow(row + imageData, outputFile)
		return True
	
	print(currRowNum, rowId, "No image")
	return False

# -- Script --

# User prompt
processUtil.confirmOverwrite(outputFile)

# Clears the file
processUtil.createOrClearFile(outputFile)

# Handles the headers
headerRow = reader.__next__()
processUtil.appendRow(headerRow + imageHeaders, outputFile)

# Reads and filters the catalog rows
rows = [row for row in reader if not shouldSkipRow(row)]
if rowLimit: rows = rows[:rowLimit]

# Requests and writes the desired image data
pool = Pool(threadNum)
pool.map(handleRow, rows)
