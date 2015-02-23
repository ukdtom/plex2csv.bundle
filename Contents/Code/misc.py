####################################################################################################
#	Helper file for Plex2CSV
# This one handles misc functions
####################################################################################################

from textwrap import wrap, fill
import re
import datetime


####################################################################################################
# This function will return info from extended page for movies
####################################################################################################
def GetExtInfo(ExtInfo, myField, default = ''):
	try:
		myLookUp = WrapStr(ExtInfo.xpath('Media/@' + myField)[0])
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will return info from different parts of a movie
####################################################################################################
def GetMoviePartInfo(ExtInfo, myField, default = ''):
	try:
		myLookUp = WrapStr(ExtInfo.get(myField))
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')


####################################################################################################
#	Pull's a field from the xml
####################################################################################################
def GetRegInfo(myMedia, myField, default = ''):
	try:
		if myField in ['rating']:			
			myLookUp = "{0:.1f}".format(float(myMedia.get(myField)))
		else:			
			myLookUp = WrapStr(fixCRLF(myMedia.get(myField)))
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
#	Wraps a string if needed
####################################################################################################
def fixCRLF(myString):
	myString = myString.decode('utf-8').replace('\r\n', ' ')
	myString = myString.decode('utf-8').replace('\n', ' ')
	myString = myString.decode('utf-8').replace('\r', ' ')
	return myString

####################################################################################################
#	Wraps a string if needed
####################################################################################################
def WrapStr(myStr):
	LineWrap = int(Prefs['Line_Length'])
	if Prefs['Line_Wrap']:		
		return fill(myStr, LineWrap)
	else:
		return myStr

####################################################################################################
# This function will return a string in hh:mm from a millisecond timestamp
####################################################################################################
def ConvertTimeStamp(timeStamp):
	seconds=str(int(timeStamp)/(1000)%60)
	if len(seconds)<2:
		seconds = '0' + seconds
	minutes=str((int(timeStamp)/(1000*60))%60)
	if len(minutes)<2:
		minutes = '0' + minutes
	hours=str((int(timeStamp)/(1000*60*60))%24)
	return hours + ':' + minutes + ':' + seconds

####################################################################################################
# This function will return a string in month, date, year format from a millisecond timestamp
####################################################################################################
def ConvertDateStamp(timeStamp):
	return Datetime.FromTimestamp(float(timeStamp)).strftime('%m/%d/%Y')


