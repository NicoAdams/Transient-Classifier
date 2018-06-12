import csv
from collections import Counter

psTransientFile = "psst_confirmed_and_good.tsv"
psCrossmatchFile = "psst_external_crossmatches.tsv"

psInternalTypeMapFile = "PS_internal_type_map.csv"
psCrossmatchTypeMapFile = "PS_crossmatch_type_map.csv"

outFile = "PS_transients_with_labels.csv"

# RawType: The string assigned to a transient in a crossmatch (eg "Ia", "SLSN", etc)
# Label:   One of "SN", "VS", "AGN". If a type cannot be matched to a label, "NULL" is used
nullLabel = "NULL"

# -- General helper functions --

def getElementFreqs(l):
	return dict(Counter(l))

def getUnanimousElement(l):
	if len(set(l)) == 1: return l[0]
	return None

def getMajorityElement(l):
	if len(l) == 0: return None
	freqs = getElementFreqs(l)
	maxFreq = max(freqs.values())
	elementsWithMaxFreq = list(map(lambda i: i[0], filter(lambda i: i[1]==maxFreq, freqs.items())))
	if len(elementsWithMaxFreq) == 1: return elementsWithMaxFreq[0]
	return None

# -- Type-to-label map helper functions --

def createTypeMap(typeMapFileName):
	with open(typeMapFileName) as f:
		reader = csv.reader(f)
		return {row[0]: row[1] for row in reader}

class TransientLabelMap:	
	def __init__(self, rawTypeMap):
		self.rawTypeMap = rawTypeMap
		self.transientLabels = {}
	
	def setRawTypeMap(self, rawTypeMap): self.rawTypeMap = rawTypeMap
	
	def getLabel(self, rawType):
		if rawType in self.rawTypeMap:
			return self.rawTypeMap[rawType] 
		return nullLabel
	
	def addLabel(self, transientId, rawType):
		label = self.getLabel(rawType)
		if transientId not in self.transientLabels:
			self.transientLabels[transientId] = []
		self.transientLabels[transientId].append(label)
	
	def getLabelsIncludingNull(self, transientId):
		return self.transientLabels[transientId]
	
	def getLabels(self, transientId):
		return list(filter(lambda l: l!=nullLabel, self.transientLabels[transientId]))
		
	def getUnanimousLabel(self, transientId):
		labels = self.getLabels(transientId)
		return getUnanimousElement(labels)
	
	def getMajorityLabel(self, transientId):
		labels = self.getLabels(transientId)
		return getMajorityElement(labels)
	
	def getUnanimousLabelDict(self):
		labelDict = {tid: self.getUnanimousLabel(tid) for tid in self.transientLabels.keys()}
		labelDictFiltered = dict(filter(lambda i: i[1] != None, labelDict.items()))
		return labelDictFiltered
		
	def getMajorityLabelDict(self):
		labelDict = {tid: self.getMajorityLabel(tid) for tid in self.transientLabels.keys()}
		labelDictFiltered = dict(filter(lambda i: i[1] != None, labelDict.items()))
		return labelDictFiltered

# -- Labelling script --

# Create type-to-label maps
internalTypeMap = createTypeMap(psInternalTypeMapFile)
crossmatchTypeMap = createTypeMap(psCrossmatchTypeMapFile)

combinedLabelMap = TransientLabelMap(None)

# Read and process internal data
internalLabelMap = TransientLabelMap(internalTypeMap)
combinedLabelMap.setRawTypeMap(internalTypeMap)
with open(psTransientFile) as tf:
	reader = csv.DictReader(tf, delimiter="\t")
	for row in reader:
		transientId = row['id']
		rawType = row['observation_status']
		internalLabelMap.addLabel(transientId, rawType)
		combinedLabelMap.addLabel(transientId, rawType)

# Read and process crossmatches
crossmatchLabelMap = TransientLabelMap(crossmatchTypeMap)
combinedLabelMap.setRawTypeMap(crossmatchTypeMap)
with open(psCrossmatchFile) as cf:
	reader = csv.DictReader(cf, delimiter="\t")
	for row in reader:
		transientId = row['transient_object_id']
		rawType = row['type']
		crossmatchLabelMap.addLabel(transientId, rawType)
		combinedLabelMap.addLabel(transientId, rawType)

# !! RESULTS !!

print("----INTERNAL----")

internalLabels = internalLabelMap.getUnanimousLabelDict()
print("Labels:", len(internalLabels))
print(getElementFreqs(internalLabels.values()))

print("----CROSSMATCHES----")

xtids = crossmatchLabelMap.transientLabels.keys()
labelCountsForAll = list(map(lambda tid: len(crossmatchLabelMap.getLabels(tid)), xtids))
labelCountsForLabelled = list(filter(lambda l: l>0, labelCountsForAll))
avgLabelsForLabelled = sum(labelCountsForLabelled) / float(len(labelCountsForLabelled))

unaLabels = crossmatchLabelMap.getUnanimousLabelDict()
majLabels = crossmatchLabelMap.getMajorityLabelDict()

print("Average label num:", round(avgLabelsForLabelled, 2))
print("Unanimous agreement:", len(unaLabels))
print("Majority agreement: ", len(majLabels))
print(getElementFreqs(unaLabels.values()))

print("----COMBINED----")

labels = combinedLabelMap.getUnanimousLabelDict()
print("Labels:", len(labels))
print(getElementFreqs(labels.values()))

# -- Write ids with labels to file --

with open(outFile, "w") as f:
	writer = csv.writer(f)
	writer.writerows(labels.items())