import ast
import urllib2

dataObj = urllib2.urlopen("https://api.sne.space/catalog?format=CSV") # The redshift of one particular object
dataString = dataObj.read()

f = open("osc-data.csv", 'w+')
f.write(dataString)
