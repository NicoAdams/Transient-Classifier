import csv
from urllib.error import URLError

def getFieldValues(objectDict, fieldPositions):
	values = ["" for i in range(len(fieldPositions))]
	if objectDict == None: return values
	for key in fieldPositions.keys():
		values[fieldPositions[key]] = objectDict[key]
	return values

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

def confirmOverwrite(outputFile):
	print("Output file:\n\n\t{}\n".format(outputFile))
	ans = input("Continue? ".format(outputFile))
	if ans not in ['y','yes','Y','YES']: exit(0)

def createOrClearFile(outputFile):
	with open(outputFile, "w"): pass