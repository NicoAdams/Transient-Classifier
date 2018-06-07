from urllib.request import urlopen
from PIL import Image

# Example URL:
# http://skyserver.sdss.org/dr14/SkyServerWS/ImgCutout/getjpeg?TaskName=Skyserver.Chart.Navi&ra=179.689293428354&dec=-0.454379056007667&scale=0.79224&width=1536&height=1536&opt=

baseUrl = "http://skyserver.sdss.org/dr14/SkyServerWS/ImgCutout/getjpeg?TaskName=Skyserver.Chart.Navi"

def getSDSSImageUrl(ra, dec, scale, sideLen):
	args = "&ra={}&dec={}&scale={}&width={}&height={}&opt=".format(ra, dec, scale, sideLen, sideLen)
	return baseUrl + args

def querySDSSImage(ra, dec, scale, sideLen):
	url = getSDSSImageUrl(ra, dec, scale, sideLen)
	response = urlopen(url)
	image = Image.open(response)
	return image

