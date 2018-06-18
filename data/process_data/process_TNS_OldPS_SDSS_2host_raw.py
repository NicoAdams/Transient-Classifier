import csv
import sys
sys.path.append('.')
import processUtil

# -- Files --

inputFile = "process_data/created/TNS_OldPS_SDSS_2host_raw.csv"
outputFile = "training/TNS_OldPS_SDSS_2host_training.csv"
transientLabelMapFile = "raw_data/TNS/TNS_type_label_map.csv"

# -- Parameters --

# Copy these from the catalog
catalogColumns = [
	'id', 'label', 'ra', 'dec', 'mag',
	'SDSS_host1_objid', 'SDSS_host1_type', 'SDSS_host1_offset', 'SDSS_host1_redshift', 'SDSS_host1_ra',
	'SDSS_host1_dec', 'SDSS_host1_u', 'SDSS_host1_g', 'SDSS_host1_r', 'SDSS_host1_i', 'SDSS_host1_z',
	'SDSS_host2_objid', 'SDSS_host2_type', 'SDSS_host2_offset', 'SDSS_host2_redshift', 'SDSS_host2_ra',
	'SDSS_host2_dec', 'SDSS_host2_u', 'SDSS_host2_g', 'SDSS_host2_r', 'SDSS_host2_i', 'SDSS_host2_z'
	]

class TrainingExample:
	exampleId = "id"
	ra = "ra"
	dec = "dec"
	transientLabel = "transient_label"
	
	hostLabel1 = "host_label_1"
	offset1 = "offset_1"
	redshift1 = "redshift_1"
	u1 = "u_1"
	g1 = "g_1"
	r1 = "r_1"
	i1 = "i_1"
	z1 = "z_1"	
	
	hostLabel2 = "host_label_2"
	offset2 = "offset_2"
	redshift2 = "redshift_2"
	u2 = "u_2"
	g2 = "g_2"
	r2 = "r_2"
	i2 = "i_2"
	z2 = "z_2"	
	
	def generateRow(self):
		return [
		self.exampleId, self.ra, self.dec, self.transientLabel, 
		self.hostLabel1, self.hostLabel2, self.offset1, self.offset2, self.redshift1, self.redshift2,
		self.u1, self.g1, self.r1, self.i1, self.z1, self.u2, self.g2, self.r2, self.i2, self.z2
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
	
	# Get the transient properties
	trainingExample.exampleId = rowMap["id"]
	trainingExample.ra = rowMap["ra"]
	trainingExample.dec = rowMap["dec"]
	trainingExample.transientLabel = rowMap["label"]
	
	# Get the host properties
	trainingExample.hostLabel1 = getHostLabel(rowMap["SDSS_host1_type"])
	trainingExample.offset1 = rowMap["SDSS_host1_offset"]
	trainingExample.redshift1 = rowMap["SDSS_host1_redshift"]
	trainingExample.u1 = rowMap["SDSS_host1_u"]
	trainingExample.g1 = rowMap["SDSS_host1_g"]
	trainingExample.r1 = rowMap["SDSS_host1_r"]
	trainingExample.i1 = rowMap["SDSS_host1_i"]
	trainingExample.z1 = rowMap["SDSS_host1_z"]
	
	trainingExample.hostLabel2 = getHostLabel(rowMap["SDSS_host2_type"])
	trainingExample.offset2 = rowMap["SDSS_host2_offset"]
	trainingExample.redshift2 = rowMap["SDSS_host2_redshift"]
	trainingExample.u2 = rowMap["SDSS_host2_u"]
	trainingExample.g2 = rowMap["SDSS_host2_g"]
	trainingExample.r2 = rowMap["SDSS_host2_r"]
	trainingExample.i2 = rowMap["SDSS_host2_i"]
	trainingExample.z2 = rowMap["SDSS_host2_z"]

	# Generate and write the training row
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