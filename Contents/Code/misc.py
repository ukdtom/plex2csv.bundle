####################################################################################################
#	Helper file for dane22
# This one handles misc functions
#
# Increment version for all new functions and fixes
#
####################################################################################################

VERSION='0.0.0.3'

from textwrap import wrap, fill
import re
import datetime
import moviefields, audiofields, tvfields, photofields

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
#	Pull's a field from the xml
####################################################################################################
def GetRegInfo2(myMedia, myField, default = 'N/A'):
	returnVal = ''	
	try:
		fieldsplit = myField.rsplit('@', 1)
		# Single attribute lookup
		if fieldsplit[0] == '':
			try:
				if len(fieldsplit) == 2:
					returnVal = myMedia.get(fieldsplit[1])
					if returnVal == None:
						returnVal = default
					elif fieldsplit[1] in moviefields.dateTimeFields:
						returnVal = ConvertDateStamp(returnVal)
						if returnVal == '01/01/1970':
							returnVal = default
					elif fieldsplit[1] in moviefields.timeFields:
						returnVal = ConvertTimeStamp(returnVal)
						if returnVal == '01/01/1970':
							returnVal = default
					# IMDB or TheMovieDB?
					elif fieldsplit[1] == 'guid':
						linkID = returnVal[returnVal.index('://')+3:returnVal.index('?lang')]
						if 'com.plexapp.agents.imdb' in returnVal:
							sTmp = 'http://www.imdb.com/title/' + linkID
						elif 'com.plexapp.agents.themoviedb' in returnVal:
							sTmp = 'https://www.themoviedb.org/movie/' + linkID
						elif 'com.plexapp.agents.thetvdb' in returnVal:
							linkID = linkID[:returnVal.index('/')]
							sTmp = 'https://thetvdb.com/?tab=series&id=' + linkID[:linkID.index('/')]
						else:
							sTmp = 'N/A'
						#returnVal = sTmp
						return sTmp.encode('utf8')
			except:
				Log.Exception('Exception on field: ' + myField)
		else:
			# Attributes from xpath
			retVals = myMedia.xpath(fieldsplit[0][:-1])
			for retVal2 in retVals:
				try:
					# Get attribute
					retVal = retVal2.get(fieldsplit[1])
					# Did it exists?
					if retVal == None:
						retVal = default
					# Is it a dateStamp?
					elif fieldsplit[1] in moviefields.dateTimeFields:					
						retVal = ConvertDateStamp(retVal)
					# Got a timestamp?
					elif fieldsplit[1] in moviefields.timeFields:
						retVal = ConvertTimeStamp(retVal)
					# size conversion?
					elif fieldsplit[1] == 'size':
						retVal = (str(ConvertSize(retVal))+' GB')
					if returnVal == '':
						returnVal = retVal
					else:
						returnVal = returnVal + Prefs['Seperator'] + retVal
				except:
					Log.Exception('Exception happend in field: ' + myField)		
		return WrapStr(fixCRLF(returnVal)).encode('utf8')
	except:
		returnVal = default

####################################################################################################
#	Fix CR/LF
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

####################################################################################################
# This function will return fieldnames for a level
####################################################################################################
def getLevelFields(levelFields, fieldnames):
	fieldnamesList = list(fieldnames)
	for item in levelFields:
		fieldnamesList.append(str(item[0]))
	return fieldnamesList

####################################################################################################
# This function fetch the actual info for the element
####################################################################################################
def getItemInfo(et, myRow, fieldList):
	for item in fieldList:
		key = str(item[0])
		value = str(item[1])
		element = GetRegInfo2(et, value, 'N/A')
		if key in myRow:
			myRow[key] = myRow[key] + Prefs['Seperator'] + element
		else:
			myRow[key] = element
	return myRow

####################################################################################################
# This function will return the media path info for movies
####################################################################################################
def getMediaPath(myMedia, myRow):
	# Get tree info for media
	myMediaTreeInfoURL = 'http://127.0.0.1:32400/library/metadata/' + GetRegInfo(myMedia, 'ratingKey') + '/tree'
	TreeInfo = XML.ElementFromURL(myMediaTreeInfoURL).xpath('//MediaPart')
	for myPart in TreeInfo:
		MediaHash = GetRegInfo(myPart, 'hash')
		PMSMediaPath = os.path.join(Core.app_support_path, 'Media', 'localhost', MediaHash[0], MediaHash[1:]+ '.bundle', 'Contents')
		myRow['PMS Media Path'] = PMSMediaPath.encode('utf8')
	return myRow

####################################################################################################
# This function converts Byte to Gigabyte
####################################################################################################
def ConvertSize(SizeAsString):
	ConvertedSize = round(float(SizeAsString)/(1024**3),2)
	return ConvertedSize
