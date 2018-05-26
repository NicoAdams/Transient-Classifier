from urllib.request import urlopen
from urllib.error import HTTPError
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

def getSDSSRadialSearchUrl(ra, dec, radius): # Radius should actually be 5 arcsec, this is 1 arcmin
	# Returns the URL that will search SDSS at the given ra, dec, and radius
	args = "ra={}&dec={}&radius={}&limit=0".format(ra, dec, radius)
	return radialSearchUrl+args

def getSDSSNearestHostsCommand(ra, dec, radius, hostNum):
	cmd = ("SELECT TOP {}"
		   " p.objid, p.type, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z, p.err_u, p.err_g, p.err_r, p.err_i, p.err_z, n.distance, pz.z AS redshift, pz.zErr AS err_redshift"
	 	   " FROM fGetNearbyObjEq({},{},{}) n"
	 	   " JOIN PhotoPrimary p ON n.objID=p.objID"
	 	   " LEFT JOIN Photoz pz ON pz.objID=p.objID"
	 	   " ORDER BY distance"
	 	  ).format(hostNum, ra, dec, radius)
	return cmd

def getSDSSNearestHostsUrl(ra, dec, radius, hostNum):
	urlCmd = quote(getSDSSNearestHostsCommand(ra, dec, radius, hostNum))
	args = "cmd={}&limit=0".format(urlCmd)
	url = sqlSearchUrl + args
	return url

def processResponse(responseReadout):
	responseObject = json.loads(responseReadout.decode("utf-8"))
	hostsList = responseObject[0]['Rows'] # Extracts the dictionary of hosts info
	hostsList = list(map(convertNoneValsTo0, hostsList))
	return hostsList

# --- Search functions ---

def searchByUrl(url):
	response = urlopen(url)
	return processResponse(response.read())

def searchRadial(ra, dec, radius):
	# Returns a list of hosts from SDSS (unlimited length, no particular order)
	url = getSDSSRadialSearchUrl(ra, dec, radius)
	return searchByUrl(url)

def searchNearestHosts(ra, dec, radius, hostNum):
	# Returns a list of hostNum hosts from SDSS, ordered by distance
	url = getSDSSNearestHostsUrl(ra, dec, radius, hostNum)
	return searchByUrl(url)

def searchNearestHost(ra, dec, radius):
	# Returns a dict on the nearest host, or None if there is no host in the given radius
	url = getSDSSNearestHostsUrl(ra, dec, radius, 1)
	hostsList = searchByUrl(url)
	if len(hostsList) == 0: return None
	return hostsList[0]
