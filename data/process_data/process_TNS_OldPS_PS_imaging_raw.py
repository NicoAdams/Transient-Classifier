import csv
import sys
sys.path.append('.')
import processUtil

# -- Parameters --

inputFile = "process_data/created/TNS_OldPS_PS_imaging_10px_raw.csv"
outputFile = "training/TNS_OldPS_PS_imaging_10px_training.csv"

transientHeaders = ['id', 'transient_label']

# -- Helper functions --

reader = csv.reader(open(inputFile))

idCol = 0
labelCol = 1
firstPixelCol = 5

def handleRow(row):
	transientId = row[idCol]
	transientLabel = row[labelCol]
	pixelData = row[firstPixelCol:]
	
	trainingRow = [transientId, transientLabel] + pixelData
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
trainingRows = [handleRow(row) for row in reader]
processUtil.appendRows(trainingRows, outputFile)
