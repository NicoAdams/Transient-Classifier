import csv
import sys
sys.path.append('.')
import processUtil

# -- Parameters --

inputFile = "process_data/created/TNS_OldPS_SDSS_120arcsec_raw.csv"
outputFile = "training/TNS_OldPS_SDSS_120arcsec_training.csv"
transientLabelMapFile = "raw_data/TNS/TNS_type_label_map.csv"

# Copy these from the catalog
catalogColumns = [
	'id', 'label', 'ra', 'dec', 'mag',
	'SDSS objid', 'SDSS type', 'SDSS offset', 'SDSS ra', 'SDSS dec',
	'SDSS redshift', 'SDSS u', 'SDSS g', 'SDSS r', 'SDSS i', 'SDSS z',
	'SDSS err_u', 'SDSS err_g', 'SDSS err_r', 'SDSS err_i', 'SDSS err_z', 'SDSS err_redshift'
]

class TrainingExample:
	exampleId = "id"
	ra = "ra"
	dec = "dec"
	transientLabel = "transient_label"
	transientMag = "transient_mag"
	hostLabel = "host_label"
	offset = "offset"
	redshift = "redshift"
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

def getHostLabel(sdssType):
	return hostLabelMap[sdssType] if sdssType in hostLabelMap else hostOtherType

def handleRowMap(rowMap):
	trainingExample = TrainingExample()
	
	# Transient properties
	trainingExample.exampleId = rowMap["id"]
	trainingExample.ra = rowMap["ra"]
	trainingExample.dec = rowMap["dec"]
	trainingExample.transientLabel = rowMap["label"]
	trainingExample.transientMag = processUtil.filterTNSTransientMag(rowMap["mag"])
	
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
