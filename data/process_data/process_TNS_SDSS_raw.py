import csv

# -- Files --

inFile = "raw_data/TNS_SDSS_120arcsec_raw.csv"
outFile = "training/TNS_SDSS_120arcsec_training.csv"
transientLabelMapFile = "process_data/TNS_type_label_map.csv"

# -- Parameters --

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
	
# -- Code --

trainingHeaders = TrainingExample().generateRow()
	
tnsReader = csv.reader(open(inFile))
tnsWriter = csv.writer(open(outFile, "w"))

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
transientOtherType = "OTHER TRANSIENT"
def getTransientLabel(tnsType): return transientLabelMap[tnsType] if tnsType in transientLabelMap else transientOtherType

# SDSS host-type mapping

hostLabelMap = {}
hostLabelMap['3'] = "GALAXY"
hostLabelMap['6'] = "STAR"
hostOtherType = "OTHER"
def getHostLabel(sdssType):
	return hostLabelMap[sdssType] if sdssType in hostLabelMap else hostOtherType	

# (For printing at the end)

labelCounts = {label: 0 for label in set(list(transientLabelMap.values()) + [transientOtherType])}
typesLabeledOther = set()

# The read-process-write loop

headerRow = True
for row in tnsReader:
	if headerRow:
		headerRow = False
		tnsWriter.writerow(trainingHeaders)
		continue
	
	rowMap = {catalogColumns[i]: row[i] for i in range(len(row))}
	
	trainingExample = TrainingExample()
	
	# Get the transient properties
	trainingExample.exampleId = rowMap["ID"]
	trainingExample.ra = rowMap["RA"]
	trainingExample.dec = rowMap["DEC"]
	trainingExample.transientLabel = getTransientLabel(rowMap["Type"])
	trainingExample.transientMag = filterTransientMag(rowMap["Discovery Mag"])
	trainingExample.transientFilter = rowMap["Discovery Mag Filter"]
	
	# Get host properties
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
	tnsWriter.writerow(trainingRow)

# Prints a short label report

labelCountPairs = sorted(labelCounts.items(), key=lambda c: c[1], reverse=True)
labelTotal = sum(labelCounts.values())

print("Total transients:", labelTotal)
for pair in labelCountPairs:
	print(pair[0], "{0:.1%}".format(pair[1]/float(labelTotal)))
print("Other types:", list(typesLabeledOther))
