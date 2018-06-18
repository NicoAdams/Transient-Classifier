import csv

psFile = "raw_data/PS/psst_confirmed_and_good.tsv"
psTypeMapFile = "raw_data/PS/PS_internal_type_map.csv"

psTypesToSkip = {"", "NULL", "Observed"}

def createTypeMap(typeMapFileName):
	with open(typeMapFileName) as f:
		reader = csv.reader(f)
		return {row[0]: row[1] for row in reader}

def getLabelNum(label):
	return 1 if label == "SN" else 0

psTypeMap = createTypeMap(psTypeMapFile)

rows = None
with open(psFile) as f:
	reader = csv.DictReader(f, delimiter="\t")
	rows = [row for row in reader]

total = 0

actualPostives = 0
predictedPositives = 0

classificationTable = [[0, 0], [0, 0]]

for row in rows:
	psType = row['observation_status']
	sherlockLabel = row['sherlockClassification']
	if psType in psTypesToSkip: continue
	
	A = getLabelNum(psTypeMap[psType])
	P = getLabelNum(sherlockLabel)
	
	total += 1
	if A == 1: actualPostives += 1
	if P == 1: predictedPositives += 1
	classificationTable[P][A] += 1

print("Total:", total)
print("A=1:  ", actualPostives)
print("P=1:  ", predictedPositives)
print()

t = classificationTable
print("\tP=1\tP=0")
print("A=1\t{}\t{}".format(t[1][1], t[0][1]))
print("A=0\t{}\t{}".format(t[1][0], t[0][0]))


