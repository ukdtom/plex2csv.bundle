####################################################################################################
#	Helper file for dane22
# This one handles misc functions
#
# Increment version for all new functions and fixes
#
####################################################################################################

VERSION='0.0.0.1'

from textwrap import wrap, fill
import re
import datetime

####################################################################################################
# This function will return the version of the misc module
####################################################################################################
def getVersion():
	return VERSION

####################################################################################################
# This function will return a valid token from plex.tv
####################################################################################################
def getToken():
	userName = Prefs['Plex_User']
	userPwd = Prefs['Plex_Pwd']
	myUrl = 'https://plex.tv/users/sign_in.json'
	# Create the authentication string
	base64string = String.Base64Encode('%s:%s' % (userName, userPwd))
	# Create the header
	MYAUTHHEADER= {}
	MYAUTHHEADER['X-Plex-Product'] = consts.DESCRIPTION
	MYAUTHHEADER['X-Plex-Client-Identifier'] = consts.APPGUID
	MYAUTHHEADER['X-Plex-Version'] = consts.VERSION
	MYAUTHHEADER['Authorization'] = 'Basic ' + base64string
	MYAUTHHEADER['X-Plex-Device-Name'] = consts.NAME
	# Send the request
	try:
		httpResponse = HTTP.Request(myUrl, headers=MYAUTHHEADER, method='POST')
		myToken = JSON.ObjectFromString(httpResponse.content)['user']['authentication_token']
		Log.Debug('Response from plex.tv was : %s' %(httpResponse.headers["status"]))
	except:
		Log.Critical('Exception happend when trying to get a token from plex.tv')
		Log.Critical('Returned answer was %s' %httpResponse.content)
		Log.Critical('Status was: %s' %httpResponse.headers)
		return ''			
	return myToken

####################################################################################################
# This function will return the loopback address
####################################################################################################
def GetLoopBack():

	# For now, simply return the IPV4 LB Addy, until PMS is better with this
	return 'http://127.0.0.1:32400'
	
	try:
		httpResponse = HTTP.Request('http://[::1]:32400/web', immediate=True, timeout=5)
		return 'http://[::1]:32400'
	except:
		print 'Got IP v4'
		return 'http://127.0.0.1:32400'

####################################################################################################
# This function will return info from an array, defined in an xpath
####################################################################################################
def GetArrayAsString(Media, Field, default = ''):
	Fields = Media.xpath(Field)
	if not Fields:
		Fields = ['']
	Field = ''
	for myField in Fields:
		if Field == '':
			Field = myField
		else:
			Field = Field + Prefs['Seperator'] + myField
	Field = WrapStr(Field)
	return Field.encode('utf8')

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
#		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
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
#		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
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
#		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
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


