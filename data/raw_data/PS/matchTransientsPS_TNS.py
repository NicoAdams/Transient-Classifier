import csv
from astropy import SkyCoord

psFile = "PS/psst_confirmed_and_good.tsv"
psTransientIdFile = "PS/PS_transients_with_labels.csv"
tnsFile = "TNS/TNScatalog_processed.csv"

# Get PS transient IDs

# Get PS transient RA/DECs
with open(psFile) as f:
	reader = csv.DictReader(f)
	

# Get TNS transient RA/DECs