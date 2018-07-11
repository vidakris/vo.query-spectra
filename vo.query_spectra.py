#!/usr/bin/env python
# Query Virtual Observatory services for spectral data 
# v1.0 2017-01-24 VidaK vidakris@konkoly.hu

from astropy.coordinates import SkyCoord
from astropy import units as u
import pyvo as vo
import getopt
import sys

import warnings
warnings.simplefilter("ignore")		#suppress all warnings (typically VOTable exceptions)

def usage():
	print "Usage: "+sys.argv[0]+" <options> TARGET"
	print "Options:"
	print "-h, --help\t\tThis message" 
	print "-t, --target=TARGET\t\tSearch target resolved by CDS"
	print "-r, --radius=R\t\tSearch radius in arcmin"
	print "-o, --output=OUTFILE\t\tName of output file for download links"


#####################
# Command line args #
#####################

#Default options:
r=5/60. #arcmin
datatype="application/fits"

try:
	opts, args = getopt.getopt(sys.argv[1:], "ht:r:f:o:", \
	["help", "target=", "radius=", "format=","output="])

except getopt.GetoptError as err:
	print str(err)
	usage()
	sys.exit()

for opt, arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit()
	elif opt in ("-t", "--target"):
		targetname = arg
	elif opt in ("-r", "--radius"):
		r = float(arg)/60.
	elif opt in ("-f", "--format"):
		datatype = arg
	elif opt in ("-o", "--output"):
		outfilename = arg
	else:
		usage()
		sys.exit()

#Check if targetname is defined:
if "targetname" not in locals():
	try:
		targetname=args[0]
	except IndexError:
		usage()
		sys.exit()

if "outfilename" in locals():
	HARDCOPY = True
	outfile=open(outfilename,"w")
else:
	HARDCOPY = False

coords=SkyCoord.from_name(targetname)
print "Target: ",targetname
print "Coordinates: ",coords.to_string('hmsdms')
print "Search radius: ",r*60," arcmin"
print ""
print 20*"-"," Available services ",20*"-"

#Querying all Simple Spectrum Access services in all bands
#see http://www.ivoa.net/documents/SSA/20120210/REC-SSA-1.1-20120210.htm for protocol details
services = vo.regsearch(servicetype="ssa")

i=0
for service in services:
	print i,service.short_name," "*(20-len(service.short_name)),service.res_title
	i+=1

print "-"*60

i=0
for service in services:
	#Following 3 lines for testing purposes only:
	#if i in [32,48,71,76,80,81]:
	#if i in [62]:
	if True:
		try:
			spectra=vo.spectrumsearch(service.access_url,pos=(coords.ra.degree,coords.dec.degree),size=r,format=datatype)
			print i,service.short_name," "*(20-len(service.short_name)),len(spectra)," spectra found"
			switch=0			#in the case if one more random new "standard" url field pops up...
			if HARDCOPY:
				outfile.write("#"+service.short_name+" "*(19-len(service.short_name))+service.res_title+" "+service.res_type+"\n")
				for datafile in spectra:
					if datafile.getdataurl() != None:
						outfile.write(datafile.getdataurl()+"\n")
					elif datafile.has_key('url'):
						outfile.write(datafile.get('url')+"\n")
					elif datafile.has_key('DATA_LINK'):
						outfile.write(datafile.get('DATA_LINK')+"\n")
					else:
						if switch == 0:
							print datafile.keys()
							switch = 1
		except vo.DALQueryError as err:
			print i,service.short_name," "*(20-len(service.short_name)),"DAL Query Error: ",err.reason
		except vo.DALFormatError as err:
			print i,service.short_name," "*(20-len(service.short_name)),"XML/VOTable Error: ",err.cause		#so nice they could match their 3 exceptions...
		except vo.DALAccessError as err:
			print i,service.short_name," "*(20-len(service.short_name)),"DAL Access Error (try again later?): ",err.reason
	i+=1

if HARDCOPY:
	outfile.close()
