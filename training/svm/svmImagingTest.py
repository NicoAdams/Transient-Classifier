import csv
from sklearn import svm
import random
import time

trainingInputFile = 'data/training/TNS_OldPS_PS_imaging_10px_training.csv'

snKeepProb = 1

# -- Helper functions --

def getLabelNum(transientLabel):
	return 1 if transientLabel == "SN" else 0

def getRowFeatures(row):
	# Here, could process the raw pixel data before feeding it in to the classifier
	return list(map(int, row[2:]))
	
def getRowLabel(row):
	return getLabelNum(row[1])
	
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
	reader = csv.reader(f)
	reader.__next__()
	for r in reader:
		if getRowLabel(r) == 0 or randomProb(snKeepProb):
			rows.append(r)
random.shuffle(rows)

X = [getRowFeatures(r) for r in rows]
y = [getRowLabel(r) for r in rows]

# -- Trains classifier --

print("Training classifier...")
start = time.time()

testFraction = 0.25
trainingNum = int(len(rows) * (1-testFraction))

trainingX = X[:trainingNum]
trainingy = y[:trainingNum]

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

