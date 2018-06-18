import csv
from sklearn import svm
import random
import time

# Features:
# - Host label
# - Host offsetd
# - Host redshift
# - One host filter (r)
# - All host filter diffs

trainingInputFile = 'data/training/TNS_OldPS_SDSS_2host_training.csv'

# -- Helper functions --

def getLabelNum(transientLabel):
	return 1 if transientLabel == "SN" else 0

def getHostLabel(hostLabel):
	return 1 if hostLabel == "GALAXY" else 0

def getForBothHosts(header, rowDict, processFunc=(lambda f: f)):
	return processFunc(rowDict[header+"_1"]), processFunc(rowDict[header+"_2"])

def getRowFeatures(rowDict):
	hostLabels = getForBothHosts('host_label', rowDict, getHostLabel)
	offsets = getForBothHosts('offset', rowDict, float)
	redshifts = getForBothHosts('redshift', rowDict, float)
	u, g, r, i, z = [getForBothHosts(f, rowDict, float) for f in 'ugriz']
	featureLists = [
		[
			hostLabels[h], offsets[h], redshifts[h],
			r[h], u[h]-g[h], g[h]-r[h], r[h]-i[h], i[h]-z[h]
		]
		for h in range(2)
	]
	return featureLists[0] + featureLists[1]
	
def getRowLabel(rowDict):
	return getLabelNum(rowDict['transient_label'])
	
def getF1FromPR(p, r):
	if p + r == 0: return 0
	return 2 * p * r / (p + r)

def getF1FromCombinedStats(correctPositives, falsePositives, falseNegatives):
	predictedPositives = correctPositives + falsePositives
	actualPositives = correctPositives + falseNegatives
	if predictedPositives == 0 or actualPositives == 0: return 0
	
	p = correctPositives / (predictedPositives)
	r = correctPositives / (actualPositives)
	return getF1FromPR(p, r)

def asPercent(num, roundTo=2):
	return str(round(num * 100, 2)) + "%"

# -- Gets data --

print("Extracting data...")

rows = None
with open(trainingInputFile) as f:
	dictReader = csv.DictReader(f)
	rows = [r for r in dictReader]
random.shuffle(rows)

X = [getRowFeatures(r) for r in rows]
y = [getRowLabel(r) for r in rows]

# -- Trains classifier --

print("Training classifier...")

testFraction = 0.25
trainingNum = int(len(rows) * (1-testFraction))

trainingX = X[:trainingNum]
trainingy = y[:trainingNum]

start = time.time()

classifier = svm.SVC()
classifier.fit(trainingX, trainingy)

end = time.time()

print("Classifier trained. Time taken:", end-start)

# -- Tests classifier --

print("Testing classifier...")

testX = X[trainingNum:]
testy = y[trainingNum:]

numTested = 0
numCorrect = 0

# Prediction stats
predictedPositives = 0
predictedNegatives = 0

# Actual stats
actualPositives = 0
actualNegatives = 0

# Combined stats
correctPositives = 0
correctNegatives = 0
falsePositives = 0
falseNegatives = 0

for i in range(len(testX)):
	predicted = classifier.predict([testX[i]])
	actual = testy[i]
	
	numTested += 1
	if predicted == actual: numCorrect += 1
	
	if predicted == 1: predictedPositives += 1
	if actual == 1: actualPositives += 1
	
	if predicted == 0: predictedNegatives += 1
	if actual == 0: actualNegatives += 1
	
	if (predicted, actual) == (1, 1): correctPositives += 1
	if (predicted, actual) == (0, 0): correctNegatives += 1
	if (predicted, actual) == (1, 0): falsePositives += 1
	if (predicted, actual) == (0, 1): falseNegatives += 1

print("Done!")
print("Tested:       ", numTested)
print("SN:           ", actualPositives)
print()

print('\tP=1\tP=0')
print('A=1\t{}\t{}'.format(correctPositives, falseNegatives))
print('A=0\t{}\t{}'.format(falsePositives, correctNegatives))
print()

print("F1:            ", asPercent(getF1FromCombinedStats(correctPositives, falsePositives, falseNegatives)))
print("F1 (all SN):   ", asPercent(getF1FromCombinedStats(actualPositives, actualNegatives, 0)))
print("F1 (negatives):", asPercent(getF1FromCombinedStats(correctNegatives, falseNegatives, falsePositives)))

