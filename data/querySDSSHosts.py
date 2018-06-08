from urllib.request import urlopen
from urllib.parse import quote
import json

# Example search URL:
# http://skyserver.sdss.org/dr14/SkyServerWS/SearchTools/RadialSearch?ra=258.2&dec=64&radius=4.1&whichway=equatorial&limit=10&format=html&fp=none&uband=0,17&check_u=u&gband=0,15&check_g=g&whichquery=imaging

baseUrl = "http://skyserver.sdss.org/dr14/SkyServerWS/SearchTools/"
radialSearchUrl = baseUrl + "RadialSearch?"
sqlSearchUrl = baseUrl + "SqlSearch?"

# --- Helper functions ---

def convertNoneValsTo0(hostDict):
	return {k: 0 if hostDict[k]==None else hostDict[k] for k in hostDict}

def getRadialSearchUrl(ra, dec, radius): # Radius should actually be 5 arcsec, this is 1 arcmin
	# Returns the URL that will search SDSS at the given ra, dec, and radius
	args = "ra={}&dec={}&radius={}&limit=0".format(ra, dec, radius)
	return radialSearchUrl+args

def getSQLSearchCommandUrl(command):
	urlCmd = quote(command)
	args = "cmd={}&limit=0".format(urlCmd)
	url = sqlSearchUrl + args
	return url

def getSDSSNearestHostsCommand(ra, dec, radius, hostNum):
	return (
		"SELECT TOP {}"
		" p.objid, p.type, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z, p.err_u, p.err_g, p.err_r, p.err_i, p.err_z, n.distance AS offset, pz.z AS redshift, pz.zErr AS err_redshift"
 	    " FROM fGetNearbyObjEq({},{},{}) n"
 	    " JOIN PhotoPrimary p ON n.objID=p.objID"
 	    " LEFT JOIN Photoz pz ON pz.objID=p.objID"
 	    " ORDER BY offset"
		).format(hostNum, ra, dec, radius)

def getSDSSNearestGalaxiesCommand(ra, dec, radius, hostNum):
	return (
		"SELECT TOP {}"
	    " g.objid, g.type, g.ra, g.dec, g.u, g.g, g.r, g.i, g.z, g.err_u, g.err_g, g.err_r, g.err_i, g.err_z, n.distance AS offset, pz.z AS redshift, pz.zErr AS err_redshift"
 	    " FROM fGetNearbyObjEq({},{},{}) n"
 	    " JOIN Galaxy g ON n.objID=g.objID"
 	    " LEFT JOIN Photoz pz ON pz.objID=g.objID"
 	    " ORDER BY offset"
		).format(hostNum, ra, dec, radius)

def getSDSSNearestStarsCommand(ra, dec, radius, hostNum):
	return (
		"SELECT TOP {}"
	    " s.objid, s.type, s.ra, s.dec, s.u, s.g, s.r, s.i, s.z, s.err_u, s.err_g, s.err_r, s.err_i, s.err_z, n.distance AS offset, pz.z AS redshift, pz.zErr AS err_redshift"
 	    " FROM fGetNearbyObjEq({},{},{}) n"
 	    " JOIN Star s ON n.objID=s.objID"
 	    " LEFT JOIN Photoz pz ON pz.objID=s.objID"
 	    " ORDER BY offset"
		).format(hostNum, ra, dec, radius)

def processResponse(responseReadout):
	responseObject = json.loads(responseReadout.decode("utf-8"))
	hostsList = responseObject[0]['Rows'] # Extracts the dictionary of hosts info
	hostsList = list(map(convertNoneValsTo0, hostsList))
	return hostsList

# --- Search functions ---

def searchByUrl(url):
	response = urlopen(url)
	return processResponse(response.read())

# Returns a list of hosts from SDSS within the given radius (unlimited length, no particular order)
def searchRadial(ra, dec, radius):
	url = getRadialSearchUrl(ra, dec, radius)
	return searchByUrl(url)

# Returns a list of hostNum hosts from SDSS, ordered by distance
def searchNearestHosts(ra, dec, radius, hostNum):
	command = getSDSSNearestHostsCommand(ra, dec, radius, hostNum)
	url = getSQLSearchCommandUrl(command)
	return searchByUrl(url)

# Returns a dict of the nearest host, or None if there is no host in the given radius
def searchNearestHost(ra, dec, radius):
	hostList = searchNearestHosts(ra, dec, radius, 1)
	if len(hostList) == 0: return None
	return hostList[0]

# Returns a list of hostNum galaxies from SDSS, ordered by distance
def searchNearestGalaxies(ra, dec, radius, hostNum):
	command = getSDSSNearestGalaxiesCommand(ra, dec, radius, hostNum)
	url = getSQLSearchCommandUrl(command)
	return searchByUrl(url)
	
# Returns a dict of the nearest galaxy by offset angle, or None if there is no galaxy in the given radius
def searchNearestGalaxy(ra, dec, radius):
	hostList = searchNearestGalaxies(ra, dec, radius, 1)
	if len(hostList) == 0: return None
	return hostList[0]

# Returns a list of hostNum galaxies from SDSS, ordered by distance
def searchNearestStars(ra, dec, radius, hostNum):
	command = getSDSSNearestStarsCommand(ra, dec, radius, hostNum)
	url = getSQLSearchCommandUrl(command)
	return searchByUrl(url)
	
# Returns a dict of the nearest galaxy by offset angle, or None if there is no galaxy in the given radius
def searchNearestStar(ra, dec, radius):
	hostList = searchNearestStars(ra, dec, radius, 1)
	if len(hostList) == 0: return None
	return hostList[0]
