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

trainingInputFile = 'data/training/TNS_OldPS_SDSS_120arcsec_training.csv'

snKeepProb = 1
# cxWeightRatio = 1

# -- Helper functions --

def getLabelNum(transientLabel):
	return 1 if transientLabel == "SN" else 0

def getHostLabel(hostLabel):
	return 1 if hostLabel == "GALAXY" else 0

def getRowFeatures(rowDict):
	hostLabel = getHostLabel(rowDict['host_label'])
	offset = float(rowDict['offset'])
	redshift = float(rowDict['redshift'])
	u, g, r, i, z = (float(rowDict[f]) for f in 'ugriz')
	return [hostLabel, offset, redshift, r, u-g, g-r, r-i, i-z]
	
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

def randomProb(p):
	return random.random() < p

# -- Gets data --

print("Extracting data...")

rows = []
with open(trainingInputFile) as f:
	dictReader = csv.DictReader(f)
	for r in dictReader:
		if getRowLabel(r) == 0 or randomProb(snKeepProb):
			rows.append(r)
random.shuffle(rows)

X = [getRowFeatures(r) for r in rows]
y = [getRowLabel(r) for r in rows]

for cxWeightRatio in [(i+1)**2 for i in range(20)]:
	
	# -- Trains classifier --

	# print("Training classifier...")
	# print("CX Weight:", cxWeightRatio)

	testFraction = 0.25
	trainingNum = int(len(rows) * (1-testFraction))

	trainingX = X[:trainingNum]
	trainingy = y[:trainingNum]

	start = time.time()

	classifier = svm.SVC(class_weight={0: cxWeightRatio})
	classifier.fit(trainingX, trainingy)

	end = time.time()

	# print("Classifier trained. Time taken:", end-start)

	# -- Tests classifier --

	# print("Testing classifier...")

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

	# print("Tested:       ", numTested)
	# print("SN:           ", actualPositives)
	# print()

	# print('\tP=1\tP=0')
	# print('A=1\t{}\t{}'.format(correctPositives, falseNegatives))
	# print('A=0\t{}\t{}'.format(falsePositives, correctNegatives))
	# print()
	
	# print(cxWeightRatio, correctPositives, correctNegatives, falsePositives, falseNegatives, sep='\t')

	# print("F1 (+, all SN):", asPercent(getF1FromCombinedStats(actualPositives, actualNegatives, 0)))
	# print("F1 (+):        ", asPercent(getF1FromCombinedStats(correctPositives, falsePositives, falseNegatives)))
	# print("F1 (-):        ", asPercent(getF1FromCombinedStats(correctNegatives, falseNegatives, falsePositives)))
	# print()

	print(cxWeightRatio, getF1FromCombinedStats(correctPositives, falsePositives, falseNegatives), getF1FromCombinedStats(correctNegatives, falseNegatives, falsePositives))

