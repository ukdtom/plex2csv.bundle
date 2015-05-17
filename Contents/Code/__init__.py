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
import movies, tvseries, audio
import consts, misc

# Threading stuff
bScanStatus = 0				# Current status of the background scan
initialTimeOut = 12		# When starting a scan, how long in seconds to wait before displaying a status page. Needs to be at least 1.
sectiontype = ''			# Type of section been exported
bScanStatusCount = 0	# Number of item currently been investigated

LOOPBACK = ''					# Loopback address in use. Gets set from the misc module
MYHEADER={}						# Header to be used when accessing PMS

####################################################################################################
# Start function
####################################################################################################
def Start():
	print("********  Started %s on %s  **********" %(consts.NAME  + consts.VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(consts.NAME  + consts.VERSION, Platform.OS))
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(consts.ART)
	ObjectContainer.title1 = consts.NAME  + consts.VERSION
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(consts.ICON)
	HTTP.CacheTime = 0
	# Get the loopback address
	global LOOPBACK
	LOOPBACK = misc.GetLoopBack()
	Log.Debug('Loopback address is: %s' %(LOOPBACK))
	Log.Debug('Misc module is version: %s' %misc.getVersion())

####################################################################################################
# Main menu
####################################################################################################
@handler(consts.PREFIX, consts.NAME, thumb=consts.ICON, art=consts.ART)
@route(consts.PREFIX + '/MainMenu')
def MainMenu(random=0):
	Log.Debug("**********  Starting MainMenu  **********")
	global sectiontype
	oc = ObjectContainer()
	try:
		if ValidateExportPath():
			sections = XML.ElementFromURL(LOOPBACK + '/library/sections?', headers=MYHEADER).xpath('//Directory')
			for section in sections:
				sectiontype = section.get('type')
#				if sectiontype != "photo" and sectiontype != 'artist': # ToDo: Remove artist when code is in place for it.
				if sectiontype != "photo": # ToDo: Remove artist when code is in place for it.
					title = section.get('title')
					key = section.get('key')
					thumb = LOOPBACK + section.get('thumb')
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
@route(consts.PREFIX + '/complete')
def complete(title=''):
	global bScanStatus
	Log.Debug("*******  All done, tell my Master  ***********")
	title = ('Export Completed for %s' %(title))
	message = 'Check the directory: %s' %(os.path.join(Prefs['Export_Path'], consts.NAME)) 
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
					oc2 = complete(title=title)
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
	try:
		bScanStatus = 1
		Log.Debug("Section type is %s" %(sectiontype))
		myMediaURL = LOOPBACK + '/library/sections/' + key + "/all"
		Log.Debug("Path to medias in section is %s" %(myMediaURL))
		# Get current date and time
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# Generate Output FileName
		if sectiontype == 'show':
			myLevel = Prefs['TV_Level']
		if sectiontype == 'movie':
			myLevel = Prefs['Movie_Level']
		if sectiontype == 'artist':
			myLevel = Prefs['Artist_Level']
		# Remove invalid caracters, if on Windows......
		newtitle = re.sub('[\/[:#*?"<>|]', '_', title)
		myCSVFile = os.path.join(Prefs['Export_Path'], consts.NAME, newtitle + '-' + myLevel + '-' + timestr + '.csv')
		Log.Debug('Output file is named %s' %(myCSVFile))
		# Scan the database based on the type of section
		if sectiontype == "movie":
			scanMovieDB(myMediaURL, myCSVFile)
		elif sectiontype == "artist":
			scanArtistDB(myMediaURL, myCSVFile)
		elif sectiontype == "show":
			scanShowDB(myMediaURL, myCSVFile)
		else:
			Log.Debug("Error: unknown section type: %s" %(sectiontype))
			bScanStatus = 91
		# Stop scanner on error
		if bScanStatus >= 90: return
		Log.Debug("*******  Ending backgroundScanThread  ***********")
		bScanStatus = 2
		return
	except:
		Log.Critical("Exception happened in backgroundScanThread")
		bScanStatus = 99
		raise
	Log.Debug("*******  Ending backgroundScanThread  ***********")

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
		while True:
			Log.Debug("Walking medias")
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCurrent) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEMOVIES)
			iCount = bScanStatusCount
			partMedias = XML.ElementFromURL(fetchURL, headers=MYHEADER)
			if bScanStatusCount == 0:
				bScanStatusCountOf = partMedias.get('totalSize')
				Log.Debug('Amount of items in this section is %s' %bScanStatusCountOf)
			# HERE WE DO STUFF
			Log.Debug("Retrieved part of medias okay [%s of %s]" %(str(bScanStatusCount), str(bScanStatusCountOf)))
			medias = partMedias.xpath('.//Video')
			for media in medias:
				myRow = {}
				# Export the info			
				myRow = movies.getMovieInfo(media, myRow, MYHEADER, csvwriter)
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
		raise e
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
		Log.Debug('Starting to fetch the list of items in this section')
		while True:
			Log.Debug("Walking medias")
			iCount = bScanStatusCount
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCount) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZETV)			
			partMedias = XML.ElementFromURL(fetchURL, headers=MYHEADER)
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
				myURL = LOOPBACK + '/library/metadata/' + ratingKey + '/allLeaves'
				Log.Debug('Show %s of %s with a RatingKey of %s at myURL: %s with a title of "%s"' %(iCount, bScanStatusCountOf, ratingKey, myURL, title))			
				MainEpisodes = XML.ElementFromURL(myURL, headers=MYHEADER)
				Episodes = MainEpisodes.xpath('//Video')
				Log.Debug('Show %s with an index of %s contains %s episodes' %(MainEpisodes.get('parentTitle'), iCount, MainEpisodes.get('size')))
				for Episode in Episodes:
					myRow = {}	
					myRow = tvseries.ExportTVShows(Episode, myRow, MYHEADER, TVShows)
					Log.Debug("Show %s from database: %s Season %s Episode %s title: %s" %(bScanStatusCount, misc.GetRegInfo(Episode, 'grandparentTitle'), misc.GetRegInfo(Episode, 'parentIndex'), misc.GetRegInfo(Episode, 'index'), misc.GetRegInfo(Episode, 'title')))							
					csvwriter.writerow(myRow)								
			# Got to the end of the line?		
			if int(partMedias.get('size')) == 0:
				break
		csvfile.close
	except ValueError as err:
		Log.Debug('Exception happend as %s' %err.args)		
	Log.Debug("******* Ending scanShowDB ***********")

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
		iCount = bScanStatusCount
		Log.Debug('Starting to fetch the list of items in this section')
		while True:
			Log.Debug("Walking medias")
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCount) + '&X-Plex-Container-Size=' + str(consts.CONTAINERSIZEAUDIO)	
			partMedias = XML.ElementFromURL(fetchURL, headers=MYHEADER)
			if bScanStatusCount == 0:
				bScanStatusCountOf = partMedias.get('totalSize')
				Log.Debug('Amount of items in this section is %s' %bScanStatusCountOf)
			# HERE WE DO STUFF
			Log.Debug("Retrieved part of medias okay [%s of %s]" %(str(iCount), str(bScanStatusCountOf)))
			AllParts = partMedias.xpath('.//Directory')
			for Part in AllParts:
				bScanStatusCount += 1
				iCount += 1
				ratingKey = Part.get("ratingKey")
				title = Part.get("title")
				myURL = LOOPBACK + '/library/metadata/' + ratingKey + '/allLeaves'				
				Log.Debug("Album %s of %s with a RatingKey of %s at myURL: %s" %(bScanStatusCount, bScanStatusCountOf, ratingKey, myURL))		
				myMedias2 = XML.ElementFromURL(myURL, headers=MYHEADER).xpath('//Track')			
				for myMedia2 in myMedias2:
					myRow = {}
					# Get the Audio Info
					audio.getAudioInfo(Part, myRow, MYHEADER, csvwriter, myMedia2)
					csvwriter.writerow(myRow)			
				Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, misc.GetRegInfo(Part, 'title') + '-' + misc.GetRegInfo(myMedia2, 'parentTitle')))
			# Got to the end of the line?		
			if int(partMedias.get('size')) == 0:
				break
		csvfile.close
	except:
		Log.Critical("Detected an exception in scanArtistDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanArtistDB ***********")

