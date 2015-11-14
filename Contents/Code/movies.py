####################################################################################################
#	Helper file for Plex2CSV
# This one handles movies
####################################################################################################

import misc, moviefields

####################################################################################################
# This function will return the header for the CSV file for movies
####################################################################################################
def getMovieHeader(PrefsLevel):
	fieldnames = ()	

	print 'GED 1223: ', PrefsLevel

	if PrefsLevel.startswith('Special Level'):
		if PrefsLevel == 'Special Level 1':
			fieldnames = getLevelFields(moviefields.SLevel_1, fieldnames)
			print 'GED: Special Level 1'
			return fieldnames
		if PrefsLevel == 'Special Level 2':
			fieldnames = getLevelFields(moviefields.SLevel_2, fieldnames)
			print 'GED: Special Level 2'
			return fieldnames
		if PrefsLevel == 'Special Level 3':
			fieldnames = getLevelFields(moviefields.SLevel_3, fieldnames)
			print 'GED: Special Level 3'
			return fieldnames
		if PrefsLevel == 'Special Level 4':
			fieldnames = getLevelFields(moviefields.SLevel_4, fieldnames)
			print 'GED: Special Level 4'
			return fieldnames
		if PrefsLevel == 'Special Level 666':
			fieldnames = getLevelFields(moviefields.SLevel_666, fieldnames)
			print 'GED: Special Level 666'
			return fieldnames
	# Level 1 fields
	fieldnames = getLevelFields(moviefields.Level_1, fieldnames)		
	# Basic fields
	if PrefsLevel in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = getLevelFields(moviefields.Level_2, fieldnames)		
	# Extended fields
	if PrefsLevel in ['Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = getLevelFields(moviefields.Level_3, fieldnames)		
	# Extreme fields
	if PrefsLevel in ['Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = getLevelFields(moviefields.Level_4, fieldnames)
	# Extreme 2 (Part) level
	if PrefsLevel in ['Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = getLevelFields(moviefields.Level_5, fieldnames)			
	# Extreme 3 level
	if PrefsLevel in ['Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = getLevelFields(moviefields.Level_6, fieldnames)
	# Above All level
	if PrefsLevel in ['Level 666']:			
		fieldnames = getLevelFields(moviefields.Level_666, fieldnames)
	return fieldnames

####################################################################################################
# This function will return fieldnames for a level
####################################################################################################
def getLevelFields(levelFields, fieldnames):
	fieldnamesList = list(fieldnames)
	for item in levelFields:
		fieldnamesList.append(str(item[0]))
	return fieldnamesList

####################################################################################################
# This function will return the info for movies
####################################################################################################
def getMovieInfo(myMedia, myRow, csvwriter):
	prefsLevel = Prefs['Movie_Level']
	if prefsLevel == 'Special Level 1':
		myRow = getItemInfo(myMedia, myRow, moviefields.SLevel_1)
		print 'GED FETCHING: Special Level 1'
		return myRow
	elif prefsLevel == 'Special Level 2':
		myRow = getItemInfo(myMedia, myRow, moviefields.SLevel_2)
		print 'GED FETCHING: Special Level 2'
		return myRow
	elif prefsLevel == 'Special Level 3':
		myRow = getItemInfo(myMedia, myRow, moviefields.SLevel_3)
		print 'GED FETCHING: Special Level 3'
		return myRow
	elif prefsLevel == 'Special Level 4':
		myRow = getItemInfo(myMedia, myRow, moviefields.SLevel_4)
		print 'GED FETCHING: Special Level 4'
		return myRow
	elif prefsLevel == 'Special Level 666':
		myRow = getItemInfo(myMedia, myRow, moviefields.SLevel_666)
		print 'GED FETCHING: Special Level 666'
		return myRow
	else:
		# Get Simple Info
		myRow = getItemInfo(myMedia, myRow, moviefields.Level_1)
		# Get Basic Info
		if prefsLevel in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = getItemInfo(myMedia, myRow, moviefields.Level_2)
		# Get Extended Info
		if prefsLevel in ['Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = getItemInfo(myMedia, myRow, moviefields.Level_3)
		# Get Extreme Info
		if prefsLevel in ['Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = getItemInfo(myMedia, myRow, moviefields.Level_4)
		# Get Extreme 2 Info
		if prefsLevel in ['Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = getItemInfo(myMedia, myRow, moviefields.Level_5)
		# Get Extreme 3 Info
		if prefsLevel in ['Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = getItemInfo(myMedia, myRow, moviefields.Level_6)
		# Get All of Above Info
		if prefsLevel in ['Level 666']:
			myRow = getAboveAll(myMedia, myRow)	
		return myRow

####################################################################################################
# This function will return the Above All info for movies
####################################################################################################
def getAboveAll(myMedia, myRow):
	# Get tree info for media
	myMediaTreeInfoURL = 'http://127.0.0.1:32400/library/metadata/' + misc.GetRegInfo(myMedia, 'ratingKey') + '/tree'
	TreeInfo = XML.ElementFromURL(myMediaTreeInfoURL).xpath('//MediaPart')
	for myPart in TreeInfo:
		MediaHash = misc.GetRegInfo(myPart, 'hash')
		PMSMediaPath = os.path.join(Core.app_support_path, 'Media', 'localhost', MediaHash[0], MediaHash[1:]+ '.bundle', 'Contents')
		myRow['PMS Media Path'] = PMSMediaPath.encode('utf8')
	return myRow

####################################################################################################
# This function fetch the actual info for movies
####################################################################################################
def getItemInfo(et, myRow, fieldList):
	for item in fieldList:
		key = str(item[0])
		value = str(item[1])
		element = misc.GetRegInfo2(et, value, 'N/A')
		if key in myRow:
			myRow[key] = myRow[key] + Prefs['Seperator'] + element
		else:
			myRow[key] = element
	return myRow

