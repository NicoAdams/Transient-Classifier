import uuid
import csv
from urllib.error import URLError

def generateUUID(digits=20):
	# Generates a unique universal ID
	return uuid.uuid4().int % 10**digits

def getFieldValues(objectDict, fieldPositions):
	values = ["" for i in range(len(fieldPositions))]
	if objectDict == None: return values
	for key in fieldPositions.keys():
		values[fieldPositions[key]] = objectDict[key]
	return values

def generateLabelMap(labelMapFile):
	with open(labelMapFile) as f:
		labelMapReader = csv.reader(f)
		labelMap = {row[0]: row[1] for row in labelMapReader}
	return labelMap

def requestUntilSuccess(requestFunction, limit=None, returnOnFailure=None):
	attempts = 0
	while attempts != limit:
		try:
			return requestFunction()
		except URLError:
			attempts += 1
	return returnOnFailure

def appendRow(row, outputFile):
	# Writes a line to csv atomically (cannot write at the same time as another thread)
	with open(outputFile, 'a') as f:
		writer = csv.writer(f)
		writer.writerow(row)

def appendRows(rows, outputFile):
	# Writes multiple lines to csv atomically (cannot write at the same time as another thread)
	with open(outputFile, 'a') as f:
		writer = csv.writer(f)
		writer.writerows(rows)

def confirmOverwrite(outputFile):
	print("The following file will be overwritten:\n\n\t{}\n".format(outputFile))
	ans = input("Continue? ".format(outputFile))
	if ans not in ['y','yes','Y','YES']: exit(0)

def createOrClearFile(outputFile):
	with open(outputFile, "w"): pass

# -- TNS specific functions --

def getTNSRowRaDec(row):
	return float(row[2]), float(row[3])

def filterTNSTransientMag(transientMag):
	try:
		transientMagVal = float(transientMag)
		if transientMagVal > 1: return transientMagVal
	except ValueError: pass
	return ""

