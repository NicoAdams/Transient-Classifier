import csv

def getRowRaDec(row):
	return float(row[2]), float(row[3])
	
def filterTransientMag(transientMag):
	try:
		transientMagVal = float(transientMag)
		if transientMagVal > 1: return transientMagVal
	except ValueError: pass
	return ""

def generateTransientLabelMap(transientLabelMapFile):
	with open(transientLabelMapFile) as f:
		transientLabelMapReader = csv.reader(f)
		transientLabelMap = {row[0]: row[1] for row in transientLabelMapReader}
	return transientLabelMap