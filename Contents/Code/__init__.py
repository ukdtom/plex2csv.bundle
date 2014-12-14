####################################################################################################
#	This plugin will create a list of medias in a section of Plex as a csv file
#
#	Made by 
#	dane22....A Plex Community member
#	srazer....A Plex Community member
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

VERSION = ' V0.0.2.4'
NAME = 'Plex2csv'
ART = 'art-default.jpg'
ICON = 'icon-Plex2csv.png'
PREFIX = '/applications/Plex2csv'
APPGUID = '7608cf36-742b-11e4-8b39-00089bd210b2'
DESCRIPTION = 'Export Plex libraries to CSV-Files'
MYHEADER = {}

bScanStatus = 0			# Current status of the background scan
initialTimeOut = 12		# When starting a scan, how long in seconds to wait before displaying a status page. Needs to be at least 1.
sectiontype = ''		# Type of section been exported

####################################################################################################
# Start function
####################################################################################################
def Start():
#	print("********  Started %s on %s  **********" %(NAME  + VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME  + VERSION, Platform.OS))
	global MYHEADER
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
					Log.Debug('Title of section is %s with a key of %s' %(title, key))
					oc.add(DirectoryObject(key=Callback(backgroundScan, title=title, sectiontype=sectiontype, key=key, random=time.clock()), title='Export from "' + title + '"', summary='Export list from "' + title + '"'))
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

####################################################################################################
# This function will return the header for the CSV file for movies
####################################################################################################
@route(PREFIX + '/getMovieHeader')
def getMovieHeader():
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
	if (Prefs['Movie_Level'] in ['Basic','Extended','Extreme', 'Extreme 2']):
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
			'Labels'
			)
	# Extended fields
	if Prefs['Movie_Level'] in ['Extended','Extreme', 'Extreme 2']:
		fieldnames = fieldnames + (
			'Original Title',
			'Collections',
			'Added',
			'Updated'
			)
	# Extreme fields
	if Prefs['Movie_Level'] in ['Extreme', 'Extreme 2']:
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
	if Prefs['Movie_Level'] in ['Extreme 2']:			
		fieldnames = fieldnames + (
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Duration',
			'Part Container'
			)
	return fieldnames

####################################################################################################
# This function will wrap a string if needed
####################################################################################################
@route(PREFIX + '/WrapStr')
def WrapStr(myStr):
	LineWrap = int(Prefs['Line_Length'])
	if Prefs['Line_Wrap']:		
		return fill(myStr, LineWrap)
	else:
		return myStr

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
	try:
		Log.Debug('Starting to fetch the list of items in this section')
		req = Request(myMediaURL, headers=MYHEADER)
		response = urlopen(req)
	except HTTPError as e:
		Log.Critical('The server couldn\'t fulfill the request. Errorcode was %s' %e.code)
		bScanStatus = 401
	except URLError as e:
		Log.Critical('We failed to reach a server. Reason was %s' %e.reason)
		bScanStatus = 401
	except:
		Log.Critical('Unknown error in scanMovieDb')
		bScanStatus = 99
	else:
		# everything is fine
		tree = et.parse(response)
		root = tree.getroot()
		myMedias = root.findall('.//Video')		
		mySepChar = Prefs['Seperator']
		Log.Debug("Retrieved myMedias okay")
		bScanStatusCountOf = len(myMedias)
		Log.Debug("Found %s items" %(bScanStatusCountOf))
		Log.Debug("About to open file %s" %(myCSVFile))
		csvfile = io.open(myCSVFile,'wb')
		# Create output file, and print the header
		csvwriter = csv.DictWriter(csvfile, fieldnames=getMovieHeader(), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		Log.Debug("Writing header")
		csvwriter.writeheader()
		Log.Debug("Walking medias")
		for myMedia in myMedias:				
			myRow = {}
# Add all for Simple Export and above
			# Get Media ID
			myRow['Media ID'] = GetRegInfo(myMedia, 'ratingKey')
			# Get Extended info if needed
			if Prefs['Movie_Level'] in ['Basic','Extended','Extreme','Extreme 2']:				
				myExtendedInfoURL = 'http://127.0.0.1:32400/library/metadata/' + GetRegInfo(myMedia, 'ratingKey') + '?includeExtras=1&'
				ExtInfo = XML.ElementFromURL(myExtendedInfoURL, headers=MYHEADER).xpath('//Video')[0]
			# Get title
			myRow['Title'] = GetRegInfo(myMedia, 'title')
			# Get Sorted title
			myRow['Sort title'] = GetRegInfo(myMedia, 'titleSort')
			# Get Studio
			myRow['Studio'] = GetRegInfo(myMedia, 'studio')
			# Get contentRating
			myRow['Content Rating'] = GetRegInfo(myMedia, 'contentRating')
			# Get Year
			myRow['Year'] = GetRegInfo(myMedia, 'year')
			# Get Rating
			myRow['Rating'] = GetRegInfo(myMedia, 'rating')
			# Get Summary
			myRow['Summary'] = GetRegInfo(myMedia, 'summary')
			# Get Genres							
			if Prefs['Movie_Level'] in ['Extended','Extreme','Extreme 2']:
				Genres = ExtInfo.xpath('Genre/@tag')
			else:
				Genres = myMedia.xpath('Genre/@tag')
			if not Genres:
				Genres = ['']
			Genre = ''
			for myGenre in Genres:
				if Genre == '':
					Genre = myGenre
				else:
					Genre = Genre + mySepChar + myGenre
			Genre = WrapStr(Genre)
			myRow['Genres'] = Genre.encode('utf8')
			# And now for Basic Export or higher if needed, else write out the row
			if Prefs['Movie_Level'] not in ['Basic','Extended','Extreme','Extreme 2']:
				csvwriter.writerow(myRow)
			else:
# Basic and above
				# Get View Count
				myRow['View Count'] = GetRegInfo(myMedia, 'viewCount')
				# Get last watched timestamp
				lastViewedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia, 'lastViewedAt', '0')))).strftime('%m/%d/%Y')
				if lastViewedAt == '01/01/1970':
					myRow['Last Viewed at'] = ''
				else:
					myRow['Last Viewed at'] = lastViewedAt.encode('utf8')
				# Get the Tag Line
				myRow['Tagline'] = GetRegInfo(myMedia, 'tagline')
				# Get the Release Date
				myRow['Release Date'] = GetRegInfo(myMedia, 'originallyAvailableAt')
				# Get the Writers
				Writer = myMedia.xpath('Writer/@tag')
				if not Writer:
					Writer = ['']
				Author = ''
				for myWriter in Writer:
					if Author == '':
						Author = myWriter
					else:
						Author = Author + mySepChar + myWriter
				Author = WrapStr(Author)
				myRow['Writers'] = Author.encode('utf8')
				# Get the duration of the movie
				duration = ConvertTimeStamp(GetRegInfo(myMedia, 'duration', '0'))
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
						Director = Director + mySepChar + myDirector
				Director = WrapStr(Director)
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
						Label = Label + mySepChar + myLabel
				Label = WrapStr(Label)
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
						Field = Field + mySepChar + myField
				Director = WrapStr(Director)
				myRow['Locked Fields'] = Field.encode('utf8')
				# Got extras?
				Extras = ExtInfo.xpath('//Extras/@size')
				if not Extras:
					Extra = '0'
				else:
					for myExtra in Extras:
						Extra = myExtra								
				Extra = WrapStr(Extra)
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
							Role = Role + mySepChar + myRole
				elif Prefs['Movie_Level'] in ['Extended','Extreme','Extreme 2']:
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
										Role = Role + mySepChar + 'Actor: ' + myActor + ' as: ' + myActorRole
								else:
									if Role == '':
										Role = 'Actor: ' + myActor
									else:
										Role = Role + mySepChar + 'Actor: ' + myActor
				Role = WrapStr(Role)
				myRow['Roles'] = Role.encode('utf8')
				# End here, or higher level selected by my master?
				if Prefs['Movie_Level'] not in ['Extended','Extreme','Extreme 2']:
					csvwriter.writerow(myRow)
				else:
# Extended or higher
					# Here goes extended stuff, not part of basic or simple
					# Get Collections
					Collections = ExtInfo.xpath('Collection/@tag')
					if not Collections:
						Collections = ['']
					Collection = ''
					for myCollection in Collections:
						if Collection == '':
							Collection = myCollection
						else:
							Collection = Collection + mySepChar + myCollection
					Collection = WrapStr(Collection)
					myRow['Collections'] = Collection.encode('utf8')
					# Get the original title
					myRow['Original Title'] = GetRegInfo(myMedia, 'originalTitle')
					# Get Added at
					addedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia, 'addedAt', '0')))).strftime('%m/%d/%Y')
					myRow['Added'] = addedAt.encode('utf8')
					# Get Updated at
					updatedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia, 'updatedAt', '0')))).strftime('%m/%d/%Y')
					myRow['Updated'] = updatedAt.encode('utf8')
					if Prefs['Movie_Level'] not in ['Extreme','Extreme 2']:
						csvwriter.writerow(myRow)
					else:
# Extreme or higher
						# Get Video Resolution
						myRow['Video Resolution'] = GetExtInfo(ExtInfo, 'videoResolution')
						# Get Bitrate
						myRow['Bitrate'] = GetExtInfo(ExtInfo, 'bitrate')
						# Get Width
						myRow['Width'] = GetExtInfo(ExtInfo, 'width')
						# Get Height
						myRow['Height'] = GetExtInfo(ExtInfo, 'height')
						# Get Aspect Ratio
						myRow['Aspect Ratio'] = GetExtInfo(ExtInfo, 'aspectRatio')
						# Get Audio Channels
						myRow['Audio Channels'] = GetExtInfo(ExtInfo, 'audioChannels')
						# Get Audio Codec
						myRow['Audio Codec'] = GetExtInfo(ExtInfo, 'audioCodec')
						# Get Video Codec
						myRow['Video Codec'] = GetExtInfo(ExtInfo, 'videoCodec')
						# Get Container
						myRow['Container'] = GetExtInfo(ExtInfo, 'container')
						# Get Video FrameRate
						myRow['Video FrameRate'] = GetExtInfo(ExtInfo, 'videoFrameRate')
						# Everything is gathered, so let's write the row if needed
						if Prefs['Movie_Level'] in ['Extreme 2']:									
							parts = ExtInfo.xpath('//Part')
							movieParts = 0
							# Check if part is an extra or a real movie part
							for part in parts:
								if GetRegInfo(part, 'file')	!= '':
									movieParts += 1
							if movieParts > 1:
								csvwriter.writerow(myRow)
								myRow = {}						
						else:						
							csvwriter.writerow(myRow)
#Extreme 2 Level
						if Prefs['Movie_Level'] in ['Extreme 2']:
							Parts = ExtInfo.xpath('//Video/Media/Part')
							for part in parts:
								if GetRegInfo(part, 'file')	== '':
									pass
								else:
									# File Name of this Part
									myRow['Part File'] = GetMoviePartInfo(part, 'file', 'N/A')
									# File size of this part
									myRow['Part Size'] = GetMoviePartInfo(part, 'size', 'N/A')
									# Is This part Indexed
									myRow['Part Indexed'] = GetMoviePartInfo(part, 'indexes', 'N/A')
									# Part Container
									myRow['Part Container'] = GetMoviePartInfo(part, 'container', 'N/A')
									# Part Duration
									partDuration = ConvertTimeStamp(GetMoviePartInfo(part, 'duration', '0'))
									myRow['Part Duration'] = partDuration.encode('utf8')								
									csvwriter.writerow(myRow)
						# Extreme 2 ended
			bScanStatusCount += 1
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, GetRegInfo(myMedia, 'title')))
		Log.Debug("******* Ending scanMovieDB ***********")
		csvfile.close

####################################################################################################
# This function will return info from different parts of a movie
####################################################################################################
@route(PREFIX + '/GetMoviePartInfo')
def GetMoviePartInfo(ExtInfo, myField, default = ''):
	try:
		myLookUp = WrapStr(ExtInfo.get(myField))
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will return info from extended page for movies
####################################################################################################
@route(PREFIX + '/GetExtInfo')
def GetExtInfo(ExtInfo, myField, default = ''):
	try:
		myLookUp = WrapStr(ExtInfo.xpath('Media/@' + myField)[0])
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will return info from regular fields for a movies
####################################################################################################
@route(PREFIX + '/GetRegInfo')
def GetRegInfo(myMedia, myField, default = ''):
	try:
		if myField in ['rating']:			
			myLookUp = "{0:.1f}".format(float(myMedia.get(myField)))
		else:			
			myLookUp = WrapStr(fixCRLF(myMedia.get(myField)))
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s. Reverting to default' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will return the header for the CSV file for TV-Shows
####################################################################################################
@route(PREFIX + '/getTVHeader')
def getTVHeader():
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
	if (Prefs['TV_Level'] in ['Basic','Extended','Extreme', 'Extreme2']):
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
	if Prefs['TV_Level'] in ['Extended','Extreme', 'Extreme2']:
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
			'Extras'
			)
	# Extreme fields
	if Prefs['TV_Level'] in ['Extreme', 'Extreme2']:
		fieldnames = fieldnames + (			
			'Part Duration',
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Container'			
			)
	return fieldnames

####################################################################################################
# This function will scan a TV-Show section.
####################################################################################################
@route(PREFIX + '/scanShowDB')
def scanShowDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanShowDB with an URL of %s ***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	global bScanStatus
	myMediaPaths = []
	bScanStatusCount = 0
	try:
		Log.Debug('Starting to fetch the list of items in this section')
		req = Request(myMediaURL, headers=MYHEADER)
		response = urlopen(req)
	except HTTPError as e:
		Log.Critical('The server couldn\'t fulfill the request. Errorcode was %s' %e.code)
		bScanStatus = 401
	except URLError as e:
		Log.Critical('We failed to reach a server. Reason was %s' %e.reason)
		bScanStatus = 401
	except:
		Log.Critical('Unknown error in scanMovieDb')
		bScanStatus = 99
	else:
		mySepChar = Prefs['Seperator']
		tree = et.parse(urllib2.urlopen(req))	
		root = tree.getroot()
		myMedias = root.findall('.//Directory')		
		bScanStatusCountOf = len(myMedias)
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=getTVHeader(), delimiter=Prefs['Delimiter'], quoting=csv.QUOTE_NONNUMERIC)
		csvwriter.writeheader()
		for myMedia in myMedias:
			bScanStatusCount += 1
			ratingKey = myMedia.get("ratingKey")
			myURL = "http://127.0.0.1:32400/library/metadata/" + ratingKey + "/allLeaves?"
			Log.Debug("Show %s of %s with a RatingKey of %s at myURL: %s" %(bScanStatusCount, bScanStatusCountOf, ratingKey, myURL))
			req = Request(myURL, headers=MYHEADER)
			tree2 = et.parse(urllib2.urlopen(req))		
			root2 = tree2.getroot()
			myMedias2 = root2.findall('.//Video')		
			for myMedia2 in myMedias2:
# Simple and above
				myRow = {}
				# Get episode rating key
				myRow['Id'] = GetRegInfo(myMedia2, 'ratingKey')
				# Get Serie Title
				myRow['Series Title'] = GetRegInfo(myMedia2, 'grandparentTitle')
				# Get Episode sort Title
				myRow['Episode Sort Title'] = GetRegInfo(myMedia2, 'titleSort')
				# Get Episode title
				myRow['Episode Title'] = GetRegInfo(myMedia2, 'title')
				# Get Year
				myRow['Year'] = GetRegInfo(myMedia2, 'year')
				# Get Season number
				myRow['Season'] = GetRegInfo(myMedia2, 'parentIndex')
				# Get Episode number
				myRow['Episode'] = GetRegInfo(myMedia2, 'index')
				# Get Content Rating
				myRow['Content Rating'] = GetRegInfo(myMedia2, 'contentRating')
				# Get summary
				myRow['Summary'] = GetRegInfo(myMedia2, 'summary')
				# Get Rating
				myRow['Rating'] = GetRegInfo(myMedia2, 'rating')
				# And now for Basic Export
				if Prefs['TV_Level'] not in ['Basic','Extended','Extreme']:
					csvwriter.writerow(myRow)
				else:
# Basic and above
					# Get Watched count
					myRow['View Count'] = GetRegInfo(myMedia2, 'viewCount')
					# Get last watched timestamp
					lastViewedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia2, 'lastViewedAt', '0')))).strftime('%m/%d/%Y')
					if lastViewedAt == '01/01/1970':
						myRow['Last Viewed at'] = ''
					else:
						myRow['Last Viewed at'] = lastViewedAt.encode('utf8')
					# Get Studio
					myRow['Studio'] = GetRegInfo(myMedia2, 'studio')
					# Get Originally Aired
					myRow['Originally Aired'] = GetRegInfo(myMedia2, 'originallyAvailableAt')
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
					Author = WrapStr(Author)
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
							Genre = Genre + mySepChar + myGenre
					Genre = WrapStr(Genre)
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
							Director = Director + mySepChar + myDirector
					Director = WrapStr(Director)
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
							Role = Role + mySepChar + myRole
					Role = WrapStr(Role)
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
							Label = Label + mySepChar + myLabel
					Label = WrapStr(Label)
					myRow['Labels'] = Label.encode('utf8')
					# Get the duration of the episode
					duration = ConvertTimeStamp(GetRegInfo(myMedia2, 'duration', '0'))
					myRow['Duration'] = duration.encode('utf8')
					# Get Added at
					addedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia2, 'addedAt', '0')))).strftime('%m/%d/%Y')
					myRow['Added'] = addedAt.encode('utf8')
					# Get Updated at
					updatedAt = (Datetime.FromTimestamp(float(GetRegInfo(myMedia2, 'updatedAt', '0')))).strftime('%m/%d/%Y')
					myRow['Updated'] = updatedAt.encode('utf8')
					# Everything is gathered, so let's write the row if needed
					if Prefs['TV_Level'] not in ['Extended','Extreme']:
						csvwriter.writerow(myRow)
					else:		
# Extended or above		
						myExtendedInfoURL = 'http://127.0.0.1:32400/library/metadata/' + GetRegInfo(myMedia2, 'ratingKey') + '?checkFiles=1&includeExtras=1&'
						Medias2 = XML.ElementFromURL(myExtendedInfoURL, headers=MYHEADER).xpath('//Media')	
						if len(Medias2)>1:
							csvwriter.writerow(myRow)
							myRow = {}										
						for Media in Medias2:
							# VideoResolution
							myRow['Video Resolution'] = GetMoviePartInfo(Media, 'videoResolution', 'N/A')
							# id
							myRow['Media Id'] = GetMoviePartInfo(Media, 'id', 'N/A')
							# Duration
							Mediaduration = ConvertTimeStamp(GetRegInfo(Media, 'duration', '0'))
							myRow['Media Duration'] = Mediaduration.encode('utf8')
							# Bitrate
							myRow['Bit Rate'] = GetMoviePartInfo(Media, 'bitrate', 'N/A')
							# Width
							myRow['Width'] = GetMoviePartInfo(Media, 'width', 'N/A')
							# Height
							myRow['Height'] = GetMoviePartInfo(Media, 'height', 'N/A')
							# AspectRatio
							myRow['Aspect Ratio'] = GetMoviePartInfo(Media, 'aspectRatio', 'N/A')
							# AudioChannels
							myRow['Audio Channels'] = GetMoviePartInfo(Media, 'audioChannels', 'N/A')
							# AudioCodec
							myRow['Audio Codec'] = GetMoviePartInfo(Media, 'audioCodec', 'N/A')
							# VideoCodec
							myRow['Video Codec'] = GetMoviePartInfo(Media, 'videoCodec', 'N/A')
							# Container
							myRow['Container'] = GetMoviePartInfo(Media, 'container', 'N/A')
							# VideoFrameRate
							myRow['Video FrameRate'] = GetMoviePartInfo(Media, 'videoFrameRate', 'N/A')
							# Get the Locked fields
							Fields = Media.xpath('//Field/@name')
							if not Fields:
								Fields = ['']
							Field = ''
							for myField in Fields:
								if Field == '':
									Field = myField
								else:
									Field = Field + mySepChar + myField
							Field = WrapStr(Field)
							myRow['Locked fields'] = Field.encode('utf8')
							# Got extras?
							Extras = Media.xpath('//Extras/@size')
							if not Extras[0]:
								Extra = '0'
							else:
								Extra = Extras[0]
							Extra = WrapStr(Extra)
							myRow['Extras'] = Extra.encode('utf8')
						# Everything is gathered, so let's write the row if needed
						if Prefs['TV_Level'] not in ['Extreme']:
							csvwriter.writerow(myRow)
						else:
# Extreme level and above
							parts = Media.xpath('//Part')
							if len(parts)>1:
								csvwriter.writerow(myRow)
								myRow = {}							
							for part in parts:
								# File Name of this Part
								myRow['Part File'] = GetMoviePartInfo(part, 'file', 'N/A')
								# File size of this part
								myRow['Part Size'] = GetMoviePartInfo(part, 'size', 'N/A')
								# Is This part Indexed
								myRow['Part Indexed'] = GetMoviePartInfo(part, 'indexes', 'N/A')
								# Part Container
								myRow['Part Container'] = GetMoviePartInfo(part, 'container', 'N/A')
								# Part Duration
								partDuration = ConvertTimeStamp(GetMoviePartInfo(part, 'duration', '0'))
								myRow['Part Duration'] = partDuration.encode('utf8')								
								csvwriter.writerow(myRow)
						# Extreme ended
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, GetRegInfo(myMedia, 'grandparentTitle') + '-' + GetRegInfo(myMedia, 'title')))
		return
#	except:
#		Log.Critical("Detected an exception in scanShowDB")
#		bScanStatus = 99
#		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanShowDB ***********")

####################################################################################################
# This function will return a string in hh:mm from a millisecond timestamp
####################################################################################################
@route(PREFIX + '/ConvertTimeStamp')
def ConvertTimeStamp(timeStamp):
	seconds=str(int(timeStamp)/(1000)%60)
	if len(seconds)<2:
		seconds = '0' + seconds
	minutes=str((int(timeStamp)/(1000*60))%60)
	if len(minutes)<2:
		minutes = '0' + minutes
	hours=str((int(timeStamp)/(1000*60*60))%24)
	return hours + ':' + minutes + ':' + seconds

####################################################################################################
# This function will return the header for the CSV file for Music
####################################################################################################
@route(PREFIX + '/getMusicHeader')
def getMusicHeader():
	# Simple fields
	fieldnames = ('Media ID',
			'Artist', 
			'Album',
			'Title',
			)
	# Basic fields
	if (Prefs['Artist_Level'] in ['Basic','Extended','Extreme', 'Extreme2']):
		fieldnames = fieldnames + (
			'Artist Summery',
			'Track No',
			'Duration',
			'Added',
			'Updated',
			)
	return fieldnames

####################################################################################################
# This function will replace CRLF, CR and LF from a string with a space
####################################################################################################
@route(PREFIX + '/fixCRLF')
def fixCRLF(myString):
	myString = myString.decode('utf-8').replace('\r\n', ' ')
	myString = myString.decode('utf-8').replace('\n', ' ')
	myString = myString.decode('utf-8').replace('\r', ' ')
	return myString

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
		csvwriter = csv.DictWriter(csvfile, fieldnames=getMusicHeader())
		csvwriter.writeheader()
		for myMedia in myMedias:
			bScanStatusCount += 1
			ratingKey = myMedia.get("ratingKey")
			myURL = "http://127.0.0.1:32400/library/metadata/" + ratingKey + "/allLeaves"
			Log.Debug("Album %s of %s with a RatingKey of %s at myURL: %s" %(bScanStatusCount, bScanStatusCountOf, ratingKey, myURL))


			#TODO Switch away from framework here
			myMedias2 = XML.ElementFromURL(myURL, headers=MYHEADER).xpath('//Track')			

			for myMedia2 in myMedias2:
# Simple and above
				myRow = {}
				# Get episode rating key
				myRow['Media ID'] = GetRegInfo(myMedia2, 'ratingKey')
				# Get Track title
				myRow['Title'] = GetRegInfo(myMedia2, 'title')	
				# Get Artist
				myRow['Artist'] = GetRegInfo(myMedia, 'title')	
				# Get Album
				myRow['Album'] = GetRegInfo(myMedia2, 'parentTitle')								
				# And now for Basic Export
				if Prefs['Artist_Level'] not in ['Basic','Extended','Extreme']:
					csvwriter.writerow(myRow)
				else:
# Basic and above
					myRow['Artist Summery'] = GetRegInfo(myMedia, 'summary')
					myRow['Track No'] = GetRegInfo(myMedia2, 'index')
					myRow['Duration'] = ConvertTimeStamp(GetRegInfo(myMedia2, 'duration', '0'))
					myRow['Added'] = (Datetime.FromTimestamp(float(GetRegInfo(myMedia2, 'addedAt', '0')))).strftime('%m/%d/%Y')
					myRow['Updated'] = (Datetime.FromTimestamp(float(GetRegInfo(myMedia2, 'updatedAt', '0')))).strftime('%m/%d/%Y')



					csvwriter.writerow(myRow)






				
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, GetRegInfo(myMedia, 'title') + '-' + GetRegInfo(myMedia2, 'parentTitle')))
		return
	except:
		Log.Critical("Detected an exception in scanArtistDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
	Log.Debug("******* Ending scanArtistDB ***********")



	

