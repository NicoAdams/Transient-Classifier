import csv
from astropy import units as u
from astropy.coordinates import SkyCoord
import os

def insertSpaces(str, positionSet):
	# Inserts a space before each position in positionSet
	newStr = ""
	for i in range(len(str)):
		if i in positionSet: newStr+=" "
		newStr+=str[i]
	return newStr

def convertJ2000ToDegPair(j2000, roundTo=7):
	# j2000: The coord string in J2000 coords
	# rountTo: The number of decimal places to include in the final coords
	# Returns: The RA/dec of the given j2000 string as a pair of degrees
	# Insert spaces as needed for astropy to parse it
	coordString = insertSpaces(j2000, set([2,4,13,15]))
	# Convert to SkyCoord
	coord = SkyCoord(coordString, unit=(u.hourangle, u.deg))
	# Return the new numbers as a tuple
	return(round(coord.ra.deg, roundTo), round(coord.dec.deg, roundTo)) 
                                               
with open("GCVS5_dimmest.csv", "r") as fin:
	with open("GCVS5_dimmest_coords.csv", "w+") as fout:
		reader = csv.reader(fin)
		writer = csv.writer(fout)
		headerRow = True
		
		for row in reader:
			if headerRow:
				newHeaderRow = row[:2] + ["RA", "Dec"] + row[3:]
				writer.writerow(newHeaderRow)
				headerRow = False
				continue
			# Parse the new coordinates
			j2000 = row[2]
			coords = convertJ2000ToDegPair(j2000)
			# Creates the new row
			newRow = row[:2] + [str(coords[0]), str(coords[1])] + row[3:]
			# Writes the new row
			writer.writerow(newRow)
