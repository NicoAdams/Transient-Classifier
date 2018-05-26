import csv

# Files (set these)
tnsInFile = "exploratory/TNS_SDSS_raw.csv"
tnsOutFile = "exploratory/TNS_SDSS_label_converted.csv"
typeLabelMapFile = "exploratory/TNS_type_label_map.csv"

# Parameters (set these)
tnsTypeColumnIndex = 4
labelColumnName = "Label"
otherLabel = "OTHER"

# Code (do not edit)
typeLabelMapReader = csv.reader(open(typeLabelMapFile))
typeLabelMap = {row[0]: row[1] for row in typeLabelMapReader}
tnsReader = csv.reader(open(tnsInFile))
tnsWriter = csv.writer(open(tnsOutFile, "w"))

typesLabeledOther = set()

def getLabel(tnsType):
	return (typeLabelMap[tnsType] if tnsType in typeLabelMap else otherLabel)

# Keeps track of the number of each type of label to print at the end of this script
uniqueLabels = set(list(typeLabelMap.values()) + [otherLabel])
labelCounts = {label: 0 for label in uniqueLabels}

headerRow = True
for row in tnsReader:
	# Change the "type" header to the "label" header
	if headerRow:
		row[tnsTypeColumnIndex] = labelColumnName
		headerRow = False
		tnsWriter.writerow(row)
		continue
	
	# Convert the type value to a label
	tnsType = row[tnsTypeColumnIndex]
	label = getLabel(tnsType)
	
	if label==otherLabel:
		typesLabeledOther.add(tnsType)
	
	row[tnsTypeColumnIndex] = label
	tnsWriter.writerow(row)
	
	labelCounts[label] += 1

# Prints a short label report
labelCountPairs = sorted(labelCounts.items(), key=lambda c: c[1], reverse=True)
labelTotal = sum(labelCounts.values())

for pair in labelCountPairs:
	print(pair[0], "{0:.1%}".format(pair[1]/float(labelTotal)))

print("Other types:", list(typesLabeledOther))
