import csv
import sys
sys.path.append('.')
import processUtil
import processTNSUtil

# -- Parameters --

inputFile = "process_data/created/TNS_SDSS_120arcsec_raw.csv"
outputFile = "training/TNS_SDSS_120arcsec_training TEST.csv"
transientLabelMapFile = "process_data/TNS_type_label_map.csv"

# Copy these from the catalog
catalogColumns = [
	'ID', 'Name', 'RA', 'DEC', 'Type', 'Redshift', 'Host Name', 'Host Redshift', 'Discovering Group/s',
	'Classifying Group/s', 'Associated Group/s', 'Disc. Internal Name', 'Disc. Instrument/s', 'Class. Instrument/s',
	'TNS AT', 'Public', 'End Prop. Period', 'Discovery Mag', 'Discovery Mag Filter', 'Discovery Date (UT)', 'Sender',
	'Ext. catalog/s',
	'SDSS objid', 'SDSS type', 'SDSS offset', 'SDSS ra', 'SDSS dec', 'SDSS u', 'SDSS g', 'SDSS r', 'SDSS i', 'SDSS z',
	'SDSS redshift', 'SDSS err_u', 'SDSS err_g', 'SDSS err_r', 'SDSS err_i', 'SDSS err_z', 'SDSS err_redshift'
	]

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
	
	def generateRow(self): return [
		self.exampleId, self.ra, self.dec, self.transientLabel, self.hostLabel, self.offset, self.redshift, 
		self.transientMag, self.transientFilter, self.u, self.g, self.r, self.i, self.z
		]
	
# -- Helper functions --

trainingHeaders = TrainingExample().generateRow()
dictReader = csv.DictReader(open(inputFile))

hostLabelMap = {}
hostLabelMap['3'] = "GALAXY"
hostLabelMap['6'] = "STAR"
hostOtherType = "OTHER"

transientLabelMap = processTNSUtil.generateTransientLabelMap(transientLabelMapFile)
transientOtherType = "OTHER TRANSIENT"

def getTransientLabel(tnsType):
	return transientLabelMap[tnsType] if tnsType in transientLabelMap else transientOtherType

def getHostLabel(sdssType):
	return hostLabelMap[sdssType] if sdssType in hostLabelMap else hostOtherType

def handleRowMap(rowMap):
	trainingExample = TrainingExample()
	
	# Transient properties
	trainingExample.exampleId = rowMap["ID"]
	trainingExample.ra = rowMap["RA"]
	trainingExample.dec = rowMap["DEC"]
	trainingExample.transientLabel = getTransientLabel(rowMap["Type"])
	trainingExample.transientMag = processTNSUtil.filterTransientMag(rowMap["Discovery Mag"])
	trainingExample.transientFilter = rowMap["Discovery Mag Filter"]
	
	# Host properties
	trainingExample.hostLabel = getHostLabel(rowMap["SDSS type"])
	trainingExample.offset = rowMap["SDSS offset"]
	trainingExample.redshift = rowMap["SDSS redshift"]
	trainingExample.u = rowMap["SDSS u"]
	trainingExample.g = rowMap["SDSS g"]
	trainingExample.r = rowMap["SDSS r"]
	trainingExample.i = rowMap["SDSS i"]
	trainingExample.z = rowMap["SDSS z"]
	
	# Add the label to the label counts
	tl = trainingExample.transientLabel
	labelCounts[tl] += 1
	if tl==transientOtherType: typesLabeledOther.add(rowMap["Type"])
	
	# Generate and write the training file row
	trainingRow = trainingExample.generateRow()
	processUtil.appendRow(trainingRow, outputFile)
	return trainingRow

# -- Script --

# User prompt
processUtil.confirmOverwrite(outputFile)

# Clears output file
processUtil.createOrClearFile(outputFile)

# Handles headers
dictReader.__next__()
processUtil.appendRow(trainingHeaders, outputFile)

# Generates and writes training rows
trainingRows = [handleRowMap(rowMap) for rowMap in dictReader]
