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
def getTVInfo(Episode, myRow, MYHEADER, csvwriter, EpisodeMedia):
		# Get Simple Info
		myRow = getTVSimple(Episode, myRow)

		print 'GED TV 1'

		# Get Basic Info
		if Prefs['TV_Level'] in ["Basic","Extended", "Extreme", "Extreme 2"]:
			myRow = getTVBasic(Episode, myRow, EpisodeMedia)

		print 'GED TV 2'

		# Gather som futher info here		
		if Prefs['TV_Level'] in ["Extended", "Extreme", "Extreme 2"]:

			print 'GED TV 3'

			print 'GED ', EpisodeMedia

			# Get Extended info
			myRow = getTVExtended(Episode, myRow, EpisodeMedia)

		return myRow

####################################################################################################
# This function will return the Extended info for TV-Shows
####################################################################################################
def getTVExtended(Episode, myRow, EpisodeMedia):

	# VideoResolution
	myRow['Video Resolution'] = misc.GetMoviePartInfo(EpisodeMedia, 'videoResolution', 'N/A')
	# id
	myRow['Media Id'] = misc.GetMoviePartInfo(Episode, 'id', 'N/A')
	# Duration
	Mediaduration = misc.ConvertTimeStamp(misc.GetRegInfo(EpisodeMedia, 'duration', '0'))
	myRow['Media Duration'] = Mediaduration.encode('utf8')
	# Bitrate
	myRow['Bit Rate'] = misc.GetMoviePartInfo(EpisodeMedia, 'bitrate', 'N/A')



	print 'GED3 ', misc.GetMoviePartInfo(Episode, 'id', 'N/A')




	return myRow


####################################################################################################
# This function will return the Basic info for TV-Shows
####################################################################################################
def getTVBasic(myMedia2, myRow, myMedia):
	# Get Watched count
	myRow['View Count'] = misc.GetRegInfo(myMedia2, 'viewCount')
	# Get last watched timestamp
	lastViewedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia2, 'lastViewedAt', '0'))
	if lastViewedAt == '01/01/1970':
		myRow['Last Viewed at'] = 'N/A'
	else:
		myRow['Last Viewed at'] = lastViewedAt.encode('utf8')
	# Get Studio
	myRow['Studio'] = misc.GetRegInfo(myMedia2, 'studio')
	# Get Originally Aired
	myRow['Originally Aired'] = misc.GetRegInfo(myMedia2, 'originallyAvailableAt')
	# Get the Writers
	Writer = myMedia2.xpath('Writer/@tag')
	if not Writer:
		Writer = ['']
	Author = ''
	for myWriter in Writer:
		if Author == '':
			Author = myWriter
		else:
			Author = Author + ' - ' + myWriter
	Author = misc.WrapStr(Author)
	myRow['Authors'] = Author.encode('utf8')
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
	# Get the Directors
	Directors = myMedia2.xpath('Director/@tag')
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
	# Get labels
	Labels = myMedia2.xpath('Label/@tag')
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
	duration = misc.ConvertTimeStamp(misc.GetRegInfo(myMedia2, 'duration', '0'))
	myRow['Duration'] = duration.encode('utf8')
	# Get Added at
	addedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia2, 'addedAt', '0'))
	myRow['Added'] = addedAt.encode('utf8')
	# Get Updated at
	updatedAt = misc.ConvertDateStamp(misc.GetRegInfo(myMedia2, 'updatedAt', '0'))
	myRow['Updated'] = updatedAt.encode('utf8')
	return myRow

####################################################################################################
# This function will return the simple info for TV-Shows
####################################################################################################
def getTVSimple(myMedia2, myRow):
	# Get episode rating key
	myRow['Id'] = misc.GetRegInfo(myMedia2, 'ratingKey')
	# Get Serie Title
	myRow['Series Title'] = misc.GetRegInfo(myMedia2, 'grandparentTitle')
	# Get Episode sort Title
	myRow['Episode Sort Title'] = misc.GetRegInfo(myMedia2, 'titleSort')
	# Get Episode title
	myRow['Episode Title'] = misc.GetRegInfo(myMedia2, 'title')
	# Get Year
	myRow['Year'] = misc.GetRegInfo(myMedia2, 'year')
	# Get Season number
	myRow['Season'] = misc.GetRegInfo(myMedia2, 'parentIndex')
	# Get Episode number
	myRow['Episode'] = misc.GetRegInfo(myMedia2, 'index')
	# Get Content Rating
	myRow['Content Rating'] = misc.GetRegInfo(myMedia2, 'contentRating')
	# Get summary
	myRow['Summary'] = misc.GetRegInfo(myMedia2, 'summary')
	# Get Rating
	myRow['Rating'] = misc.GetRegInfo(myMedia2, 'rating')
	return myRow







