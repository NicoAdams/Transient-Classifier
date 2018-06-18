import csv
import sys
sys.path.append('.')
import processUtil

# -- Parameters --

tnsCatalogFile = 'raw_data/TNS/TNScatalog_processed.csv'
oldPSCatalogFile = 'raw_data/PS/old_surveys/OldPS_non_tns.csv'

tnsLabelMapFile = 'raw_data/TNS/TNS_type_label_map.csv'
oldPSLabelMapFile = 'raw_data/PS/old_surveys/OldPS_type_label_map.csv'

outputFile = 'process_data/combined_catalogs/TNS_OldPS_Catalog.csv'

# -- Helper functions --

headers = ['id', 'label', 'ra', 'dec', 'mag']

tnsReader = csv.DictReader(open(tnsCatalogFile))
oldPSReader = csv.DictReader(open(oldPSCatalogFile))

tnsLabelMap = processUtil.generateLabelMap(tnsLabelMapFile)
oldPSLabelMap = processUtil.generateLabelMap(tnsLabelMapFile)
otherType = "OTHER"

def getLabel(transType, labelMap):
	return labelMap[transType] if transType in tnsLabelMap else otherType

def processTNSRow(tnsRow):
	transId = processUtil.generateUUID()
	label = getLabel(tnsRow['Type'], tnsLabelMap)
	ra, dec = tnsRow['RA'], tnsRow['DEC']
	mag = tnsRow['Discovery Mag']
	return [transId, label, ra, dec, mag]

def processOldPSRow(psRow):
	transId = processUtil.generateUUID()
	label = getLabel(psRow['class'], oldPSLabelMap)
	ra, dec = psRow['ra'], psRow['dec']
	mag = psRow['first_detect_mag']
	return [transId, label, ra, dec, mag]

# -- Script --

processUtil.confirmOverwrite(outputFile)

processUtil.createOrClearFile(outputFile)

processUtil.appendRow(headers, outputFile)
processUtil.appendRows([processTNSRow(r) for r in tnsReader], outputFile)
processUtil.appendRows([processOldPSRow(r) for r in oldPSReader], outputFile)
