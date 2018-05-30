from astropy import units as u
from astropy.coordinates import Angle
import csv

reader = csv.reader(open("raw_data/TNS/TNScatalog_raw.csv"))
writer = csv.writer(open("raw_data/TNS/TNScatalog_processed.csv", "w"))

# Index of the TNS type label
tnsTypeIndex = 4

# Replaces RA and DEC in a row
def replaceRaDec(row, newRa, newDec):
	return row[:2] + [newRa, newDec] + row[4:]

headerRow = True
for row in reader:
	
	if headerRow:
		headerRow = False
		newHeaders = replaceRaDec(row, "RA", "DEC")
		writer.writerow(newHeaders)
		continue
	
	# Filters rows by type
	if not row[tnsTypeIndex]: continue
	
	ra = row[2]
	dec = row[3]
	raDeg = round(Angle(ra, unit=u.hour).degree, 5)
	decDeg = round(Angle(dec, unit=u.deg).degree, 5)
	row = replaceRaDec(row, raDeg, decDeg)	
	
	writer.writerow(row)
	