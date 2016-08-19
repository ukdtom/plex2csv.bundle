####################################################################################################
#	Helper file for Plex2CSV
# This one handles TV-Shows
####################################################################################################

import misc, tvfields, consts

STACKEDLABELS = ['cd', 'disc', 'disk', 'dvd', 'part', 'pt']

####################################################################################################
# This function will return the header for the CSV file for TV-Shows
####################################################################################################
def getTVHeader(PrefsLevel):
	fieldnames = ()
	# Show only stuff
	if PrefsLevel.startswith('Show Only'):
		fieldnames = misc.getLevelFields(tvfields.Show_1, fieldnames)
		if PrefsLevel == 'Show Only 2':
			fieldnames = misc.getLevelFields(tvfields.Show_2, fieldnames)
		return fieldnames
	# Special stuff
	if PrefsLevel.startswith('Special Level'):
		if PrefsLevel == 'Special Level 1':
			fieldnames = misc.getLevelFields(tvfields.SLevel_1, fieldnames)
		if PrefsLevel == 'Special Level 2':
			fieldnames = misc.getLevelFields(tvfields.SLevel_2, fieldnames)
		if PrefsLevel == 'Special Level 3':
			fieldnames = misc.getLevelFields(tvfields.SLevel_3, fieldnames)
		if PrefsLevel == 'Special Level 4':
			fieldnames = misc.getLevelFields(tvfields.SLevel_4, fieldnames)
		if PrefsLevel == 'Special Level 666':
			fieldnames = misc.getLevelFields(tvfields.SLevel_666, fieldnames)
		if PrefsLevel == 'Special Level 666-2':
			fieldnames = misc.getLevelFields(tvfields.SLevel_666, fieldnames)
		# Do we need the PMS path?
		if '666' in PrefsLevel:
			fieldnames.append('PMS Media Path')
		return fieldnames
	# Level 1 fields
	fieldnames = misc.getLevelFields(tvfields.Level_1, fieldnames)		
	# Basic fields
	if PrefsLevel in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = misc.getLevelFields(tvfields.Level_2, fieldnames)		
	# Extended fields
	if PrefsLevel in ['Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = misc.getLevelFields(tvfields.Level_3, fieldnames)		
	# Extreme fields
	if PrefsLevel in ['Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = misc.getLevelFields(tvfields.Level_4, fieldnames)
	# Extreme 2 (Part) level
	if PrefsLevel in ['Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = misc.getLevelFields(tvfields.Level_5, fieldnames)			
	# Extreme 3 level
	if PrefsLevel in ['Level 6', 'Level 7', 'Level 8', 'Level 666']:
		fieldnames = misc.getLevelFields(tvfields.Level_6, fieldnames)
	# PMS Path also needs to be exported
	if '666' in PrefsLevel:
		fieldnames.append('PMS Media Path')
	return fieldnames


####################################################################################################
# This function will return the info for tv-shows
####################################################################################################
def getTvInfo(myMedia, myRow):
	prefsLevel = Prefs['TV_Level']
	if prefsLevel in ['Show Only 1', 'Show Only 2']:
		myRow = misc.getItemInfo(myMedia, myRow, tvfields.Show_1)
		if prefsLevel == 'Show Only 2':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Show_2)
		return myRow		
	elif 'Special' in prefsLevel:
		if prefsLevel == 'Special Level 1':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.SLevel_1)
		elif prefsLevel == 'Special Level 2':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.SLevel_2)
		elif prefsLevel == 'Special Level 3':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.SLevel_3)
		elif prefsLevel == 'Special Level 4':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.SLevel_4)
		elif prefsLevel == 'Special Level 666':
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.SLevel_666)
		if '666' in prefsLevel:
			myRow = misc.getMediaPath(myMedia, myRow)			
		return myRow
	else:
		# Get Simple Info
		myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_1)
		# Get Basic Info
		if prefsLevel in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_2)
		# Get Extended Info
		if prefsLevel in ['Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_3)
		# Get Extreme Info
		if prefsLevel in ['Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_4)
		# Get Extreme 2 Info
		if prefsLevel in ['Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_5)
		# Get Extreme 3 Info
		if prefsLevel in ['Level 6', 'Level 7', 'Level 8', 'Level 666']:
			myRow = misc.getItemInfo(myMedia, myRow, tvfields.Level_6)
		# Get Media Path as well
		if '666' in prefsLevel:
			myRow = misc.getMediaPath(myMedia, myRow)	
		return myRow

''' Export TV Show info only '''
def getShowOnly(myMedia, myRow, level):
	prefsLevel = Prefs['TV_Level']
	for key, value in tvfields.Show_1:
		element = myMedia.get(value[1:])
		if element == None:
			element = 'N/A'
		element = misc.WrapStr(misc.fixCRLF(element).encode('utf8'))
		if key in myRow:
			myRow[key] = myRow[key] + Prefs['Seperator'] + element
		else:
			myRow[key] = element
	# Now we sadly needs to make a call for each show :-(
	if '2' in prefsLevel:
		myExtendedInfoURL = misc.GetLoopBack() + '/library/metadata/' + myMedia.get('ratingKey')
		for key, value in tvfields.Show_2:
			if key == 'MetaDB Link':
				myRow[key] = misc.metaDBLink(XML.ElementFromURL(myExtendedInfoURL, timeout=float(consts.PMSTIMEOUT))[0].xpath('@guid')[0])

	return myRow

