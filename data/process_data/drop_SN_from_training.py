import pandas as pd

inputFile = 'training/TNS_OldPS_SDSS_6arcsec_training.csv'
outputTemplate = 'training/sn_dropped/TNS_OldPS_SDSS_6arcsec_training_{}_dropped_{}.csv'
copies = 10
dropRatio = 0.8

labelCol = 'transient_label'
snLabel = 'SN'

def pruneSNRows(df, dropRatio):
	return df.drop(df.query('{} == "{}"'.format(labelCol, snLabel)).sample(frac=dropRatio).index)

def getOutputFile(copyNum):
	return outputTemplate.format(dropRatio, copyNum)

df = pd.read_csv(inputFile)
print("Creating files...")
for copy in range(1, copies+1):
	pruneSNRows(df, dropRatio).to_csv(getOutputFile(copy), index=False)
print("Done!")