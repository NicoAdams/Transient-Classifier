import numpy as np

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