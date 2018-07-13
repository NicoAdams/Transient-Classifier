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

def getCompletenessPurityCurve(predictProbaOutput, actual):
	"""
	Inputs:
	- predictProbaOutput: Classifier output from the `predict_proba` function
	- actual: The actual labels for the classified examples
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
	for i in range(len(probsSorted)):
		p, a = probsSorted[i], actualSorted[i]
		
		if p > currThresh:			
			_updateClassTable(classTable, actualForCurrThresh)
			actualForCurrThresh = [0, 0]
			
			currCompleteness, currPurity = getCompletenessAndPurity(classTable)
			currThresh = p
			cpt.append((currCompleteness, currPurity, currThresh))
			
		actualForCurrThresh[a] += 1
	
	# Adds the cpt values for thresh = 1
	currThresh = 1
	currCompleteness, currPurity = getCompletenessAndPurity(makeClassTable([0]*len(actualSorted), actualSorted))
	cpt.append((currCompleteness, currPurity, currThresh))
	
	completeness, purity, threshold = zip(*cpt)
	return completeness, purity, threshold

def getCPTForPurity(predictProbaOutput, actual, purity):
	"""
	Inputs:
	- predictProbaOutput: Classifier output from the `predict_proba` function
	- actual: The actual labels for the classified examples
	- purity: The purity desired
	Returns: (completeness, purity, threshold) for the minimum threshold yielding the purity specified
	(Note that this purity might be higher than the one you specified)
	"""
	cList, pList, tList = getCompletenessPurityCurve(predictProbaOutput, actual)
	for i in range(len(cList)):
		if pList[i] >= purity: return cList[i], pList[i], tList[i]
