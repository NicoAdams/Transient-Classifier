import csv
import sys
sys.path.append('.')
import processUtil
import processTNSUtil

# -- Parameters --

inputFile = "process_data/created/TNS_PS_imaging_20px_raw.csv"
outputFile = "training/TNS_PS_imaging_20px_training.csv"
transientLabelMapFile = "process_data/TNS_type_label_map.csv"

transientHeaders = ['id', 'transient_label']

# -- Helper functions --

reader = csv.reader(open(inputFile))

idCol = 0
typeCol = 4
firstPixelCol = 22

transientLabelMap = processTNSUtil.generateTransientLabelMap(transientLabelMapFile)
transientOtherType = "OTHER TRANSIENT"

def getTransientLabel(tnsType):
	return transientLabelMap[tnsType] if tnsType in transientLabelMap else transientOtherType

def handleRow(row):
	transientId = row[idCol]
	transientLabel = getTransientLabel(row[typeCol])
	pixelData = row[firstPixelCol:]
	
	trainingRow = [transientId, transientLabel] + pixelData
	processUtil.appendRow(trainingRow, outputFile)
	return trainingRow

# -- Script --

# User prompt
processUtil.confirmOverwrite(outputFile)

# Clears output file
processUtil.createOrClearFile(outputFile)

# Handles headers
headers = reader.__next__()
processUtil.appendRow(transientHeaders + headers[firstPixelCol:], outputFile)

# Generates and writes training rows
for row in reader: handleRow(row)
