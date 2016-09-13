####################################################################################################
#	This plugin will create a list of medias in a section of Plex as a csv file
#
#	Made by 
#	dane22....A Plex Community member
#	srazer....A Plex Community member
# CCarpo....A Plex Community member
#
####################################################################################################

# To find Work in progress, search this file for the word ToDo in all the modules
#TODO: Poster view for first menu

import os
import time
import io
import csv
import re
import movies, tvseries, audio, photo
import consts, misc, playlists
import moviefields, audiofields, tvfields, photofields

# Threading stuff
bScanStatus = 0				# Current status of the background scan
initialTimeOut = 12		# When starting a scan, how long in seconds to wait before displaying a status page. Needs to be at least 1.
sectiontype = ''			# Type of section been exported
bScanStatusCount = 0	# Number of item currently been investigated

EXPORTPATH = ''				# Path to export file

####################################################################################################
# Start function
####################################################################################################
def Start():
	global DEBUGMODE
	# Switch to debug mode if needed
	debugFile = Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name, consts.NAME + '.bundle', 'debug')
	DEBUGMODE = os.path.isfile(debugFile)
	if DEBUGMODE:
		VERSION = consts.VERSION + ' ****** WARNING Debug mode on *********'
		print("********  Started %s on %s  **********" %(consts.NAME  + ' ' + VERSION, Platform.OS))
	else:
		VERSION = consts.VERSION
	Log.Debug("*******  Started %s on %s  ***********" %(consts.NAME  + VERSION, Platform.OS))
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	ObjectContainer.art = R(consts.ART)
	ObjectContainer.title1 = consts.NAME  + consts.VERSION
	DirectoryObject.thumb = R(consts.ICON)
	HTTP.CacheTime = 0
	Log.Debug('Misc module is version: %s' %misc.getVersion())

####################################################################################################
# Main menu
####################################################################################################
@handler(consts.PREFIX, consts.NAME, thumb=consts.ICON, art=consts.ART)
@route(consts.PREFIX + '/MainMenu')
def MainMenu(random=0):
	Log.Debug("**********  Starting MainMenu  **********")
	global sectiontype
	ObjectContainer.art = R(consts.ART)
	ObjectContainer.title1 = consts.NAME  + consts.VERSION
	oc = ObjectContainer()
	oc.view_group = 'List'
	try:
		if ValidateExportPath():
			title = 'playlists'
			key = '-1'
			thumb = R(consts.PLAYLIST)
			sectiontype = title
			oc.add(DirectoryObject(key=Callback(selectPList), thumb=thumb, title='Export from "' + title + '"', summary='Export list from "' + title + '"'))
			Log.Debug('Getting section List from: ' + misc.GetLoopBack() + '/library/sections')
			sections = XML.ElementFromURL(misc.GetLoopBack() + '/library/sections', timeout=float(consts.PMSTIMEOUT)).xpath('//Directory')
			for section in sections:
				sectiontype = section.get('type')
				if sectiontype != "photook": # ToDo: Remove artist when code is in place for it.
					title = section.get('title')
					key = section.get('key')
					thumb = misc.GetLoopBack() + section.get('thumb')		
					Log.Debug('Title of section is %s with a key of %s' %(title, key))
					oc.add(DirectoryObject(key=Callback(backgroundScan, title=title, sectiontype=sectiontype, key=key, random=time.clock()), thumb=thumb, title='Export from "' + title + '"', summary='Export list from "' + title + '"'))
		else:
			oc.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Select Preferences to set the export path"))
	except:
		Log.Critical("Exception happened in MainMenu")
		raise
	oc.add(PrefsObject(title='Preferences', thumb=R(consts.ICON)))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc

####################################################################################################
# Validate Export Path
####################################################################################################
@route(consts.PREFIX + '/ValidateExportPath')
def ValidateExportPath():
	Log.Debug('Entering ValidateExportPath')
	if Prefs['Auto_Path']:
		return True
	# Let's check that the provided path is actually valid
	myPath = Prefs['Export_Path']
	Log.Debug('My master set the Export path to: %s' %(myPath))
	try:
		#Let's see if we can add out subdirectory below this
		if os.path.exists(myPath):
			Log.Debug('Master entered a path that already existed as: %s' %(myPath))
			if not os.path.exists(os.path.join(myPath, consts.NAME)):
				os.makedirs(os.path.join(myPath, consts.NAME))
				Log.Debug('Created directory named: %s' %(os.path.join(myPath, consts.NAME)))
				return True
			else:
				Log.Debug('Path verified as already present')
				return True
		else:
			raise Exception("Wrong path specified as export path")
			return False
	except:
		Log.Critical('Bad export path')
		return False

####################################################################################################
# Called by the framework every time a user changes the prefs
####################################################################################################
@route(consts.PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	return

####################################################################################################
# Export Complete.
####################################################################################################
@indirect
@route(consts.PREFIX + '/complete')
def complete(title=''):
	global bScanStatus
	Log.Debug("*******  All done, tell my Master  ***********")
	title = ('Export Completed for %s' %(title))
	message = 'Check the file: %s' %(EXPORTPATH) 
	oc2 = ObjectContainer(title1=title, no_cache=True, message=message)
	oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Go to the Main Menu"))
	# Reset the scanner status
	bScanStatus = 0
	Log.Debug("*******  Ending complete  ***********")
	return oc2

####################################################################################################
# Start the scanner in a background thread and provide status while running
####################################################################################################
@route(consts.PREFIX + '/backgroundScan')
def backgroundScan(title='', key='', sectiontype='', random=0, statusCheck=0):
	Log.Debug("******* Starting backgroundScan *********")
	# Current status of the Background Scanner:
	# 0=not running, 1=db, 2=complete
	# Errors: 91=unknown section type, 99=Other Error, 401= Authentication error
	global bScanStatus
	# Current status count (ex. "Show 2 of 31")
	global bScanStatusCount
	global bScanStatusCountOf
	try:
		if bScanStatus == 0 and not statusCheck:
			bScanStatusCount = 0
			bScanStatusCountOf = 0
			# Start scanner
			Thread.Create(backgroundScanThread, globalize=True, title=title, key=key, sectiontype=sectiontype)
			# Wait 10 seconds unless the scanner finishes
			x = 0
			while (x <= initialTimeOut):
				time.sleep(1)
				x += 1
				if bScanStatus == 2:
					Log.Debug("************** Scan Done, stopping wait **************")
					Log.Debug("*******  All done, tell my Master  ***********")
					title = ('Export Completed for %s' %(title))
					message = 'Check the file: %s' %(EXPORTPATH) 
					oc2 = ObjectContainer(title1=title, no_cache=True, message=message)
					oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Go to the Main Menu"))
					# Reset the scanner status
					bScanStatus = 0
					Log.Debug("*******  Ending complete  ***********")
					return oc2
					break
				if bScanStatus >= 90:
					Log.Debug("************** Error in thread, stopping wait **************")
					break
		# Sometimes a scanStatus check will happen when a scan is running. Usually from something weird in the web client. This prevents the scan from restarting
		elif bScanStatus == 0 and statusCheck:
			Log.Debug("backgroundScan statusCheck is set and no scan is running")
			oc2 = ObjectContainer(title1="Scan is not running.", no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Go to the Main Menu"))
			return oc2
			# Summary to add to the status
		summary = "The Plex Server will only wait a few seconds for us to work, so we run it in the background. This requires you to keep checking on the status until it is complete. \n\n"
		if bScanStatus == 1:
			# Scanning Database
			summary = summary + "The Database is being exported. \nExporting " + str(bScanStatusCount) + " of " + str(bScanStatusCountOf) + ". \nPlease wait a few seconds and check the status again."
			oc2 = ObjectContainer(title1="Exporting the Database " + str(bScanStatusCount) + " of " + str(bScanStatusCountOf) + ".", no_history=True)
			oc2.add(DirectoryObject(key=Callback(backgroundScan, random=time.clock(), statusCheck=1, title=title), title="Exporting the database. To update Status, click here.", summary=summary))
			oc2.add(DirectoryObject(key=Callback(backgroundScan, random=time.clock(), statusCheck=1, title=title), title="Exporting " + str(bScanStatusCount) + " of " + str(bScanStatusCountOf), summary=summary))
		elif bScanStatus == 2:
			# Show complete screen.
			oc2 = complete(title=title)
			return oc2
		elif bScanStatus == 91:
			# Unknown section type
			summary = "Unknown section type returned."
			oc2 = ObjectContainer(title1="Results", no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="*** Unknown section type. ***", summary=summary))
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="*** Please submit logs. ***", summary=summary))
			bScanStatus = 0
		elif bScanStatus == 99:
			# Error condition set by scanner
			summary = "An internal error has occurred. Please check the logs"
			oc2 = ObjectContainer(title1="Internal Error Detected. Please check the logs",no_history=True, view_group = 'List')
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="An internal error has occurred.", summary=summary))
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="*** Please submit logs. ***", summary=summary))
			consts.bScanStatus = 0
		elif consts.bScanStatus == 401:
			oc2 = ObjectContainer(title1="ERROR", no_history=True)
			# Error condition set by scanner
			summary = "When running in like Home mode, you must enable authentication in the preferences"
			oc2 = ObjectContainer(title1=summary,no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Authentication error.", summary=summary))			
			consts.bScanStatus = 0
		else:
			# Unknown status. Should not happen.
			summary = "Something went horribly wrong. The scanner returned an unknown status."
			oc2 = ObjectContainer(title1="Uh Oh!.", no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="*** Unknown status from scanner ***", summary=summary))
			bScanStatus = 0
	except:
		Log.Critical("Detected an exception in backgroundScan")
		raise
	Log.Debug("******* Ending backgroundScan ***********")
	return oc2

####################################################################################################
# Background scanner thread.
####################################################################################################
@route(consts.PREFIX + '/backgroundScanThread')
def backgroundScanThread(title, key, sectiontype):
	Log.Debug("*******  Starting backgroundScanThread  ***********")
	global bScanStatus
	global bScanStatusCount
	global bScanStatusCountOf	
	global EXPORTPATH
	try:
		bScanStatus = 1
		Log.Debug("Section type is %s" %(sectiontype))
		if sectiontype == 'playlists':
			myMediaURL = misc.GetLoopBack() + key
			playListType = title
			title = XML.ElementFromURL(myMediaURL, timeout=float(consts.PMSTIMEOUT)).get('title')
		else:
			myMediaURL = misc.GetLoopBack() + '/library/sections/' + key + "/all"
		Log.Debug("Path to medias in selection is %s" %(myMediaURL))
		# Get current date and time
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# Generate Output FileName
		if sectiontype == 'show':
			myLevel = Prefs['TV_Level']
		elif sectiontype == 'movie':
			myLevel = Prefs['Movie_Level']
		elif sectiontype == 'artist':
			myLevel = Prefs['Artist_Level']
		elif sectiontype == 'photo':
			myLevel = Prefs['Photo_Level']
		elif sectiontype == 'playlists':
			myLevel = Prefs['PlayList_Level']
		else:
			myLevel = ''
		# Remove invalid caracters, if on Windows......
		newtitle = re.sub('[\/[:#*?"<>|]', '_', title)
		if sectiontype == 'playlists':
			myCSVFile = os.path.join(Prefs['Export_Path'], consts.NAME, 'Playlist-' + newtitle + '-' + myLevel + '-' + timestr + '.csv')
		else:
			if Prefs['Auto_Path']:
				# Need to grap the first location for the section
				locations = XML.ElementFromURL('http://127.0.0.1:32400/library/sections/', timeout=float(consts.PMSTIMEOUT)).xpath('.//Directory[@key="' + key + '"]')[0]
				location = locations[0].get('path')
				myCSVFile = os.path.join(location, consts.NAME, newtitle + '-' + myLevel + '-' + timestr + '.csv')
				if not os.path.exists(os.path.join(location, consts.NAME)):
					os.makedirs(os.path.join(location, consts.NAME))
					Log.Debug('Auto Created directory named: %s' %(os.path.join(location, consts.NAME)))
				else:
					Log.Debug('Auto directory named: %s already exists' %(os.path.join(location, consts.NAME)))
			else:
				myCSVFile = os.path.join(Prefs['Export_Path'], consts.NAME, newtitle + '-' + myLevel + '-' + timestr + '.csv')
		EXPORTPATH = myCSVFile
		Log.Debug('Output file is named %s' %(myCSVFile))
		# Scan the database based on the type of section
		if sectiontype == "movie":
			scanMovieDB(myMediaURL, myCSVFile)
		elif sectiontype == "artist":
			scanArtistDB(myMediaURL, myCSVFile)
		elif sectiontype == "show":
			scanShowDB(myMediaURL, myCSVFile)
		elif sectiontype == "playlists":
			scanPList(myMediaURL, playListType, myCSVFile)
		elif sectiontype == "photo":
			scanPhotoDB(myMediaURL, myCSVFile)
		else:
			Log.Debug("Error: unknown section type: %s" %(sectiontype))
			bScanStatus = 91
		# Stop scanner on error
		if bScanStatus >= 90: return
		Log.Debug("*******  Ending backgroundScanThread  ***********")
		bScanStatus = 2
		return
	except:
		Log.Exception("Exception happened in backgroundScanThread")
		bScanStatus = 99
		raise
	Log.Debug("*******  Ending backgroundScanThread  ***********")


#*************************** IS THIS USED ANYMORE? TODO ******************
def getValues(tree, category):
    parent = tree.find(".//parent[@name='%s']" % category)
    return [child.get('value') for child in parent]

####################################################################################################
# This function will scan a movie section.
####################################################################################################
@route(consts.PREFIX + '/scanMovieDB')
def scanMovieDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanMovieDB with an URL of %s ***********" %(myMediaURL))
	Log.Debug('Movie Export level is %s' %(Prefs['Movie_Level']))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	bScanStatusCount = 0
	bScanStatusCountOf = 0	
	iCurrent = 0
	try:
		Log.Debug("About to open file %s" %(myCSVFile))
		csvfile = io.open(myCSVFile,'wb')
		# Create output file, and print the header
		csvwriter = csv.DictWriter(csvfile, fieldnames=movies.getMovieHeader(Prefs['Movie_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		Log.Debug("Writing header")
		csvwriter.writeheader()
		if Prefs['Movie_Level'] in moviefields.singleCall:
			bExtraInfo = False
		else:
			bExtraInfo = True	
		while True:
			Log.Debug("Walking medias")
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCurrent) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEMOVIES)	
			iCount = bScanStatusCount
			partMedias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
			if bScanStatusCount == 0:
				bScanStatusCountOf = partMedias.get('totalSize')
				Log.Debug('Amount of items in this section is %s' %bScanStatusCountOf)
			# HERE WE DO STUFF
			Log.Debug("Retrieved part of medias okay [%s of %s]" %(str(bScanStatusCount), str(bScanStatusCountOf)))
			medias = partMedias.xpath('.//Video')
			for media in medias:
				myRow = {}
				# Was extra info needed here?
				if bExtraInfo:
					myExtendedInfoURL = misc.GetLoopBack() + '/library/metadata/' + misc.GetRegInfo(media, 'ratingKey') + '?includeExtras=1&includeChapters=1'
					if Prefs['Check_Files']:				
						myExtendedInfoURL = myExtendedInfoURL + '&checkFiles=1&includeChapters=1'				
					media = XML.ElementFromURL(myExtendedInfoURL, timeout=float(consts.PMSTIMEOUT)).xpath('//Video')[0]
				# Export the info			
				myRow = movies.getMovieInfo(media, myRow, csvwriter)
				csvwriter.writerow(myRow)
				iCurrent += 1
				bScanStatusCount += 1
				Log.Debug("Media #%s from database: '%s'" %(str(iCurrent), misc.GetRegInfo(media, 'title')))
			# Got to the end of the line?		
			if int(partMedias.get('size')) == 0:
				break
		csvfile.close
	except ValueError, Argument:
		Log.Critical('Unknown error in scanMovieDb %s' %(Argument))
		bScanStatus = 99
		raise 
	Log.Debug("******* Ending scanMovieDB ***********")

####################################################################################################
# This function will scan a TV-Show section.
####################################################################################################
@route(consts.PREFIX + '/scanShowDB')
def scanShowDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanShowDB with an URL of %s ***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	bScanStatusCount = 0
	bScanStatusCountOf = 0	
	try:
		Log.Debug("About to open file %s" %(myCSVFile))
		csvfile = io.open(myCSVFile,'wb')
		# Create output file, and print the header
		csvwriter = csv.DictWriter(csvfile, fieldnames=tvseries.getTVHeader(Prefs['TV_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		Log.Debug("Writing header")
		csvwriter.writeheader()
		if Prefs['TV_Level'] in tvfields.singleCall:
			bExtraInfo = False
		else:
			bExtraInfo = True	
		Log.Debug('Starting to fetch the list of items in this section')
		while True:
			Log.Debug("Walking medias")
			iCount = bScanStatusCount
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCount) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZETV)			
			partMedias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
			if bScanStatusCount == 0:
				bScanStatusCountOf = partMedias.get('totalSize')
				Log.Debug('Amount of items in this section is %s' %bScanStatusCountOf)
			# HERE WE DO STUFF
			Log.Debug("Retrieved part of medias okay [%s of %s]" %(str(iCount), str(bScanStatusCountOf)))
			AllTVShows = partMedias.xpath('.//Directory')
			for TVShows in AllTVShows:
				bScanStatusCount += 1
				iCount += 1
				ratingKey = TVShows.get("ratingKey")
				title = TVShows.get("title")
				if 'Show Only' in Prefs['TV_Level']:
					myRow = {}
					# Export the info			
					myRow = tvseries.getShowOnly(TVShows, myRow, Prefs['TV_Level'])
					iCount += consts.CONTAINERSIZETV - 1
					try:
						csvwriter.writerow(myRow)
					except Exception, e:
						Log.Exception('Exception happend in ScanShowDB: ' + str(e))
					continue					
				else:
					if Prefs['TV_Level'] in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
						myURL = misc.GetLoopBack() + '/library/metadata/' + ratingKey
						tvSeriesInfo = XML.ElementFromURL(myURL, timeout=float(consts.PMSTIMEOUT))
						# Getting stuff from the main TV-Show page
						# Grab collections
						serieInfo = tvSeriesInfo.xpath('//Directory/Collection')
						myCol = ''
						for collection in serieInfo:
							if myCol == '':
								myCol = collection.get('tag')
							else:
								myCol = myCol + Prefs['Seperator'] + collection.get('tag')
						if myCol == '':
							myCol = 'N/A'
						# Grab locked fields
						serieInfo = tvSeriesInfo.xpath('//Directory/Field')
						myField = ''
						for Field in serieInfo:
							if myField == '':
								myField = Field.get('name')
							else:
								myField = myField + Prefs['Seperator'] + Field.get('name')
						if myField == '':
							myField = 'N/A'
					# Get size of TV-Show
					episodeTotalSize = XML.ElementFromURL(misc.GetLoopBack() + '/library/metadata/' + ratingKey + '/allLeaves?X-Plex-Container-Start=0&X-Plex-Container-Size=0', timeout=float(consts.PMSTIMEOUT)).xpath('@totalSize')[0]
					Log.Debug('Show: %s has %s episodes' %(title, episodeTotalSize))
					episodeCounter = 0
					baseURL = misc.GetLoopBack() + '/library/metadata/' + ratingKey + '/allLeaves'
					while True:
						myURL = baseURL + '?X-Plex-Container-Start=' + str(episodeCounter) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEEPISODES)
						Log.Debug('Show %s of %s with a RatingKey of %s at myURL: %s with a title of "%s" episode %s of %s' %(iCount, bScanStatusCountOf, ratingKey, myURL, title, episodeCounter, episodeTotalSize))
						MainEpisodes = XML.ElementFromURL(myURL, timeout=float(consts.PMSTIMEOUT))
						Episodes = MainEpisodes.xpath('//Video')
						for Episode in Episodes:
							myRow = {}	
							# Was extra info needed here?
							if bExtraInfo:
								myExtendedInfoURL = misc.GetLoopBack() + '/library/metadata/' + misc.GetRegInfo(Episode, 'ratingKey') + '?includeExtras=1'
								if Prefs['Check_Files']:				
									myExtendedInfoURL = myExtendedInfoURL + '&checkFiles=1'							
								Episode = XML.ElementFromURL(myExtendedInfoURL, timeout=float(consts.PMSTIMEOUT)).xpath('//Video')[0]
							# Export the info			
							myRow = tvseries.getTvInfo(Episode, myRow)
							if Prefs['TV_Level'] in ['Level 2','Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7', 'Level 8', 'Level 666']:
								myRow['Collection'] = myCol
								myRow['Locked Fields'] = myField		
							csvwriter.writerow(myRow)								
						episodeCounter += consts.CONTAINERSIZEEPISODES
						if episodeCounter > int(episodeTotalSize):
							break			



			# Got to the end of the line?		
			if int(partMedias.get('size')) == 0:
				break
		csvfile.close
	except ValueError as err:
		Log.Exception('Exception happend as %s' %err.args)		
	Log.Debug("******* Ending scanShowDB ***********")

####################################################################################################
# This function will show a menu with playlists
####################################################################################################
@route(consts.PREFIX + '/selectPList')
def selectPList():
	Log.Debug("User selected to export a playlist")
	# Abort if set to auto path
	if Prefs['Auto_Path']:
		message = 'Playlists can not be exported when path is set to auto. You need to specify a manual path in the prefs'
		oc = ObjectContainer(title1='Error!. Playlists can not be exported when path is set to auto. You need to specify a manual path in the prefs', no_cache=True, message=message)
		oc.add(DirectoryObject(key=Callback(MainMenu), title="Go to the Main Menu"))
		Log.Debug('Can not continue, since on AutoPath')
		return oc
	# Else build up a menu of the playlists
	oc = ObjectContainer(title1='Select Playlist to export', no_cache=True)
	playlists = XML.ElementFromURL(misc.GetLoopBack() + '/playlists/all', timeout=float(consts.PMSTIMEOUT)).xpath('//Playlist')
	for playlist in playlists:
		title = playlist.get('title')
		thumb = misc.GetLoopBack() + playlist.get('composite')
		playlistType= playlist.get('playlistType')
		key = playlist.get('key')
		if playlistType in ['video','audio', 'photo']:
			Log.Debug("Added playlist: " + title + " to the listing with a key of: " + key)
			oc.add(DirectoryObject(key=Callback(backgroundScan, title=playlistType, sectiontype='playlists', key=key, random=time.clock()), thumb=thumb, title='Export from "' + title + '"', summary='Export list from "' + title + '"'))
	oc.add(DirectoryObject(key=Callback(MainMenu), title="Go to the Main Menu"))
	return oc

####################################################################################################
# Here we go for the actual playlist
####################################################################################################
@route(consts.PREFIX + '/getPListContents')
def scanPList(key, playListType, myCSVFile):
	Log.Debug("******* Starting scanPList with an URL of: %s" %(key))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	bScanStatusCount = 0
	try:
		mySepChar = Prefs['Seperator']
		Log.Debug('Writing headers for Playlist Export')
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=playlists.getPlayListHeader(playListType, Prefs['PlayList_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		csvwriter.writeheader()
		iCount = bScanStatusCount
		Log.Debug('Starting to fetch the list of items in this section')
		myRow = {}
		if playListType == 'video':
			playListItems = XML.ElementFromURL(key, timeout=float(consts.PMSTIMEOUT)).xpath('//Video')
		elif playListType == 'audio':
			playListItems = XML.ElementFromURL(key, timeout=float(consts.PMSTIMEOUT)).xpath('//Track')
		elif playListType == 'photo':
			playListItems = XML.ElementFromURL(key, timeout=float(consts.PMSTIMEOUT)).xpath('//Photo')
		for playListItem in playListItems:
			playlists.getPlayListInfo(playListItem, myRow, playListType)
			csvwriter.writerow(myRow)
	except:
		Log.Critical("Detected an exception in scanPList")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	message = 'All done'
	oc = ObjectContainer(title1='Playlists', no_cache=True, message=message)
	oc.add(DirectoryObject(key=Callback(MainMenu), title="Go to the Main Menu"))
	Log.Debug("******* Ending scanPListDB ***********")
	return oc

####################################################################################################
# This function will scan a Music section.
####################################################################################################
@route(consts.PREFIX + '/scanArtistDB')
def scanArtistDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanArtistDB with an URL of %s ***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	bScanStatusCount = 0
	try:
		mySepChar = Prefs['Seperator']
		Log.Debug('Writing headers for Audio Export')
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=audio.getMusicHeader(Prefs['Artist_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		csvwriter.writeheader()
		if Prefs['Artist_Level'] in audiofields.singleCall:
			bExtraInfo = False
		else:
			bExtraInfo = True
		Log.Debug('Starting to fetch the list of items in this section')
		fetchURL = myMediaURL + '?type=10&X-Plex-Container-Start=' + str(bScanStatusCount) + '&X-Plex-Container-Size=0'
		medias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
		if bScanStatusCount == 0:
			bScanStatusCountOf = medias.get('totalSize')
			Log.Debug('Amount of items in this section is %s' %bScanStatusCountOf)
		Log.Debug("Walking medias")
		while True:
			fetchURL = myMediaURL + '?type=10&sort=artist.titleSort,album.titleSort:asc&X-Plex-Container-Start=' + str(bScanStatusCount) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEAUDIO)	
			medias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
			if medias.get('size') == '0':
				break
			# HERE WE DO STUFF
			tracks = medias.xpath('.//Track')
			for track in tracks:
				bScanStatusCount += 1
				# Get the Audio Info
				myRow = {}
				# Was extra info needed here?
				if bExtraInfo:
					myExtendedInfoURL = misc.GetLoopBack() + '/library/metadata/' + misc.GetRegInfo(track, 'ratingKey') + '?includeExtras=1'
					if Prefs['Check_Files']:				
						myExtendedInfoURL = myExtendedInfoURL + '&checkFiles=1'										
					track = XML.ElementFromURL(myExtendedInfoURL, timeout=float(consts.PMSTIMEOUT)).xpath('//Track')[0]
				audio.getAudioInfo(track, myRow)
				csvwriter.writerow(myRow)	
		csvfile.close
	except:
		Log.Critical("Detected an exception in scanArtistDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanArtistDB ***********")

####################################################################################################
# This function will scan a Photo section.
####################################################################################################
@route(consts.PREFIX + '/scanPhotoDB')
def scanPhotoDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanPhotoDB with an URL of %s ***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	bScanStatusCount = 0
	iLocalCounter = 0
	try:
		mySepChar = Prefs['Seperator']
		Log.Debug('Writing headers for Photo Export')
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=photo.getHeader(Prefs['Photo_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		csvwriter.writeheader()
		if Prefs['Photo_Level'] in photofields.singleCall:
			bExtraInfo = False
		else:
			bExtraInfo = True
		Log.Debug('Starting to fetch the list of items in this section')
		fetchURL = myMediaURL + '?type=10&X-Plex-Container-Start=' + str(iLocalCounter) + '&X-Plex-Container-Size=0'
		medias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
		bScanStatusCountOf = 'N/A'
		Log.Debug("Walking medias")
		while True:
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iLocalCounter) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEPHOTO)	
			medias = XML.ElementFromURL(fetchURL, timeout=float(consts.PMSTIMEOUT))
			if medias.get('size') == '0':
				break
			getPhotoItems(medias, csvwriter, bExtraInfo)
			iLocalCounter += int(consts.CONTAINERSIZEPHOTO)	
		csvfile.close
	except:
		Log.Critical("Detected an exception in scanPhotoDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanPhotoDB ***********")
	return

####################################################################################################
# This function will walk directories in a photo section
####################################################################################################
@route(consts.PREFIX + '/getPhotoItems')
def getPhotoItems(medias, csvwriter, bExtraInfo):
	global bScanStatusCount
	# Start by grapping pictures here
	et = medias.xpath('.//Photo')
	for element in et:
		myRow = {}
		myRow = photo.getInfo(element, myRow)		
		bScanStatusCount += 1
		csvwriter.writerow(myRow)			
	# Elements that are directories
	et = medias.xpath('.//Directory')
	for element in et:
		myExtendedInfoURL = misc.GetLoopBack() + element.get('key') + '?includeExtras=1'
#		if bExtraInfo:
#			if Prefs['Check_Files']:				
#				myExtendedInfoURL = myExtendedInfoURL + '&checkFiles=1'										
		# TODO: Make small steps here when req. photos
		elements = XML.ElementFromURL(myExtendedInfoURL, timeout=float(consts.PMSTIMEOUT))
#		if bExtraInfo:
			
		getPhotoItems(elements, csvwriter, bExtraInfo)

