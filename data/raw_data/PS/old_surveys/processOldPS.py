import json
import csv

inputFile = 'PS/old_surveys/OldPS_combined.json'
tnsCatalogFile = 'TNS/TNScatalog_processed.csv'
outputFile = 'PS/old_surveys/OldPS_non_tns.csv'

raDecTolerance = 0.001
def sameRaDec(rd1, rd2):
	return abs(rd1[0]-rd2[0]) < raDecTolerance and abs(rd1[1]-rd2[1]) < raDecTolerance

jsonFields = ['transient_object_id', 'class', 'ra', 'dec', 'first_detect_mag', 'first_detect_filter']
def getCSVRow(jsonRow):
	return [jsonRow[f] for f in jsonFields]

def rowHasType(jsonRow):
	return jsonRow['class'] != "NULL"

# Filters duplicate data and missing types
data = None
with open(inputFile) as f: data = json.load(f)
rows = data['rows']
rows = list({r['transient_object_id']: r for r in rows}.values())
rows = list(filter(rowHasType, rows))

# Check for uniqueness against TNS
tnsRaDecs = None
with open(tnsCatalogFile) as f: 
	dictReader = csv.DictReader(f)
	tnsRaDecs = [(float(r['RA']), float(r['DEC'])) for r in dictReader]
nonTNSRows = []
for r in rows:
	psRD = (float(r['ra']), float(r['dec']))
	if not any(map(lambda tnsRD: sameRaDec(psRD, tnsRD), tnsRaDecs)):
		nonTNSRows.append(r)

# Writes unique rows to CSV
with open(outputFile, 'w') as f:
	writer = csv.writer(f)
	writer.writerow(jsonFields)
	for jsonRow in nonTNSRows: writer.writerow(getCSVRow(jsonRow))
	
