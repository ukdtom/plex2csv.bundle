####################################################################################################
#	Helper file for Plex2CSV
# This one handles movies
####################################################################################################

import misc


####################################################################################################
# This function will return the header for the CSV file for movies
####################################################################################################
def getMovieHeader(PrefsLevel):
	# Simple fields
	fieldnames = ('Media ID', 
			'Title',
			'Sort title',
			'Studio',
			'Content Rating',
			'Summary',
			'Rating',
			'Year',
			'Genres'
			)
	# Basic fields
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme 2', 'Extreme 3']):
		fieldnames = fieldnames + (
			'View Count',
			'Last Viewed at',
			'Tagline',
			'Release Date',
			'Writers',
			'Directors',
			'Roles',
			'Duration',
			'Locked Fields',
			'Extras',
			'Labels',
			'IMDB Id',
			'Country'
			)
	# Extended fields
	if PrefsLevel in ['Extended','Extreme', 'Extreme 2', 'Extreme 3']:
		fieldnames = fieldnames + (
			'Original Title',
			'Collections',
			'Added',
			'Updated',
			'Audio Languages',
			'Subtitle Languages'
			)
	# Extreme fields
	if PrefsLevel in ['Extreme', 'Extreme 2', 'Extreme 3']:
		fieldnames = fieldnames + (
			'Video Resolution',
			'Bitrate',
			'Width',
			'Height',
			'Aspect Ratio',
			'Audio Channels',
			'Audio Codec',
			'Video Codec',
			'Container',
			'Video FrameRate'
			)
	# Part info
	if PrefsLevel in ['Extreme 2', 'Extreme 3']:			
		fieldnames = fieldnames + (
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Duration',
			'Part Container'
			)
	# Extreme 3 level
	if PrefsLevel in ['Extreme 3']:			
		fieldnames = fieldnames + (
			'PMS Media Path',
			''
			)
	return fieldnames

####################################################################################################
# This function will return the info for movies
####################################################################################################
def getMovieInfo(myMedia, myRow, MYHEADER, csvwriter):
		# Get Extended info if needed
		if Prefs['Movie_Level'] not in ['Simple']:				
			myExtendedInfoURL = 'http://127.0.0.1:32400/library/metadata/' + misc.GetRegInfo(myMedia, 'ratingKey') + '?includeExtras=1'
			ExtInfo = XML.ElementFromURL(myExtendedInfoURL, headers=MYHEADER).xpath('//Video')[0]
		# Get Simple Info
		myRow = getMovieSimple(myMedia, myRow)
		# Get Basic Info
		if Prefs['Movie_Level'] in ['Basic', "Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getMovieBasic(myMedia, myRow, ExtInfo)
		# Get Extended Info
		if Prefs['Movie_Level'] in ["Extended", "Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getMovieExtended(myMedia, myRow, ExtInfo)	
		# Get Extreme Info
		if Prefs['Movie_Level'] in ["Extreme", "Extreme 2", "Extreme 3"]:
			myRow = getMovieExtreme(myMedia, myRow, ExtInfo)	
		# Get Extreme 2 Info
		if Prefs['Movie_Level'] in ["Extreme 2", "Extreme 3"]:
			myRow = getMovieExtreme2(myMedia, myRow, ExtInfo)	
		# Get Extreme 2 Info
		if Prefs['Movie_Level'] in ["Extreme 3"]:
			myRow = getMovieExtreme3(myMedia, myRow, ExtInfo, MYHEADER)	
		return myRow

####################################################################################################
# This function will return the extreme 2 info for movies
####################################################################################################
def getMovieExtreme3(myMedia, myRow, ExtInfo, MYHEADER):

	# Get tree info for media
	myMediaTreeInfoURL = 'http://127.0.0.1:32400/library/metadata/' + misc.GetRegInfo(myMedia, 'ratingKey') + '/tree'
	TreeInfo = XML.ElementFromURL(myMediaTreeInfoURL, headers=MYHEADER).xpath('//MediaPart')
	for myPart in TreeInfo:
		MediaHash = misc.GetRegInfo(myPart, 'hash')
		PMSMediaPath = os.path.join(Core.app_support_path, 'Media', 'localhost', MediaHash[0], MediaHash[1:]+ '.bundle', 'Contents')
		myRow['PMS Media Path'] = PMSMediaPath.encode('utf8')
	return myRow

####################################################################################################
# This function will return the extreme 2 info for movies
####################################################################################################
def getMovieExtreme2(myMedia, myRow, ExtInfo):
	Videos = ExtInfo.xpath('//Video')
	if not Videos:
		Videos = ['']
	for Video in Videos:
		if not Video.get('extraType'):
			realVideo = Video.xpath('//Part')
			# File size of this part
			myRow['Part Size'] = misc.GetRegInfo(realVideo[0], 'size', 'N/A')			
			# File Name of this Part
			myRow['Part File'] = misc.GetRegInfo(realVideo[0], 'file', 'N/A')
			# Is This part Indexed
			myRow['Part Indexed'] = misc.GetRegInfo(realVideo[0], 'indexes', 'N/A')
			# Part Container
			myRow['Part Container'] = misc.GetRegInfo(realVideo[0], 'container', 'N/A')
			# Part Duration
			partDuration = misc.ConvertTimeStamp(misc.GetRegInfo(realVideo[0], 'duration', '0'))
			myRow['Part Duration'] = partDuration.encode('utf8')
	return myRow

####################################################################################################
# This function will return the extreme info for movies
####################################################################################################
def getMovieExtreme(myMedia, myRow, ExtInfo):
	# Get Video Resolution
	myRow['Video Resolution'] = misc.GetExtInfo(ExtInfo, 'videoResolution')
	# Get Bitrate
	myRow['Bitrate'] = misc.GetExtInfo(ExtInfo, 'bitrate')
	# Get Width
	myRow['Width'] = misc.GetExtInfo(ExtInfo, 'width')
	# Get Height
	myRow['Height'] = misc.GetExtInfo(ExtInfo, 'height')
	# Get Aspect Ratio
	myRow['Aspect Ratio'] = misc.GetExtInfo(ExtInfo, 'aspectRatio')
	# Get Audio Channels
	myRow['Audio Channels'] = misc.GetExtInfo(ExtInfo, 'audioChannels')
	# Get Audio Codec
	myRow['Audio Codec'] = misc.GetExtInfo(ExtInfo, 'audioCodec')
	# Get Video Codec
	myRow['Video Codec'] = misc.GetExtInfo(ExtInfo, 'videoCodec')
	# Get Container
	myRow['Container'] = misc.GetExtInfo(ExtInfo, 'container')
	# Get Video FrameRate
	myRow['Video FrameRate'] = misc.GetExtInfo(ExtInfo, 'videoFrameRate')
	return myRow

####################################################################################################
# This function will return the extended info for movies
####################################################################################################
def getMovieExtended(myMedia, myRow, ExtInfo):
	# Get Genres							
	Genres = ExtInfo.xpath('Genre/@tag')
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
	# Get Roles Extended
	myRoles = ExtInfo.xpath('//Role')
	Role = ''
	if myRoles:
		for myRole in myRoles:
			myActor = myRole.get('tag')
			myActorRole = myRole.get('role')
			if myActor:
				# Found an Actor
				if myActorRole:
					if Role == '':
						Role = 'Actor: ' + myActor + ' as: ' + myActorRole
					else:
						Role = Role + Prefs['Seperator'] + 'Actor: ' + myActor + ' as: ' + myActorRole
				else:
					if Role == '':
						Role = 'Actor: ' + myActor
					else:
						Role = Role + Prefs['Seperator'] + 'Actor: ' + myActor
	Role = misc.WrapStr(Role)
	myRow['Roles'] = Role.encode('utf8')
	# Get Collections
	Collections = ExtInfo.xpath('Collection/@tag')
	if not Collections:
		Collections = ['']
	Collection = ''
	for myCollection in Collections:
		if Collection == '':
			Collection = myCollection
		else:
			Collection = Collection + Prefs['Seperator'] + myCollection
	Collection = misc.WrapStr(Collection)
	myRow['Collections'] = Collection.encode('utf8')
	# Get the original title
	myRow['Original Title'] = misc.GetRegInfo(myMedia, 'originalTitle')
	# Get Added at
	addedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia, 'addedAt', '0'))
	myRow['Added'] = addedAt.encode('utf8')
	# Get Updated at
	updatedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia, 'updatedAt', '0'))
	myRow['Updated'] = updatedAt.encode('utf8')
	#Get Audio languages
	AudioLanguages = ''
	AudioStreamsLanguages = ExtInfo.xpath('Media/Part/Stream[@streamType=2][@languageCode]')
	for langCode in AudioStreamsLanguages:
		if AudioLanguages == '':
			AudioLanguages = misc.GetRegInfo(langCode, 'languageCode', 'N/A')
		else:
			AudioLanguages = AudioLanguages + Prefs['Seperator'] + misc.GetRegInfo(langCode, 'languageCode', 'N/A')
	myRow['Audio Languages'] = AudioLanguages
	#Get Subtitle languages
	SubtitleLanguages = ''
	SubtitleStreamsLanguages = ExtInfo.xpath('Media/Part/Stream[@streamType=3][@languageCode]')
	for langCode in SubtitleStreamsLanguages:
		if SubtitleLanguages == '':
			SubtitleLanguages = misc.GetRegInfo(langCode, 'languageCode', 'N/A')
		else:
			SubtitleLanguages = SubtitleLanguages + Prefs['Seperator'] + misc.GetRegInfo(langCode, 'languageCode', 'N/A')
	myRow['Subtitle Languages'] = misc.WrapStr(SubtitleLanguages)
	return myRow

####################################################################################################
# This function will return the basic info for movies
####################################################################################################
def getMovieBasic(myMedia, myRow, ExtInfo):
	# Get View Count
	myRow['View Count'] = misc.GetRegInfo(myMedia, 'viewCount')
	# Get last watched timestamp
	lastViewedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia, 'lastViewedAt', '0'))
	if lastViewedAt == '01/01/1970':
		myRow['Last Viewed at'] = 'N/A'
	else:
		myRow['Last Viewed at'] = lastViewedAt.encode('utf8')
	# Get the Tag Line
	myRow['Tagline'] = misc.GetRegInfo(myMedia, 'tagline')
	# Get the Release Date
	myRow['Release Date'] = misc.GetRegInfo(myMedia, 'originallyAvailableAt')
	# Get the Writers
	Writer = myMedia.xpath('Writer/@tag')
	if not Writer:
		Writer = ['']
	Author = ''
	for myWriter in Writer:
		if Author == '':
			Author = myWriter
		else:
			Author = Author + Prefs['Seperator'] + myWriter
	Author = misc.WrapStr(Author)
	myRow['Writers'] = Author.encode('utf8')
	# Get the Country
	Countries = myMedia.xpath('Country/@tag')
	if not Countries:
		Countries = ['N/A']
	Country = ''
	for myCountry in Countries:
		if Country == '':
			Country = myCountry
		else:
			Country = Country + Prefs['Seperator'] + myCountry
	Country = misc.WrapStr(Country)
	myRow['Country'] = Country.encode('utf8')
	# Get the duration of the movie
	duration = misc.ConvertTimeStamp(misc.GetRegInfo(myMedia, 'duration', '0'))
	myRow['Duration'] = duration.encode('utf8')
	# Get the Directors
	Directors = myMedia.xpath('Director/@tag')
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
	# Get the labels
	Labels = ExtInfo.xpath('Label/@tag')
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
	# Get Locked fields
	Fields = ExtInfo.xpath('Field/@name')
	if not Fields:
		Fields = ['']
	Field = ''
	for myField in Fields:
		if Field == '':
			Field = myField
		else:
			Field = Field + Prefs['Seperator'] + myField
	Field = misc.WrapStr(Field)
	myRow['Locked Fields'] = Field.encode('utf8')
	# Got extras?
	Extras = ExtInfo.xpath('//Extras/@size')
	if not Extras:
		Extra = '0'
	else:
		for myExtra in Extras:
			Extra = myExtra								
	Extra = misc.WrapStr(Extra)
	myRow['Extras'] = Extra.encode('utf8')
	# Only if basic, and not others
	if Prefs['Movie_Level'] in ['Basic']:
		# Get Roles Basic
		Roles = myMedia.xpath('Role/@tag')
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
	#Get IMDB ID
	IMDBId = ExtInfo.get('guid')
	# Avoid printing the guid, if this is a home movie section
	if 'com.plexapp.agents.imdb' in IMDBId:
		IMDBId = IMDBId[26:]
		if IMDBId != '':
			IMDBIds = IMDBId.split('?')
			myRow['IMDB Id'] = IMDBIds[0]
		else:
			myRow['IMDB Id'] = 'N/A'
	else:
		myRow['IMDB Id'] = 'N/A'	
	return myRow

####################################################################################################
# This function will return the simple info for movies
####################################################################################################
def getMovieSimple(myMedia, myRow):
	# Get Media ID
	myRow['Media ID'] = misc.GetRegInfo(myMedia, 'ratingKey')
	# Get title
	myRow['Title'] = misc.GetRegInfo(myMedia, 'title')
	# Get Sorted title
	myRow['Sort title'] = misc.GetRegInfo(myMedia, 'titleSort')
	# Get Studio
	myRow['Studio'] = misc.GetRegInfo(myMedia, 'studio')
	# Get contentRating
	myRow['Content Rating'] = misc.GetRegInfo(myMedia, 'contentRating')
	# Get Year
	myRow['Year'] = misc.GetRegInfo(myMedia, 'year')
	# Get Rating
	myRow['Rating'] = misc.GetRegInfo(myMedia, 'rating')
	# Get Summary
	myRow['Summary'] = misc.GetRegInfo(myMedia, 'summary')
	# Get Genres							
	Genres = myMedia.xpath('Genre/@tag')
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
	return myRow

