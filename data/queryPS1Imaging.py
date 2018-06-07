from urllib.request import urlopen
from PIL import Image
from bs4 import BeautifulSoup

# Only requests "GRIZ" filters. Omits Y because it's PS1-specific
# Example URL:
# http://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=217.12921%2C37.06777&filter=g&filter=r&filter=i&filter=z&filetypes=stack&auxiliary=data&size=40&output_size=20&verbose=0&autoscale=99.500000&catlist=

def arcsec2pix(arcsec): return arcsec*4

def getPS1ImageHTMLUrl(ra, dec, arcsec, outputPixels):
	pixels = arcsec2pix(arcsec)
	url = (
		"http://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos={}%2C{}&filter=g&filter=r&filter=i&filter=z"
		"&filetypes=stack&auxiliary=data&size={}&output_size={}&verbose=0&autoscale=99.500000&catlist="
		).format(ra, dec, pixels, outputPixels)
	return url

def queryPS1ImageHTML(ra, dec, arcsec, outputPixels):
	url = getPS1ImageHTMLUrl(ra, dec, arcsec, outputPixels)
	response = urlopen(url)
	html = response.read()
	return html

def getPS1ImageSourcesFromHTML(html):
	bs = BeautifulSoup(html, 'html.parser')
	imgs = bs.findAll("img")
	imgs = imgs[1:] # First image is the logo
	srcs = ['http:'+i['src'] for i in imgs]
	return srcs
	
def queryPS1Images(ra, dec, arcsec, outputPixels):
	html = queryPS1ImageHTML(ra, dec, arcsec, outputPixels)
	srcs = getPS1ImageSourcesFromHTML(html)
	images = []
	for src in srcs:
		response = urlopen(src)
		images.append(Image.open(response))
	return images

def queryPS1ImageData(ra, dec, arcsec, outputPixels):
	images = queryPS1Images(ra, dec, arcsec, outputPixels)
	pixelData = []
	for i in images: pixelData.extend(i.getdata())
	return pixelData
