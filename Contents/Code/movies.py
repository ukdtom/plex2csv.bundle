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
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4']):
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
	if PrefsLevel in ['Extended','Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4']:
		fieldnames = fieldnames + (
			'Original Title',
			'Collections',
			'Added',
			'Updated',
			'Audio Languages',
			'Audio Title',
			'Subtitle Languages',
			'Subtitle Title',
			'Subtitle Codec'
			)
	# Extreme fields
	if PrefsLevel in ['Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4']:
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
	if PrefsLevel in ['Extreme 2', 'Extreme 3', 'Extreme 4']:			
		fieldnames = fieldnames + (
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Duration',
			'Part Container'
			)
	# Extreme 3 level
	if PrefsLevel in ['Extreme 3', 'Extreme 4']:			
		fieldnames = fieldnames + (
			'PMS Media Path',
			''
			)
	# Extreme 4 level
	if PrefsLevel in ['Extreme 4']:			
		fieldnames = fieldnames + (
			'Video Stream Codec',
			'Video Stream bitrate',
			'Video Stream language',
			'Video Stream language Code',
			'Video Stream anamorphic',
			'Video Stream bitDepth',
			'Video Stream cabac',
			'Video Stream chromaSubsampling',
			'Video Stream codecID',
			'Video Stream frameRate',
			'Video Stream frameRateMode',
			'Video Stream hasScalingMatrix',
			'Video Stream height',
			'Video Stream pixelAspectRatio',
			'Video Stream pixelFormat',
			'Video Stream profile',
			'Video Stream refFrames',
			'Video Stream scanType',
			'Video Stream streamIdentifier',
			'Video Stream width'
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
		if Prefs['Movie_Level'] in ['Basic', "Extended", "Extreme", "Extreme 2", "Extreme 3", "Extreme 4"]:
			myRow = getMovieBasic(myMedia, myRow, ExtInfo)
		# Get Extended Info
		if Prefs['Movie_Level'] in ["Extended", "Extreme", "Extreme 2", "Extreme 3", "Extreme 4"]:
			myRow = getMovieExtended(myMedia, myRow, ExtInfo)	
		# Get Extreme Info
		if Prefs['Movie_Level'] in ["Extreme", "Extreme 2", "Extreme 3", "Extreme 4"]:
			myRow = getMovieExtreme(myMedia, myRow, ExtInfo)	
		# Get Extreme 2 Info
		if Prefs['Movie_Level'] in ["Extreme 2", "Extreme 3", "Extreme 4"]:
			myRow = getMovieExtreme2(myMedia, myRow, ExtInfo)	
		# Get Extreme 3 Info
		if Prefs['Movie_Level'] in ["Extreme 3", "Extreme 4"]:
			myRow = getMovieExtreme3(myMedia, myRow, ExtInfo)	
		# Get Extreme 4 Info
		if Prefs['Movie_Level'] in ["Extreme 4"]:
			myRow = getMovieExtreme4(myMedia, myRow, ExtInfo)	
		return myRow

####################################################################################################
# This function will return the extreme 4 info for movies
####################################################################################################
def getMovieExtreme4(myMedia, myRow, ExtInfo):


	#Get Video Streams Info
	#Video Stream Codec
	vSCodec = ''
	#Video Stream bitrate	
	vSBitRate = ''
	#Video Stream language
	vSLanguage = ''
	#Video Stream language Code
	vSLanguageCode = ''
	#Video Stream anamorphic
	vSAnamorphic = ''
	#Video Stream bitDepth
	vSBitDepth = ''
	#Video Stream cabac
	vSCabac = ''
	#Video Stream chromaSubsampling
	vSChromaSubsampling = ''
	#Video Stream codecID
	vSCodecID = ''
	#Video Stream frameRate
	vSFrameRate = ''
	#Video Stream frameRateMode
	vSFrameRateMode = ''
	#Video Stream hasScalingMatrix
	vSHasScalingMatrix = ''
	#Video Stream height
	vSHeight = ''
	#Video Stream pixelAspectRatio
	vSPixelAspectRatio = ''
	#Video Stream pixelFormat
	vSPixelFormat = ''
	#Video Stream profile
	vSProfile = ''
	#Video Stream refFrames
	vSRefFrames = ''
	#Video Stream scanType
	vSScanType = ''
	#Video Stream streamIdentifier
	vSStreamIdentifier = ''
	#Video Stream width
	vSWidth = ''
	# Walk the info, and grap the details
	vStreams = ExtInfo.xpath('Media/Part/Stream[@streamType=1]')
	for vStream in vStreams:
		thisvSCodec = misc.GetRegInfo(vStream, 'codec', 'N/A')
		if vSCodec == '':
				vSCodec = thisvSCodec
		else:
			vSCodec = vSCodec + Prefs['Seperator'] + thisvSCodec
		thisvSBitRate = misc.GetRegInfo(vStream, 'bitrate', 'N/A')
		if vSBitRate == '':
				vSBitRate = thisvSBitRate
		else:
			vSBitRate = vSBitRate + Prefs['Seperator'] + thisvSBitRate
		thisvSLanguage = misc.GetRegInfo(vStream, 'language', 'N/A')
		if vSLanguage == '':
				vSLanguage = thisvSLanguage
		else:
			vSLanguage = vSLanguage + Prefs['Seperator'] + thisvSLanguage
		thisvSLanguageCode = misc.GetRegInfo(vStream, 'languageCode', 'N/A')
		if vSLanguageCode == '':
				vSLanguageCode = thisvSLanguageCode
		else:
			vSLanguageCode = vSLanguageCode + Prefs['Seperator'] + thisvSLanguageCode
		thisvSAnamorphic = misc.GetRegInfo(vStream, 'anamorphic', 'N/A')
		if vSAnamorphic == '':
				vSAnamorphic = thisvSAnamorphic
		else:
			vSAnamorphic = vSAnamorphic + Prefs['Seperator'] + thisvSAnamorphic
		thisvSBitDepth = misc.GetRegInfo(vStream, 'bitDepth', 'N/A')
		if vSBitDepth == '':
				vSBitDepth = thisvSBitDepth
		else:
			vSBitDepth = vSBitDepth + Prefs['Seperator'] + thisvSBitDepth
		thisvSCabac = misc.GetRegInfo(vStream, 'cabac', 'N/A')
		if vSCabac == '':
				vSCabac = thisvSCabac
		else:
			vSCabac = vSCabac + Prefs['Seperator'] + thisvSCabac
		thisvSChromaSubsampling = misc.GetRegInfo(vStream, 'chromaSubsampling', 'N/A')
		if vSChromaSubsampling == '':
				vSChromaSubsampling = thisvSChromaSubsampling
		else:
			vSChromaSubsampling = vSChromaSubsampling + Prefs['Seperator'] + thisvSChromaSubsampling
		thisvSCodecID = misc.GetRegInfo(vStream, 'codecID', 'N/A')
		if vSCodecID == '':
				vSCodecID = thisvSCodecID
		else:
			vSCodecID = vSCodecID + Prefs['Seperator'] + thisvSCodecID
		thisvSFrameRate = misc.GetRegInfo(vStream, 'frameRate', 'N/A')
		if vSFrameRate == '':
				vSFrameRate = thisvSFrameRate
		else:
			vSFrameRate = vSFrameRate + Prefs['Seperator'] + thisvSFrameRate
		thisvSFrameRateMode = misc.GetRegInfo(vStream, 'frameRateMode', 'N/A')
		if vSFrameRateMode == '':
				vSFrameRateMode = thisvSFrameRateMode
		else:
			vSFrameRateMode = vSFrameRateMode + Prefs['Seperator'] + thisvSFrameRateMode
		thisvSHasScalingMatrix = misc.GetRegInfo(vStream, 'hasScalingMatrix', 'N/A')
		if vSHasScalingMatrix == '':
				vSHasScalingMatrix = thisvSHasScalingMatrix
		else:
			vSHasScalingMatrix = vSHasScalingMatrix + Prefs['Seperator'] + thisvSHasScalingMatrix
		thisvSHeight = misc.GetRegInfo(vStream, 'height', 'N/A')
		if vSHeight == '':
				vSHeight = thisvSHeight
		else:
			vSHeight = vSHeight + Prefs['Seperator'] + thisvSHeight
		thisvSPixelAspectRatio = misc.GetRegInfo(vStream, 'height', 'N/A')
		if vSPixelAspectRatio == '':
				vSPixelAspectRatio = thisvSPixelAspectRatio
		else:
			vSPixelAspectRatio = vSPixelAspectRatio + Prefs['Seperator'] + thisvSPixelAspectRatio
		thisvSPixelFormat = misc.GetRegInfo(vStream, 'pixelFormat', 'N/A')
		if vSPixelFormat == '':
				vSPixelFormat = thisvSPixelFormat
		else:
			vSPixelFormat = vSPixelFormat + Prefs['Seperator'] + thisvSPixelFormat
		thisvSProfile = misc.GetRegInfo(vStream, 'profile', 'N/A')
		if vSProfile == '':
				vSProfile = thisvSProfile
		else:
			vSProfile = vSProfile + Prefs['Seperator'] + thisvSProfile
		thisvSRefFrames = misc.GetRegInfo(vStream, 'refFrames', 'N/A')
		if vSRefFrames == '':
				vSRefFrames = thisvSRefFrames
		else:
			vSRefFrames = vSRefFrames + Prefs['Seperator'] + thisvSRefFrames
		thisvSScanType = misc.GetRegInfo(vStream, 'scanType', 'N/A')
		if vSScanType == '':
				vSScanType = thisvSScanType
		else:
			vSScanType = vSScanType + Prefs['Seperator'] + thisvSScanType
		thisvSStreamIdentifier = misc.GetRegInfo(vStream, 'streamIdentifier', 'N/A')
		if vSStreamIdentifier == '':
				vSStreamIdentifier = thisvSStreamIdentifier
		else:
			vSStreamIdentifier = vSStreamIdentifier + Prefs['Seperator'] + thisvSStreamIdentifier
		thisvSWidth = misc.GetRegInfo(vStream, 'width', 'N/A')
		if vSWidth == '':
				vSWidth = thisvSWidth
		else:
			vSWidth = vSWidth + Prefs['Seperator'] + thisvSWidth
	# save Video stream info
	myRow['Video Stream Codec'] = vSCodec
	myRow['Video Stream bitrate'] = vSBitRate
	myRow['Video Stream language'] = vSLanguage
	myRow['Video Stream language Code'] = vSLanguageCode
	myRow['Video Stream anamorphic'] = vSAnamorphic
	myRow['Video Stream bitDepth'] = vSBitDepth
	myRow['Video Stream cabac'] = vSCabac
	myRow['Video Stream chromaSubsampling'] = vSChromaSubsampling
	myRow['Video Stream codecID'] = vSCodecID
	myRow['Video Stream frameRate'] = vSFrameRate
	myRow['Video Stream frameRateMode'] = vSFrameRateMode
	myRow['Video Stream hasScalingMatrix'] = vSHasScalingMatrix
	myRow['Video Stream height'] = vSHeight
	myRow['Video Stream pixelAspectRatio'] = vSPixelAspectRatio
	myRow['Video Stream pixelFormat'] = vSPixelFormat
	myRow['Video Stream profile'] = vSProfile
	myRow['Video Stream refFrames'] = vSRefFrames
	myRow['Video Stream scanType'] = vSScanType
	myRow['Video Stream streamIdentifier'] = vSStreamIdentifier
	myRow['Video Stream width'] = vSWidth
	return myRow

####################################################################################################
# This function will return the extreme 3 info for movies
####################################################################################################
def getMovieExtreme3(myMedia, myRow, ExtInfo):

	# Get tree info for media
	myMediaTreeInfoURL = 'http://127.0.0.1:32400/library/metadata/' + misc.GetRegInfo(myMedia, 'ratingKey') + '/tree'
	TreeInfo = XML.ElementFromURL(myMediaTreeInfoURL).xpath('//MediaPart')
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
		thisAudioLanguage = misc.GetMoviePartInfo(langCode, 'languageCode', 'none')
		if thisAudioLanguage == 'zxx':
			thisAudioLanguage = 'non-linguistic content'
		if AudioLanguages == '':
			AudioLanguages = thisAudioLanguage
		else:
			AudioLanguages = AudioLanguages + Prefs['Seperator'] + thisAudioLanguage
	myRow['Audio Languages'] = AudioLanguages
	#Get Audio title
	AudioTitles = ''
	AudioStreamsTitles = ExtInfo.xpath('Media/Part/Stream[@streamType=2]')
	for title in AudioStreamsTitles:
		thisAudioTitle = misc.GetRegInfo(title, 'title', 'none')
		if AudioTitles == '':
				AudioTitles = thisAudioTitle
		else:
			AudioTitles = AudioTitles + Prefs['Seperator'] + thisAudioTitle
	myRow['Audio Title'] = misc.WrapStr(AudioTitles)
	#Get Subtitle languages
	SubtitleLanguages = ''
	SubtitleStreams = ExtInfo.xpath('Media/Part/Stream[@streamType=3]')
	for subStream in SubtitleStreams:
		thisLangCode = misc.GetRegInfo(subStream, 'languageCode', 'none')
		if 'N/A' == misc.GetRegInfo(subStream, 'key', 'N/A'):
			thisLangCode = thisLangCode + '(Internal)'
		if SubtitleLanguages == '':
				SubtitleLanguages = thisLangCode
		else:
			SubtitleLanguages = SubtitleLanguages + Prefs['Seperator'] + thisLangCode
	myRow['Subtitle Languages'] = misc.WrapStr(SubtitleLanguages)
	# Get Subtitle title
	SubtitleTitles = ''
	for subStream in SubtitleStreams:
		thisSubTitle = misc.GetRegInfo(subStream, 'title', 'none')
		if SubtitleTitles == '':
				SubtitleTitles = thisSubTitle
		else:
			SubtitleTitles = SubtitleTitles + Prefs['Seperator'] + thisSubTitle
	myRow['Subtitle Title'] = misc.WrapStr(SubtitleTitles)
	#Get Subtitle Codec
	SubtitleCodec = ''
	SubtitleStreamsCodec = ExtInfo.xpath('Media/Part/Stream[@streamType=3][@codec]')
	for subtitleFormat in SubtitleStreamsCodec:
		if SubtitleCodec == '':
			SubtitleCodec = misc.GetRegInfo(subtitleFormat, 'codec', 'N/A')
		else:
			SubtitleCodec = SubtitleCodec + Prefs['Seperator'] + misc.GetRegInfo(subtitleFormat, 'codec', 'N/A')
	myRow['Subtitle Codec'] = misc.WrapStr(SubtitleCodec)
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

