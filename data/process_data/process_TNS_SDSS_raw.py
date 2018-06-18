import csv
import sys
sys.path.append('.')
import processUtil

# -- Parameters --

inputFile = "process_data/created/TNS_SDSS_6arcsec_raw.csv"
outputFile = "training/TNS_SDSS_6arcsec_training.csv"
transientLabelMapFile = "raw_data/TNS/TNS_type_label_map.csv"

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
	u = "u"
	g = "g"
	r = "r"
	i = "i"
	z = "z"	
	
	def generateRow(self): return [
		self.exampleId, self.ra, self.dec, self.transientLabel, self.hostLabel, self.offset, self.redshift, 
		self.transientMag, self.u, self.g, self.r, self.i, self.z
		]
	
# -- Helper functions --

trainingHeaders = TrainingExample().generateRow()
dictReader = csv.DictReader(open(inputFile))

hostLabelMap = {}
hostLabelMap['3'] = 1
hostLabelMap['6'] = 0
hostOtherType = 0

transientLabelMap = processUtil.generateLabelMap(transientLabelMapFile)
transientOtherType = "OTHER"

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
	trainingExample.transientMag = processUtil.filterTNSTransientMag(rowMap["Discovery Mag"])
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
	
	# Generate and write the training file row
	trainingRow = trainingExample.generateRow()
	return trainingRow

# -- Script --

# User prompt
processUtil.confirmOverwrite(outputFile)

# Clears output file
processUtil.createOrClearFile(outputFile)

# Handles headers
processUtil.appendRow(trainingHeaders, outputFile)

# Generates and writes training rows
trainingRows = [handleRowMap(rowMap) for rowMap in dictReader]
processUtil.appendRows(trainingRows, outputFile)
