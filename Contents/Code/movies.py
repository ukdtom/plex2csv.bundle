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
	# Simple fields
	fieldnames = getLevelFields(moviefields.simpleFields, fieldnames)		
	# Basic fields
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4', 'Extreme 5', 'Extreme 6', 'Above All']):
		fieldnames = getLevelFields(moviefields.basicFields, fieldnames)		
	# Extended fields
	if PrefsLevel in ['Extended','Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4', 'Extreme 5', 'Extreme 6', 'Above All']:
		fieldnames = getLevelFields(moviefields.extendedFields, fieldnames)		
	# Extreme fields
	if PrefsLevel in ['Extreme', 'Extreme 2', 'Extreme 3', 'Extreme 4', 'Extreme 5', 'Extreme 6', 'Above All']:
		fieldnames = getLevelFields(moviefields.extremeFields, fieldnames)
	# Extreme 2 (Part) level
	if PrefsLevel in ['Extreme 2', 'Extreme 3', 'Extreme 4', 'Extreme 5', 'Extreme 6', 'Above All']:
		fieldnames = getLevelFields(moviefields.extreme2Fields, fieldnames)			
	# Extreme 3 level
	if PrefsLevel in ['Extreme 3', 'Extreme 4', 'Extreme 5', 'Extreme 6', 'Above All']:			
		fieldnames = getLevelFields(moviefields.extreme3Fields, fieldnames)
	# Above All level
	if PrefsLevel in ['Above All']:			
		fieldnames = getLevelFields(moviefields.aboveAllFields, fieldnames)
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
def getMovieInfo(myMedia, myRow, MYHEADER, csvwriter):
		# Get Extended info if needed
		if Prefs['Movie_Level'] not in ['Simple']:				
			myExtendedInfoURL = misc.GetLoopBack() + '/library/metadata/' + misc.GetRegInfo(myMedia, 'ratingKey') + '?includeExtras=1'
			ExtInfo = XML.ElementFromURL(myExtendedInfoURL).xpath('//Video')[0]
		# Get Simple Info
		myRow = getItemInfo(myMedia, myRow, moviefields.simpleFields)
		# Get Basic Info
		if Prefs['Movie_Level'] in ['Basic', "Extended", "Extreme", "Extreme 2", "Extreme 3", "Extreme 4", "Extreme 5", "Extreme 6", "Above All"]:
			myRow = getItemInfo(ExtInfo, myRow, moviefields.basicFields)
		# Get Extended Info
		if Prefs['Movie_Level'] in ["Extended", "Extreme", "Extreme 2", "Extreme 3", "Extreme 4", "Extreme 5", "Extreme 6", "Above All"]:
			myRow = getItemInfo(ExtInfo, myRow, moviefields.extendedFields)
		# Get Extreme Info
		if Prefs['Movie_Level'] in ["Extreme", "Extreme 2", "Extreme 3", "Extreme 4", "Extreme 5", "Extreme 6", "Above All"]:
			myRow = getItemInfo(myMedia, myRow, moviefields.extremeFields)
		# Get Extreme 2 Info
		if Prefs['Movie_Level'] in ["Extreme 2", "Extreme 3", "Extreme 4", "Extreme 5", "Extreme 6", "Above All"]:
			myRow = getItemInfo(myMedia, myRow, moviefields.extreme2Fields)
		# Get Extreme 3 Info
		if Prefs['Movie_Level'] in ["Extreme 3", "Extreme 4", "Extreme 5", "Extreme 6", "Above All"]:
			myRow = getItemInfo(ExtInfo, myRow, moviefields.extreme3Fields)
		# Get All of Above Info
		if Prefs['Movie_Level'] in ["Above All"]:
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

