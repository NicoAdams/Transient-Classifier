from astropy import units as u
from astropy.coordinates import Angle
import csv

fin = open("TNSsample.csv", "r")
fout = open("TNSsample_deg_converted.csv", "w")

reader = csv.reader(fin)
writer = csv.writer(fout)

def createNewRow(row, newRa, newDec):
	return row[:4] + [newRa, newDec] + row[4:]

rowCount = 0

headerRow = True
for row in reader:
	
	rowCount += 1
	
	if headerRow:
		headerRow = False
		writer.writerow(createNewRow(row, "RA (deg)", "DEC (deg)"))
		continue
	
	ra = row[2]
	dec = row[3]
	raDeg = round(Angle(ra, unit=u.hour).degree, 5)
	decDeg = round(Angle(dec, unit=u.deg).degree, 5)
	writer.writerow(createNewRow(row, raDeg, decDeg))
	