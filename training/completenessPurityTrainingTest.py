import pandas as pd
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import f1_score as F1
from sklearn.metrics.classification import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import matplotlib
matplotlib.use('tkagg') # Comment this out if matplotlib is malfunctioning on your machine!
from matplotlib import pyplot as plt

# -- Parameters --

trainingFileTemplate = 'data/training/sn_dropped/TNS_OldPS_SDSS_6arcsec_training_0.8_dropped_{}.csv'
trainingFileCount = 10

trainRatio = 0.75
purityGoal = 0.95

randomSeed = 1

featureColumns = ['host_label', 'offset', 'redshift', 'u', 'g', 'r', 'i', 'z', 'u-g', 'g-r', 'r-i', 'i-z']
labelColumn = 'transient_label'

makeClassifier = lambda: MLPClassifier(
	hidden_layer_sizes=19,
	max_iter=10**5,
	learning_rate_init=0.005,
	activation='relu',
	random_state=randomSeed
)

# -- Helper functions --

def processTransientLabel(transientLabel):
	return 1 if transientLabel == "SN" else 0

def asPct(num, roundTo=2):
	return str(round(num*100, roundTo))+"%"

def assertSameLength(list1, list2):
	l1, l2 = len(list1), len(list2)
	assert l1 == l2, "Lists must be same length, but have lengths {} and {}".format(l1, l2)

# classTable is indexed by: [predicted][actual]
def makeClassTable(predicted, actual):
	assertSameLength(predicted, actual)
	classTable = [[0,0],[0,0]]
	for i in range(len(actual)): classTable[predicted[i]][actual[i]] += 1
	return classTable

def getCompletenessAndPurity(classTable):
	truePositives = classTable[1][1]
	falsePositives = classTable[1][0]
	falseNegatives = classTable[0][1]
	
	predictedPositives = truePositives + falsePositives
	actualPositives = truePositives + falseNegatives
	
	completeness = truePositives / float(actualPositives)
	purity = truePositives / float(predictedPositives) if predictedPositives > 0 else 1
	return completeness, purity

def _updateClassTable(classTable, actualForCurrThresh):
	classTable[1][0] -= actualForCurrThresh[0]
	classTable[1][1] -= actualForCurrThresh[1]
	classTable[0][0] += actualForCurrThresh[0]
	classTable[0][1] += actualForCurrThresh[1]

def getCompletenessPurityCurve(predictProbaOutput, actual, step=True):
	"""
	Inputs:
	- predictProbaOutput: Classifier output from the `predict_proba` function
	- actual: The actual labels for the classified examples
	- step: If you plan to plot these results, "step=True" will make the plot step upward at right angles
	
	Returns:
	- Completeness list
	- Purity list
	- Threshhold list
	"""
	
	# Obtains and sorts the "predicted probabilities" (probs) and "actual labels" (actual) lists
	probs = predictProbaOutput[:,1]
	assertSameLength(probs, actual)
	probsSorted, actualSorted = zip(*sorted(zip(probs, actual)))
	
	# Creates the initial class table
	classTable = makeClassTable([1]*len(actualSorted), actualSorted)
	
	# Initializes the cpt list (completeness, purity, thresh)
	cpt = []
	
	# Adds the cpt values for thresh = 0
	currThresh = 0
	currCompleteness, currPurity = getCompletenessAndPurity(classTable)
	cpt = [(currCompleteness, currPurity, currThresh)]
	
	# Loops over every possible thresh
	actualForCurrThresh = [0, 0]
	lastPurity = 0
	for i in range(len(probsSorted)):
		p, a = probsSorted[i], actualSorted[i]
		
		if p > currThresh:			
			_updateClassTable(classTable, actualForCurrThresh)
			actualForCurrThresh = [0, 0]
			
			currCompleteness, currPurity = getCompletenessAndPurity(classTable)
			currThresh = p
			if currPurity >= lastPurity:
				if step: cpt.append((currCompleteness, lastPurity, currThresh))
				cpt.append((currCompleteness, currPurity, currThresh))
				lastPurity = currPurity
			
		actualForCurrThresh[a] += 1
	
	# Adds the cpt values for thresh = 1
	currThresh = 1
	currCompleteness, currPurity = getCompletenessAndPurity(makeClassTable([0]*len(actualSorted), actualSorted))
	cpt.append((currCompleteness, currPurity, currThresh))
	
	completenessCurve, purityCurve, threshCurve = zip(*cpt)
	return completenessCurve, purityCurve, threshCurve

def getCPTForPurity(predictProbaOutput, actual, purity):
	"""
	Inputs:
	- predictProbaOutput: Classifier output from the `predict_proba` function
	- actual: The actual labels for the classified examples
	- purity: The purity desired
	
	Returns: (completeness, purity, threshold) for the minimum threshold yielding the purity specified
	(Note that this purity might be higher than the one you specified)
	"""
	cList, pList, tList = getCompletenessPurityCurve(predictProbaOutput, actual, step=False)
	for i in range(len(cList)):
		if pList[i] >= purity: return cList[i], pList[i], tList[i]
	return -1, -1, -1
	
def getPredictionsForThresh(predictProbaOutput, thresh):
	probs = predictProbaOutput[:,1]
	mapProbsToPredictions = np.vectorize(lambda p: (1 if p >= thresh else 0)) 
	return mapProbsToPredictions(probs)

def aggregateCPCurvesByPurity(completenessCurves, purityCurves, purityBinSize=0.01):
	assertSameLength(completenessCurves, purityCurves)
	numCurves = len(completenessCurves)
	
	def _getPurityIndex(purityCurve, currPurityBin, startIndex=0):
		for i in range(startIndex, len(purityCurve)):
			if purityCurve[i] >= currPurityBin: return i
		return len(purityCurve)-1
	
	aggPurity = np.arange(0, 1+purityBinSize, purityBinSize)
	aggCompleteness = [0] * len(aggPurity)
	lastCurveIndexList = [0] * numCurves
	for binIndex in range(len(aggPurity)):
		purityBin = aggPurity[binIndex]
		for curveNum in range(numCurves):
			
			# Obtains curves
			currCompletenessCurve, currPurityCurve = \
				completenessCurves[curveNum], purityCurves[curveNum] 
			
			# Gets and stores the new index in the current curve
			lastCurveIndex = lastCurveIndexList[curveNum]
			curveIndex = _getPurityIndex(currPurityCurve, purityBin, startIndex=lastCurveIndex)
			lastCurveIndexList[curveNum] = curveIndex
			
			# Gets and stores completeness for the current curve
			curveCompleteness = currCompletenessCurve[curveIndex]
			aggCompleteness[binIndex] += curveCompleteness / float(numCurves)
	
	return aggCompleteness, aggPurity
	
# -- Trains classifier --

print("Classifier:", makeClassifier())
print()

completenessList = []
purityList = []
threshList = []

completenessCurves = []
purityCurves = []
threshCurves = []

trainingFiles = [trainingFileTemplate.format(i) for i in range(1,trainingFileCount+1)]
for trainingFile in trainingFiles:
	
	dfRaw = pd.read_csv(trainingFile)
	df = dfRaw.copy()

	# Creates columns containing the differences between consecutive filters
	df['u-g'] = dfRaw['u'] - dfRaw['g']
	df['g-r'] = dfRaw['g'] - dfRaw['r']
	df['r-i'] = dfRaw['r'] - dfRaw['i']
	df['i-z'] = dfRaw['i'] - dfRaw['z']

	df = df.dropna() # Removes any rows with missing data
	df = df[df['redshift'] >= 0] # Removes unknown (-9999) redshift values
	
	X = df[featureColumns].values
	y = df[labelColumn].apply(processTransientLabel).values
	
	X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=trainRatio, test_size=(1-trainRatio), random_state=randomSeed)
	
	# Scales the training data
	scaler = StandardScaler()
	scaler.fit(X_train)
	X_train = scaler.transform(X_train)
	X_test = scaler.transform(X_test)
	
	# Creates and trains the classifier
	clf = makeClassifier()
	clf.fit(X_train, y_train)
	
	# Makes predictions on the test data
	y_probs = clf.predict_proba(X_test)
	
	# Calculates completeness, purity and thresh values for the goal purity
	completeness, purity, thresh = getCPTForPurity(y_probs, y_test, purityGoal)
	completenessList.append(completeness)
	purityList.append(purity)
	threshList.append(thresh)
	
	# Makes predictions based on the calculated threshold
	y_predicted = getPredictionsForThresh(y_probs, thresh)
	
	# Calculates completeness-purity curve for these predictions
	completenessCurve, purityCurve, threshCurve = getCompletenessPurityCurve(y_probs, y_test, step=False)
	completenessCurves.append(completenessCurve)
	purityCurves.append(purityCurve)
	threshCurves.append(threshCurve)
	
	# Stats!
	f1AllSN =   F1(y_test, [1]*len(y_test))
	f1Actual =  F1(y_test, y_predicted)
	f1Inverse = F1(y_test, y_predicted, pos_label=0)
	classTable = pd.crosstab(
		np.asarray(y_test),
		np.asarray(y_predicted),
		rownames=['Actual'],
		colnames=['Pred']
	)
	print("----- Dataset:", trainingFile, "-----")
	print("Goal purity:           ", asPct(purityGoal))
	print("Achieved purity:       ", asPct(purity))
	print("Achieved completeness: ", asPct(completeness))
	print("Threshold:             ", asPct(thresh))
	print("F1 (all SN): ", asPct(f1AllSN))
	print("F1 (actual): ", asPct(f1Actual))
	print("F1 (inverse):", asPct(f1Inverse))
	print(classTable)
	print()

# -- Aggregate statistics --

# The average of the completeness-purity curve at each purity value
aggCompleteness, aggPurity = aggregateCPCurvesByPurity(completenessCurves, purityCurves, purityBinSize=0.005)

print("----- TOTALS ----")
print("Mean purity:       ", asPct(np.mean(purityList)))
print("Mean completeness: ", asPct(np.mean(completenessList)))
print("Mean thresh:       ", asPct(np.mean(threshList)))
print()
print("SD purity:         ", asPct(np.std(purityList)))
print("SD completeness:   ", asPct(np.std(completenessList)))
print("SD thresh:         ", asPct(np.std(threshList)))

for i in range(len(completenessCurves)):
	plt.plot(purityCurves[i], completenessCurves[i], linewidth=1, dashes=[2, 2])
plt.plot(aggPurity, aggCompleteness, linewidth=2)
plt.title('Purity vs Completeness for {} 80% SN-reduced datasets'.format(trainingFileCount))
plt.xlabel('Purity')
plt.ylabel('Completeness')
plt.axis([0.75, 1, 0, 1])
plt.show()
