# TODO: Match the "nearest filter" of SDSS and the given TNS data when calculating dmag

# -- Files --

tnsInFile = "raw_data/TNS_SDSS_raw.csv"
tnsOutFile = "training/TNS_SDSS_training.csv"
transientLabelMapFile = "process_data/TNS_type_label_map.csv"

# -- Parameters --

tnsIdIndex = 2 - 1
tnsRaIndex = 3 - 1
tnsDecIndex = 4 - 1
tnsTypeIndex = 5 - 1
sdssTypeIndex = 24 - 1
tnsMagIndex = 18 - 1
tnsFilterIndex = 19 - 1
offsetIndex = 25 - 1
redshiftIndex = 33 - 1
firstFilterIndex = 28 - 1

otherTransientLabel = "OTHER"

class TrainingExample:
	exampleId = "id"
	ra = "ra"
	dec = "dec"
	transientLabel = "transient_label"
	hostLabel = "host_label"
	offset = "offset"
	redshift = "redshift"
	transientMag = "transient_mag"
	transientFilter = "transient_filter"
	u = "u"
	g = "g"
	r = "r"
	i = "i"
	z = "z"	
	
	def generateRow(self):
		return [
		self.exampleId,
		self.ra,
		self.dec,
		self.transientLabel,
		self.hostLabel,
		self.offset,
		self.redshift,
		self.transientMag,
		self.transientFilter,
		self.u,
		self.g,
		self.r,
		self.i,
		self.z
		]
	
trainingHeaders = TrainingExample().generateRow()
	
# -- Code --

import csv

tnsReader = csv.reader(open(tnsInFile))
tnsWriter = csv.writer(open(tnsOutFile, "w"))

# Magnitude filter

def filterTransientMag(transientMag):
	try:
		transientMag = float(transientMag)
		if transientMag > 1: return transientMag
	except ValueError: pass
	return ""

# TNS transient-type mapping

transientLabelMapReader = csv.reader(open(transientLabelMapFile))
transientLabelMap = {row[0]: row[1] for row in transientLabelMapReader}
def getTransientLabel(tnsType):
	return transientLabelMap[tnsType] if tnsType in transientLabelMap else otherTransientLabel

# Extra transient-label stuff for printing at the end (not important)
labelCounts = {label: 0 for label in set(list(transientLabelMap.values()) + [otherTransientLabel])}
typesLabeledOther = set()

# SDSS host-type mapping

hostLabelMap = {}
hostLabelMap['3'] = "GALAXY"
hostLabelMap['6'] = "STAR"
hostOtherType = "OTHER"
def getHostLabel(sdssType):
	return hostLabelMap[sdssType] if sdssType in hostLabelMap else hostOtherType	

# The read-process-write loop

headerRow = True
for row in tnsReader:
	# Change the "type" header to the "label" header
	if headerRow:
		headerRow = False
		tnsWriter.writerow(trainingHeaders)
		continue
	
	trainingExample = TrainingExample()
	trainingExample.exampleId = row[tnsIdIndex]
	
	# Get the transient label
	tnsType = row[tnsTypeIndex]
	trainingExample.transientLabel = getTransientLabel(tnsType)
	
	tl = trainingExample.transientLabel
	labelCounts[tl] += 1
	if tl==otherTransientLabel: typesLabeledOther.add(tnsType)
	
	# Get the host label
	sdssType = row[sdssTypeIndex]
	trainingExample.hostLabel = getHostLabel(sdssType)
	
	# Get the magnitude values
	trainingExample.transientMag = filterTransientMag(row[tnsMagIndex])
	trainingExample.transientFilter = row[tnsFilterIndex]
	
	# Get remaining values
	trainingExample.ra = row[tnsRaIndex]
	trainingExample.dec = row[tnsDecIndex]
	trainingExample.offset = row[offsetIndex]
	trainingExample.redshift = row[redshiftIndex]
	trainingExample.u = row[firstFilterIndex]
	trainingExample.g = row[firstFilterIndex+1]
	trainingExample.r = row[firstFilterIndex+2]
	trainingExample.i = row[firstFilterIndex+3]
	trainingExample.z = row[firstFilterIndex+4]
	
	# Generate and write the training file row
	trainingRow = trainingExample.generateRow()
	tnsWriter.writerow(trainingRow)

# Prints a short label report
labelCountPairs = sorted(labelCounts.items(), key=lambda c: c[1], reverse=True)
labelTotal = sum(labelCounts.values())
for pair in labelCountPairs:
	print(pair[0], "{0:.1%}".format(pair[1]/float(labelTotal)))
print("Other types:", list(typesLabeledOther))
