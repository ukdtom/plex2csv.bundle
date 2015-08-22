####################################################################################################
#	Helper file for Plex2CSV
# This one handles Audio
####################################################################################################

import misc

####################################################################################################
# This function will return the header for the CSV file for Audio
####################################################################################################
def getMusicHeader(PrefsLevel):
	# Simple fields
	fieldnames = ('Track ID',
			'Artist', 
			'Album',
			'Title',
			)
	# Basic fields
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme2']):
		fieldnames = fieldnames + (
			'Artist Summery',
			'Track No',
			'Duration',
			'Added',
			'Updated',
			)
	# Extended fields
	if (PrefsLevel in ['Extended','Extreme', 'Extreme2']):
		fieldnames = fieldnames + (
			'Media ID',
			'bitrate',
			'audioChannels',
			'audioCodec',
			'container',
			)
	return fieldnames

####################################################################################################
# This function will return the info for Audio
####################################################################################################
def getAudioInfo(myMedia, myRow, MYHEADER, csvwriter, myMedia2):
		# Get Simple Info
		myRow = getAudioSimple(myMedia, myRow, myMedia2)
		# Get Basic Info
		if Prefs['Artist_Level'] in ['Basic', "Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getAudioBasic(myMedia, myRow, myMedia2)
		if Prefs['Artist_Level'] in ["Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getAudioExtended(myMedia, myRow, myMedia2)
		return myRow

####################################################################################################
# This function will return the extended info for Audio
####################################################################################################
def getAudioExtended(myMedia, myRow, myMedia2):
	for track in myMedia2.xpath('//Track'):
		if track.get('ratingKey') == myRow['Track ID']:
			myRow['Media ID'] = track.get('ratingKey')
			for Media in track.xpath('//Media'):
				myRow['bitrate'] = Media.get('bitrate')
				myRow['audioChannels'] = Media.get('audioChannels')
				myRow['audioCodec'] = Media.get('audioCodec')
				myRow['container'] = Media.get('container')
	return myRow

####################################################################################################
# This function will return the simple info for Audio
####################################################################################################
def getAudioSimple(myMedia, myRow, myMedia2):
	# Get episode rating key
	myRow['Track ID'] = misc.GetRegInfo(myMedia2, 'ratingKey')
	# Get Track title
	myRow['Title'] = misc.GetRegInfo(myMedia2, 'title')	
	# Get Artist
	myRow['Artist'] = misc.GetRegInfo(myMedia, 'title')	
	# Get Album
	myRow['Album'] = misc.GetRegInfo(myMedia2, 'parentTitle')		
	return myRow

####################################################################################################
# This function will return the basic info for Audio
####################################################################################################
def getAudioBasic(myMedia, myRow, myMedia2):
	myRow['Artist Summery'] = misc.GetRegInfo(myMedia, 'summary')
	myRow['Track No'] = misc.GetRegInfo(myMedia2, 'index')
	myRow['Duration'] = misc.ConvertTimeStamp(misc.GetRegInfo(myMedia2, 'duration', '0'))
	myRow['Added'] = misc.ConvertDateStamp(misc.GetRegInfo(myMedia2, 'addedAt', '0'))
	myRow['Updated'] = misc.ConvertDateStamp(misc.GetRegInfo(myMedia2, 'updatedAt', '0'))
	return myRow

