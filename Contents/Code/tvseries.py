####################################################################################################
#	Helper file for Plex2CSV
# This one handles TV-Shows
####################################################################################################

import misc

####################################################################################################
# This function will return the header for the CSV file for TV-Shows
####################################################################################################
def getTVHeader(PrefsLevel):
	# Simple fields
	fieldnames = ('Id', 
			'Series Title',
			'Episode Title',
			'Episode Sort Title',
			'Year',
			'Season',
			'Episode',
			'Content Rating',
			'Summary',
			'Rating',			
			)
	# Basic fields
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme 2']):
		fieldnames = fieldnames + (
			'View Count',
			'Last Viewed at',
			'Studio',
			'Originally Aired',
			'Authors',
			'Genres',
			'Directors',
			'Roles',
			'Labels',
			'Duration',
			'Added',
			'Updated'			
			)
	# Extended fields
	if PrefsLevel in ['Extended','Extreme', 'Extreme 2']:
		fieldnames = fieldnames + (
			'Media Id',
			'Video Resolution',
			'Media Duration',
			'Bit Rate',
			'Width',
			'Height',
			'Aspect Ratio',
			'Audio Channels',
			'Audio Codec',
			'Video Codec',
			'Container',
			'Video FrameRate',
			'Locked fields',
			'Extras',
			'Audio Languages',
			'Subtitle Languages'
			)
	# Extreme fields
	if PrefsLevel in ['Extreme', 'Extreme 2']:
		fieldnames = fieldnames + (			
			'Part Duration',
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Container'			
			)
	# Extreme 2 fields
	if PrefsLevel in ['Extreme 2']:
		fieldnames = fieldnames + (			
			'PMS Media Path',
			''
			)
	return fieldnames

####################################################################################################
# This function will return the info for TV-Shows
####################################################################################################
def ExportTVShows(Episode, myRow, MYHEADER, TVShows):
	# Get Simple Info
	myRow = getTVSimple(Episode, myRow)
	# Get Basic Info
	if Prefs['TV_Level'] in ["Basic","Extended", "Extreme", "Extreme 2"]:
		myRow = getTVBasic(Episode, myRow, TVShows)
	# Extended or above?
	if Prefs['TV_Level'] in ['Extended','Extreme', 'Extreme 2']:	
		myExtendedInfoURL = 'http://127.0.0.1:32400/library/metadata/' + Episode.get('ratingKey')
		EpisodeMedia = XML.ElementFromURL(myExtendedInfoURL, headers=MYHEADER).xpath('//Video')
		# Get Extended info
		myRow = getTVExtended(Episode, myRow, EpisodeMedia)
	# Gather Extreme info here		
	if Prefs['TV_Level'] in ["Extreme", "Extreme 2"]:
		# Get Extreme info
		myRow = getTVExtreme(Episode, myRow, EpisodeMedia)
	if Prefs['TV_Level'] in ['Extreme 2']:
		myExtendedInfoURL  = 'http://127.0.0.1:32400/library/metadata/' + Episode.get('ratingKey') + '/tree'
		Extreme2Level = XML.ElementFromURL(myExtendedInfoURL, headers=MYHEADER).xpath('//MediaPart')
		# Get Extreme info
		myRow = getTVExtreme2(Extreme2Level, myRow)
	return myRow

####################################################################################################
# This function will return the Extreme info for TV-Shows
####################################################################################################
def getTVExtreme2(Extreme2Level, myRow):
	for myPart in Extreme2Level:
		MediaHash = misc.GetRegInfo(myPart, 'hash')
		PMSMediaPath = os.path.join(Core.app_support_path, 'Media', 'localhost', MediaHash[0], MediaHash[1:]+ '.bundle', 'Contents')
		myRow['PMS Media Path'] = misc.WrapStr(PMSMediaPath.encode('utf8'))
	return myRow

####################################################################################################
# This function will return the Extreme info for TV-Shows
####################################################################################################
def getTVExtreme(Episode, myRow, EpisodeMedias):	
	for Media in EpisodeMedias:
		parts = Media.xpath('//Part')
		# TODO: Check for more parts, and then do a NewLine
		for part in parts:
			# File Name of this Part
			myRow['Part File'] = misc.GetMoviePartInfo(part, 'file', 'N/A')
			# File size of this part
			myRow['Part Size'] = misc.GetMoviePartInfo(part, 'size', 'N/A')
			# Is This part Indexed
			myRow['Part Indexed'] = misc.GetMoviePartInfo(part, 'indexes', 'N/A')
			# Part Container
			myRow['Part Container'] = misc.GetMoviePartInfo(part, 'container', 'N/A')
			# Part Duration
			partDuration = misc.ConvertTimeStamp(misc.GetMoviePartInfo(part, 'duration', '0'))
			myRow['Part Duration'] = partDuration.encode('utf8')	
	return myRow

####################################################################################################
# This function will return the Extended info for TV-Shows
####################################################################################################
def getTVExtended(Episode, myRow, EpisodeMedias):
	# VideoResolution
	myRow['Video Resolution'] = misc.GetExtInfo(Episode, 'videoResolution', 'N/A')
	# id
	myRow['Media Id'] = misc.GetExtInfo(Episode, 'id', 'N/A')
	# Duration
	Mediaduration = misc.ConvertTimeStamp(misc.GetExtInfo(Episode, 'duration', '0'))
	myRow['Media Duration'] = Mediaduration.encode('utf8')
	# Bitrate
	myRow['Bit Rate'] = misc.GetExtInfo(Episode, 'bitrate', 'N/A')
	# Width
	myRow['Width'] = misc.GetExtInfo(Episode, 'width', 'N/A')
	# Height
	myRow['Height'] = misc.GetExtInfo(Episode, 'height', 'N/A')
	# AspectRatio
	myRow['Aspect Ratio'] = misc.GetExtInfo(Episode, 'aspectRatio', 'N/A')
	# AudioChannels
	myRow['Audio Channels'] = misc.GetExtInfo(Episode, 'audioChannels', 'N/A')
	# AudioCodec
	myRow['Audio Codec'] = misc.GetExtInfo(Episode, 'audioCodec', 'N/A')
	# VideoCodec
	myRow['Video Codec'] = misc.GetExtInfo(Episode, 'videoCodec', 'N/A')
	# Container
	myRow['Container'] = misc.GetExtInfo(Episode, 'container', 'N/A')
	# VideoFrameRate
	myRow['Video FrameRate'] = misc.GetExtInfo(Episode, 'videoFrameRate', 'N/A')
	for EpisodeMedia in EpisodeMedias:
		myRow['Locked fields'] = misc.GetArrayAsString(EpisodeMedia, 'Field/@name', default = '')
		# Got extras?
		myRow['Extras'] = misc.GetArrayAsString(EpisodeMedia, 'Extras/@size', default = 'N/A')
		#Get Audio languages
		AudioStreamsLanguages = EpisodeMedia.xpath('//Stream[@streamType=2][@languageCode]')
		AudioLanguages = ''
		for langCode in AudioStreamsLanguages:
			if AudioLanguages == '':
				AudioLanguages = misc.GetMoviePartInfo(langCode, 'languageCode', 'N/A')
			else:
				AudioLanguages = AudioLanguages + Prefs['Seperator'] + misc.GetMoviePartInfo(langCode, 'languageCode', 'N/A')
		myRow['Audio Languages'] = AudioLanguages
		#Get Subtitle languages
		SubtitleStreamsLanguages = EpisodeMedia.xpath('//Stream[@streamType=3][@languageCode]')
		SubtitleLanguages = ''
		for langCode in SubtitleStreamsLanguages:
			if SubtitleLanguages == '':
				SubtitleLanguages = misc.GetMoviePartInfo(langCode, 'languageCode', 'N/A')
			else:
				SubtitleLanguages = SubtitleLanguages + Prefs['Seperator'] + misc.GetMoviePartInfo(langCode, 'languageCode', 'N/A')
		myRow['Subtitle Languages'] = SubtitleLanguages				
	return myRow

####################################################################################################
# This function will return the Basic info for TV-Shows
####################################################################################################
#def getTVBasic(Episode, myRow, myMedia, TVShow):
def getTVBasic(Episode, myRow, TVShow):
	# Get Watched count
	myRow['View Count'] = misc.GetRegInfo(Episode, 'viewCount')
	# Get last watched timestamp
	lastViewedAt = misc.ConvertDateStamp(misc.GetRegInfo(Episode, 'lastViewedAt', '0'))
	if lastViewedAt == '01/01/1970':
		myRow['Last Viewed at'] = 'N/A'
	else:
		myRow['Last Viewed at'] = lastViewedAt.encode('utf8')
	# Get Studio
	myRow['Studio'] = misc.GetRegInfo(Episode, 'studio')
	# Get Originally Aired
	myRow['Originally Aired'] = misc.GetRegInfo(Episode, 'originallyAvailableAt')
	# Get the Writers
	Writer = Episode.xpath('Writer/@tag')
	if not Writer:
		Writer = ['']
	Author = ''
	for myWriter in Writer:
		if Author == '':
			Author = myWriter
		else:
			Author = Author + Prefs['Seperator'] + myWriter
	Author = misc.WrapStr(Author)
	myRow['Authors'] = Author.encode('utf8')
	# Get Genres
	Genres = TVShow.xpath('Genre/@tag')
	if not Genres:
		Genres = ['']
	Genre = ''
	for myGenre in Genres:
		if Genre == '':
			Genre = myGenre
		else:
			Genre = Genre + Prefs['Seperator'] + myGenre
	Genre = misc.WrapStr(Genre)
	myRow['Genres'] = Genre.encode('utf8')
	# Get the Directors
	Directors = Episode.xpath('Director/@tag')
	if not Directors:
		Directors = ['']
	Director = ''
	for myDirector in Directors:
		if Director == '':
			Director = myDirector
		else:
			Director = Director + Prefs['Seperator'] + myDirector
	Director = misc.WrapStr(Director)
	myRow['Directors'] = Director.encode('utf8')
	# Get Roles
	Roles = TVShow.xpath('Role/@tag')
	if not Roles:
		Roles = ['']
	Role = ''
	for myRole in Roles:
		if Role == '':
			Role = myRole
		else:
			Role = Role + Prefs['Seperator'] + myRole
	Role = misc.WrapStr(Role)
	myRow['Roles'] = Role.encode('utf8')
	# Get labels
	Labels = Episode.xpath('Label/@tag')
	if not Labels:
		Labels = ['']
	Label = ''
	for myLabel in Labels:
		if Label == '':
			Label = myLabel
		else:
			Label = Label + Prefs['Seperator'] + myLabel
	Label = misc.WrapStr(Label)
	myRow['Labels'] = Label.encode('utf8')
	# Get the duration of the episode
	duration = misc.ConvertTimeStamp(misc.GetRegInfo(Episode, 'duration', '0'))
	myRow['Duration'] = duration.encode('utf8')
	# Get Added at
	addedAt = misc.ConvertDateStamp(misc.GetRegInfo(Episode, 'addedAt', '0'))
	myRow['Added'] = addedAt.encode('utf8')
	# Get Updated at
	updatedAt = misc.ConvertDateStamp(misc.GetRegInfo(Episode, 'updatedAt', '0'))
	myRow['Updated'] = updatedAt.encode('utf8')
	return myRow

####################################################################################################
# This function will return the simple info for TV-Shows
####################################################################################################
def getTVSimple(Episode, myRow):
	# Get episode rating key
	myRow['Id'] = misc.GetRegInfo(Episode, 'ratingKey')
	# Get Serie Title
	myRow['Series Title'] = misc.GetRegInfo(Episode, 'grandparentTitle')
	# Get Episode sort Title
	myRow['Episode Sort Title'] = misc.GetRegInfo(Episode, 'titleSort')
	# Get Episode title
	myRow['Episode Title'] = misc.GetRegInfo(Episode, 'title')
	# Get Year
	myRow['Year'] = misc.GetRegInfo(Episode, 'year')
	# Get Season number
	myRow['Season'] = misc.GetRegInfo(Episode, 'parentIndex')
	# Get Episode number
	myRow['Episode'] = misc.GetRegInfo(Episode, 'index')
	# Get Content Rating
	myRow['Content Rating'] = misc.GetRegInfo(Episode, 'contentRating')
	# Get summary
	myRow['Summary'] = misc.GetRegInfo(Episode, 'summary')
	# Get Rating
	myRow['Rating'] = misc.GetRegInfo(Episode, 'rating')
	return myRow

