from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote
import json

# TODO: I don't set a "whichquery" arg, but it takes in ether "imaging" or "spectra" -- what do they do? Could filter out hosts that are not spectroscopically confirmed
# TODO: The TNS catalog has redshift values, but we should try to get them from SDSS queries as well. Currently this does not happen 

# Example search URL:
# http://skyserver.sdss.org/dr14/SkyServerWS/SearchTools/RadialSearch?ra=258.2&dec=64&radius=4.1&whichway=equatorial&limit=10&format=html&fp=none&uband=0,17&check_u=u&gband=0,15&check_g=g&whichquery=imaging

baseUrl = "http://skyserver.sdss.org/dr14/SkyServerWS/SearchTools/"
radialSearchUrl = baseUrl + "RadialSearch?"
sqlSearchUrl = baseUrl + "SqlSearch?"

# --- Helper functions ---

def getSDSSRadialSearchUrl(ra, dec, radius): # Radius should actually be 5 arcsec, this is 1 arcmin
	# Returns the URL that will search SDSS at the given ra, dec, and radius
	args = "ra={}&dec={}&radius={}&limit=0".format(ra, dec, radius)
	return radialSearchUrl+args

def getSDSSNearestHostsCommand(ra, dec, radius, hostNum):
	cmd = ("SELECT TOP {} p.objid, p.run, p.rerun, p.camcol, p.field, p.obj, p.type, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z, n.distance " 
	 	    "FROM fGetNearbyObjEq({},{},{}) n, PhotoPrimary p WHERE n.objID=p.objID ORDER BY distance"
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
