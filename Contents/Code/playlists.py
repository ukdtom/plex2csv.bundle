####################################################################################################
#	Helper file for Plex2CSV
# This one handles playlists
####################################################################################################

import misc


####################################################################################################
# This function will return the header for the CSV file for playlists
####################################################################################################
def getPlayListHeader(listtype, level):
	if listtype == 'video':
		# Video list Simple
		fieldnames = ('Media ID',
				'Type', 
				'TV-Show',
				'Title',				
				'Rating',
				'Summary',
				'Year'
				)
	elif listtype == 'audio':
		# Audio list Simple
		fieldnames = ('Media ID',
				'Type', 
				'Artist',
				'Album',
				'Title',				
				'Summary',
				'Year'
				)	
	return fieldnames

####################################################################################################
# This function will export and return the info for the Playlist
####################################################################################################
def getPlayListInfo(playListItem, myRow, playListType):
	# Get Simple Info
	if playListType == 'video':
		myRow = getPlayListSimpleVideo(playListItem, myRow)
	elif playListType == 'audio':
		myRow = getPlayListSimpleAudio(playListItem, myRow)
	return myRow

####################################################################################################
# This function will export and return the simple info for the Playlist for video types
####################################################################################################
def getPlayListSimpleVideo(playListItem, myRow):
	# Get the media ID
	myRow['Media ID'] = misc.GetRegInfo(playListItem, 'ratingKey')	
	# Get media type
	myRow['Type'] = misc.GetRegInfo(playListItem, 'type')	
	# Get media title
	myRow['Title'] = misc.GetRegInfo(playListItem, 'title')
	# Get TV-Show name
	myRow['TV-Show'] = misc.GetRegInfo(playListItem, 'grandparentTitle', 'N/A')
	# Get Rating
	myRow['Rating'] = misc.GetRegInfo(playListItem, 'rating', 'N/A')
	# Get Summary
	myRow['Summary'] = misc.GetRegInfo(playListItem, 'summary', 'N/A')
	# Get year
	myRow['Year'] = misc.GetRegInfo(playListItem, 'year', 'N/A')
	return myRow


####################################################################################################
# This function will export and return the simple info for the Playlist for audio types
####################################################################################################
def getPlayListSimpleAudio(playListItem, myRow):
	# Get the media ID
	myRow['Media ID'] = misc.GetRegInfo(playListItem, 'ratingKey')	
	# Get media type
	myRow['Type'] = misc.GetRegInfo(playListItem, 'type')	
	# Get media title
	myRow['Title'] = misc.GetRegInfo(playListItem, 'title')
	# Get Artist name
	myRow['Artist'] = misc.GetRegInfo(playListItem, 'grandparentTitle', 'N/A')
	# Get Album name
	myRow['Album'] = misc.GetRegInfo(playListItem, 'parentTitle', 'N/A')
	# Get Summary
	myRow['Summary'] = misc.GetRegInfo(playListItem, 'summary', 'N/A')
	# Get year
	myRow['Year'] = misc.GetRegInfo(playListItem, 'year', 'N/A')
	return myRow


