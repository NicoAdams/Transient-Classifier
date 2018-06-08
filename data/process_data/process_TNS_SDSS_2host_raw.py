import csv

# -- Files --

inFile = "raw_data/TNS_SDSS_2host_raw.csv"
outFile = "training/TNS_SDSS_2host_training.csv"
transientLabelMapFile = "process_data/TNS_type_label_map.csv"

# -- Parameters --

# Copy these from the catalog
catalogColumns = [
	'ID', 'Name', 'RA', 'DEC', 'Type', 'Redshift', 'Host Name', 'Host Redshift', 'Discovering Group/s',
	'Classifying Group/s', 'Associated Group/s', 'Disc. Internal Name', 'Disc. Instrument/s', 'Class. Instrument/s',
	'TNS AT', 'Public', 'End Prop. Period', 'Discovery Mag', 'Discovery Mag Filter', 'Discovery Date (UT)', 'Sender',
	'Ext. catalog/s',
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
	transientMag = "transient_mag"
	transientFilter = "transient_filter"
	
	hostLabel1 = "host_label_1"
	offset1 = "host_offset_1"
	redshift1 = "host_redshift_1"
	u1 = "u1"
	g1 = "g1"
	r1 = "r1"
	i1 = "i1"
	z1 = "z1"	
	
	hostLabel2 = "host_label_2"
	offset2 = "host_offset_2"
	redshift2 = "host_redshift_2"
	u2 = "u2"
	g2 = "g2"
	r2 = "r2"
	i2 = "i2"
	z2 = "z2"	
	
	def generateRow(self):
		return [
		self.exampleId,
		self.ra,
		self.dec,
		self.transientLabel,
		self.transientMag,
		self.transientFilter,
		self.hostLabel1,
		self.hostLabel2,
		self.offset1,
		self.offset2,
		self.redshift1,
		self.u1,
		self.g1,
		self.r1,
		self.i1,
		self.z1,
		self.redshift2,
		self.u2,
		self.g2,
		self.r2,
		self.i2,
		self.z2
		]

# -- Code --

trainingHeaders = TrainingExample().generateRow()

reader = csv.reader(open(inFile))
writer = csv.writer(open(outFile, "w"))

# Magnitude filter

def filterTransientMag(transientMag):
	try:
		transientMag = float(transientMag)
		if transientMag > 1: return transientMag
	except ValueError: pass
	return ""

# Transient-type processor

transientLabelMapReader = csv.reader(open(transientLabelMapFile))
transientLabelMap = {row[0]: row[1] for row in transientLabelMapReader}
transientOtherType = "OTHER TRANSIENT"
def getTransientLabel(tnsType): return transientLabelMap[tnsType] if tnsType in transientLabelMap else transientOtherType

# SDSS host-type processor

hostLabelMap = {}
hostLabelMap['3'] = "GALAXY"
hostLabelMap['6'] = "STAR"
hostOtherType = "OTHER"
def getHostLabel(sdssType): return hostLabelMap[sdssType] if sdssType in hostLabelMap else hostOtherType	

# (For printing at the end)

labelCounts = {label: 0 for label in set(list(transientLabelMap.values()) + [transientOtherType])}
typesLabeledOther = set()

# The read-process-write loop

headerRow = True
for row in reader:
	if headerRow:
		writer.writerow(trainingHeaders)
		headerRow = False
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

	# Add the label to the label counts
	tl = trainingExample.transientLabel
	labelCounts[tl] += 1
	if tl==transientOtherType: typesLabeledOther.add(rowMap["Type"])
	
	# Generate and write the training row
	trainingRow = trainingExample.generateRow()
	writer.writerow(trainingRow)

# Prints a short label report

labelCountPairs = sorted(labelCounts.items(), key=lambda c: c[1], reverse=True)
labelTotal = sum(labelCounts.values())

print("Total transients:", labelTotal)
for pair in labelCountPairs:
	print(pair[0], "{0:.1%}".format(pair[1]/float(labelTotal)))
print("Other transientTypes:", list(typesLabeledOther))
