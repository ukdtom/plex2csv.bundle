####################################################################################################
#	This plugin will create a list of medias in a section of Plex as a csv file
#
#	Made by 
#	dane22....A Plex Community member
#	srazer....A Plex Community member
# CCarpo....A Plex Community member
#
####################################################################################################

# To find Work in progress, search this file for the word ToDo

import os
import unicodedata
import time
import io
import csv
import datetime
from textwrap import wrap, fill
import re
from lxml import etree as et
import urllib2
import base64
import uuid
from urllib2 import Request, urlopen, URLError, HTTPError
import movies, tvseries, audio
import consts, misc

VERSION = ' V0.0.2.9'
NAME = 'Plex2csv'
ART = 'art-default.jpg'
ICON = 'icon-Plex2csv.png'
PREFIX = '/applications/Plex2csv'
APPGUID = '7608cf36-742b-11e4-8b39-00089bd210b2'
DESCRIPTION = 'Export Plex libraries to CSV-Files'
MYHEADER = {}
CONTAINERSIZEMOVIES = 20
CONTAINERSIZETV = 5
CONTAINERSIZEAUDIO = 5

bScanStatus = 0			# Current status of the background scan
initialTimeOut = 12		# When starting a scan, how long in seconds to wait before displaying a status page. Needs to be at least 1.
sectiontype = ''		# Type of section been exported



####################################################################################################
# Start function
####################################################################################################
def Start():
#	print("********  Started %s on %s  **********" %(NAME  + VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME  + VERSION, Platform.OS))
#	global MYHEADER
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME  + VERSION
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(ICON)
	HTTP.CacheTime = 0
	getToken()

#********** Get token from plex.tv *********
''' This will return a valid token, that can be used for authenticating if needed, to be inserted into the header '''
# DO NOT APPEND THE TOKEN TO THE URL...IT MIGHT BE LOGGED....INSERT INTO THE HEADER INSTEAD
@route(PREFIX + '/getToken')
def getToken():
	Log.Debug('Starting to get the token')
	global MYHEADER
	if Prefs['Authenticate']:
		# Start by checking, if we already got a token
		if 'authentication_token' in Dict and Dict['authentication_token'] != 'NuKeMe':
			Log.Debug('Got a token from local storage')			
			MYHEADER['X-Plex-Token'] = Dict['authentication_token']
		else:
			Log.Debug('Need to generate a token first from plex.tv')
			userName = Prefs['Plex_User']
			userPwd = Prefs['Plex_Pwd']
			myUrl = 'https://plex.tv/users/sign_in.json'
			# Create the authentication string
			base64string = String.Base64Encode('%s:%s' % (userName, userPwd))
			# Create the header
			MYAUTHHEADER= {}
			MYAUTHHEADER['X-Plex-Product'] = DESCRIPTION
			MYAUTHHEADER['X-Plex-Client-Identifier'] = APPGUID
			MYAUTHHEADER['X-Plex-Version'] = VERSION
			MYAUTHHEADER['Authorization'] = 'Basic ' + base64string
			MYAUTHHEADER['X-Plex-Device-Name'] = NAME
			# Send the request
			try:
				httpResponse = HTTP.Request(myUrl, headers=MYAUTHHEADER, method='POST')
				myToken = JSON.ObjectFromString(httpResponse.content)['user']['authentication_token']
				Log.Debug('Response from plex.tv was : %s' %(httpResponse.headers["status"]))
			except:
				Log.Critical('Exception happend when trying to get a token from plex.tv')
				Log.Critical('Returned answer was %s' %httpResponse.content)
				Log.Critical('Status was: %s' %httpResponse.headers) 			
			Dict['authentication_token'] = myToken
			Dict.Save()
			MYHEADER['X-Plex-Token'] = myToken
	else:
			Log.Debug('Authentication disabled')
			return ''

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
@route(PREFIX + '/MainMenu')
def MainMenu(random=0):
	Log.Debug("**********  Starting MainMenu  **********")
	global sectiontype
	oc = ObjectContainer()
	try:
		if ValidateExportPath():
			sections = XML.ElementFromURL('http://127.0.0.1:32400/library/sections?', headers=MYHEADER).xpath('//Directory')
			for section in sections:
				sectiontype = section.get('type')
#				if sectiontype != "photo" and sectiontype != 'artist': # ToDo: Remove artist when code is in place for it.
				if sectiontype != "photo": # ToDo: Remove artist when code is in place for it.
					title = section.get('title')
					key = section.get('key')
					thumb = 'http://127.0.0.1:32400' + section.get('thumb')
					Log.Debug('Title of section is %s with a key of %s' %(title, key))
					oc.add(DirectoryObject(key=Callback(backgroundScan, title=title, sectiontype=sectiontype, key=key, random=time.clock()), thumb=thumb, title='Export from "' + title + '"', summary='Export list from "' + title + '"'))
		else:
			oc.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Select Preferences to set the export path"))
	except:
		Log.Critical("Exception happened in MainMenu")
		raise
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc

####################################################################################################
# Validate Export Path
####################################################################################################
@route(PREFIX + '/ValidateExportPath')
def ValidateExportPath():
	Log.Debug('Entering ValidateExportPath')
	# Let's check that the provided path is actually valid
	myPath = Prefs['Export_Path']
	Log.Debug('My master set the Export path to: %s' %(myPath))
	try:
		#Let's see if we can add out subdirectory below this
		if os.path.exists(myPath):
			Log.Debug('Master entered a path that already existed as: %s' %(myPath))
			if not os.path.exists(os.path.join(myPath, NAME)):
				os.makedirs(os.path.join(myPath, NAME))
				Log.Debug('Created directory named: %s' %(os.path.join(myPath, NAME)))
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
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
	if Prefs['NukeToken']:
		# My master wants to nuke the local store
		Log.Debug('Removing Token from local storage')
		# DICT RESET IS BROKEN IN THE API....SIGH....
#		Dict.Reset()
		Dict['authentication_token'] = 'NuKeMe'
		Dict.Save()
	# Lets get the token again, in case credentials are switched, or token is deleted
	getToken()
	if Prefs['NukeToken']:
		# My master has nuked the local store, so reset the prefs flag
		myHTTPPrefix = 'http://127.0.0.1:32400/:/plugins/com.plexapp.plugins.Plex2csv/prefs/'
		myURL = myHTTPPrefix + 'set?NukeToken=0'
		Log.Debug('Prefs Sending : ' + myURL)
		HTTP.Request(myURL, immediate=True, headers=MYHEADER)

####################################################################################################
# Export Complete.
####################################################################################################
@route(PREFIX + '/complete')
def complete(title=''):
	global bScanStatus
	Log.Debug("*******  All done, tell my Master  ***********")
	title = ('Export Completed for %s' %(title))
	message = 'Check the directory: %s' %(os.path.join(Prefs['Export_Path'], NAME)) 
	oc2 = ObjectContainer(title1=title, no_cache=True, message=message)
	oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Go to the Main Menu"))
	# Reset the scanner status
	bScanStatus = 0
	Log.Debug("*******  Ending complete  ***********")
	return oc2

####################################################################################################
# Start the scanner in a background thread and provide status while running
####################################################################################################
@route(PREFIX + '/backgroundScan')
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
			bScanStatus = 0
		elif bScanStatus == 401:
			oc2 = ObjectContainer(title1="ERROR", no_history=True)
			# Error condition set by scanner
			summary = "When running in like Home mode, you must enable authentication in the preferences"
			oc2 = ObjectContainer(title1=summary,no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="Authentication error.", summary=summary))			
			bScanStatus = 0
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
@route(PREFIX + '/backgroundScanThread')
def backgroundScanThread(title, key, sectiontype):
	Log.Debug("*******  Starting backgroundScanThread  ***********")
	global bScanStatus
	global bScanStatusCount
	global bScanStatusCountOf	
	try:
		bScanStatus = 1
		Log.Debug("Section type is %s" %(sectiontype))
		myMediaURL = 'http://127.0.0.1:32400/library/sections/' + key + "/all"
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
		myCSVFile = os.path.join(Prefs['Export_Path'], NAME, newtitle + '-' + myLevel + '-' + timestr + '.csv')
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
@route(PREFIX + '/scanMovieDB')
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
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCurrent) + '&X-Plex-Container-Size=' + str(CONTAINERSIZEMOVIES)
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
	except HTTPError as e:
		Log.Critical('The server couldn\'t fulfill the request. Errorcode was %s' %e.code)
		bScanStatus = 401
	except URLError as e:
		Log.Critical('We failed to reach a server. Reason was %s' %e.reason)
		bScanStatus = 401
	except ValueError, Argument:
		Log.Critical('Unknown error in scanMovieDb %s' %(Argument))
		bScanStatus = 99
		raise e
	Log.Debug("******* Ending scanMovieDB ***********")

####################################################################################################
# This function will scan a TV-Show section.
####################################################################################################
@route(PREFIX + '/scanShowDB')
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
			fetchURL = myMediaURL + '?X-Plex-Container-Start=' + str(iCount) + '&X-Plex-Container-Size=' + str(CONTAINERSIZETV)			
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
				myURL = "http://127.0.0.1:32400/library/metadata/" + ratingKey + "/allLeaves"
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
@route(PREFIX + '/scanArtistDB')
def scanArtistDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanArtistDB with an URL of %s ***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	myMediaPaths = []
	bScanStatusCount = 0
	try:
		mySepChar = Prefs['Seperator']
		#TODO 'Fix without framework'
		myMedias = XML.ElementFromURL(myMediaURL, headers=MYHEADER).xpath('//Directory')
		bScanStatusCountOf = len(myMedias)
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=audio.getMusicHeader(Prefs['Artist_Level']), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		csvwriter.writeheader()
		for myMedia in myMedias:
			bScanStatusCount += 1
			ratingKey = myMedia.get("ratingKey")
			myURL = "http://127.0.0.1:32400/library/metadata/" + ratingKey + "/allLeaves"
			Log.Debug("Album %s of %s with a RatingKey of %s at myURL: %s" %(bScanStatusCount, bScanStatusCountOf, ratingKey, myURL))

			#TODO Switch away from framework here
			myMedias2 = XML.ElementFromURL(myURL, headers=MYHEADER).xpath('//Track')			

			for myMedia2 in myMedias2:
				myRow = {}
				# Get the Audio Info
				audio.getAudioInfo(myMedia, myRow, MYHEADER, csvwriter, myMedia2)
				csvwriter.writerow(myRow)			
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, misc.GetRegInfo(myMedia, 'title') + '-' + misc.GetRegInfo(myMedia2, 'parentTitle')))
		return
	except:
		Log.Critical("Detected an exception in scanArtistDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanArtistDB ***********")



	

