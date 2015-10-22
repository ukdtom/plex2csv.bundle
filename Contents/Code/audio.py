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
	fieldnames = (
			'Track ID',
			'Artist', 
			'Album',
			'Title',
			)
	# Basic fields
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme2']):
		fieldnames = fieldnames + (
			'Rating Count',
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
def getAudioInfo(track, myRow,):
		# Get Simple Info
		myRow = getAudioSimple(track, myRow)
		# Get Basic Info
		if Prefs['Artist_Level'] in ['Basic', "Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getAudioBasic(track, myRow)
		if Prefs['Artist_Level'] in ["Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getAudioExtended(track, myRow)
		return myRow

####################################################################################################
# This function will return the simple info for Audio
####################################################################################################
def getAudioSimple(track, myRow):
	# Get episode rating key
	myRow['Track ID'] = misc.GetRegInfo(track, 'ratingKey', 'N/A')
	# Get Track title
	myRow['Title'] = misc.GetRegInfo(track, 'title')	
	# Get Artist
	myRow['Artist'] = misc.GetRegInfo(track, 'grandparentTitle')	
	# Get Album
	myRow['Album'] = misc.GetRegInfo(track, 'parentTitle')		
	return myRow

####################################################################################################
# This function will return the basic info for Audio
####################################################################################################
def getAudioBasic(track, myRow):
	myRow['Rating Count'] = misc.GetRegInfo(track, 'ratingCount', 'N/A')
	myRow['Track No'] = misc.GetRegInfo(track, 'index')
	myRow['Duration'] = misc.ConvertTimeStamp(misc.GetRegInfo(track, 'duration', '0'))
	myRow['Added'] = misc.ConvertDateStamp(misc.GetRegInfo(track, 'addedAt', '0'))
	myRow['Updated'] = misc.ConvertDateStamp(misc.GetRegInfo(track, 'updatedAt', '0'))
	return myRow

####################################################################################################
# This function will return the extended info for Audio
####################################################################################################
def getAudioExtended(track, myRow):
#TODO: Fix if more than one media for a track
	media = track.xpath('.//Media')[0]
	myRow['Media ID'] = media.get('id')
	myRow['bitrate'] = media.get('bitrate')
	myRow['audioChannels'] = media.get('audioChannels')
	myRow['audioCodec'] = media.get('audioCodec')
	myRow['container'] = media.get('container')

#	for media in track.xpath('.//Media'):
#		myRow['Media ID'] = media.get('id')
#		myRow['bitrate'] = media.get('bitrate')
#		myRow['audioChannels'] = media.get('audioChannels')
#		myRow['audioCodec'] = media.get('audioCodec')
#		myRow['container'] = media.get('container')
	return myRow

