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

VERSION = ' V0.0.0.13'
NAME = 'Plex2csv'
ART = 'art-default.jpg'
ICON = 'icon-Plex2csv.png'
PREFIX = '/applications/Plex2csv'


bScanStatus = 0			# Current status of the background scan
initialTimeOut = 3		# When starting a scan, how long in seconds to wait before displaying a status page. Needs to be at least 1.

####################################################################################################
# Start function
####################################################################################################
def Start():
	print("********  Started %s on %s  **********" %(NAME  + VERSION, Platform.OS))
	Log.Debug("*******  Started %s on %s  ***********" %(NAME  + VERSION, Platform.OS))
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME  + VERSION
	ObjectContainer.view_group = 'List'
	DirectoryObject.thumb = R(ICON)
	HTTP.CacheTime = 0

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
@route(PREFIX + '/MainMenu')
def MainMenu(random=0):
	Log.Debug("**********  Starting MainMenu  **********")
	oc = ObjectContainer()
	try:
		if ValidateExportPath():
			sections = XML.ElementFromURL('http://127.0.0.1:32400/library/sections/').xpath('//Directory')
			for section in sections:
				sectiontype = section.get('type')
				if sectiontype != "photo" and sectiontype != 'artist': # ToDo: Remove artist when code is in place for it.
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
			if not os.path.exists(os.path.join(myPath, 'Plex2CSV')):
				os.makedirs(os.path.join(myPath, 'Plex2CSV'))
				Log.Debug('Created directory named: %s' %(os.path.join(myPath, 'Plex2CSV')))
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
	# Dummy function to satisfy the framework
	return

####################################################################################################
# Export Complete.
####################################################################################################
@route(PREFIX + '/complete')
def complete(title=''):
	global bScanStatus
	Log.Debug("*******  All done, tell my Master  ***********")
	title = ('Export Completed for %s' %(title))
	message = 'Check the directory: %s' %(os.path.join(Prefs['Export_Path'], 'Plex2CSV')) 
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
	# Errors: 91=unknown section type, 99=Other Error
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
		summary = "The Plex client will only wait a few seconds for us to work, so we run it in the background. This requires you to keep checking on the status until it is complete. \n\n"
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
			oc2 = ObjectContainer(title1="Internal Error Detected. Please check the logs",no_history=True)
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="An internal error has occurred.", summary=summary))
			oc2.add(DirectoryObject(key=Callback(MainMenu, random=time.clock()), title="*** Please submit logs. ***", summary=summary))
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
		myCSVFile = os.path.join(Prefs['Export_Path'], 'Plex2CSV', title + '-' + timestr + '.csv')
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
	fieldnames = ('Media ID', 
			'Title',
			'Studio',
			'Content Rating',
			'Summary',
			'Rating',
			'Year',
			'Genres',
			)
	if (Prefs['Movie_Level'] in ['Basic','Extended','Extreme']):
		fieldnames = fieldnames + (
			'Tagline',
			'Release Date',
			'Writers',
			'Directors',
			'Roles',
			'Duration',
			)
	if Prefs['Movie_Level'] in ['Extended','Extreme']:
		fieldnames = fieldnames + (
			'Original Title',
			'Collections',
			'Added',
			'Updated',
			)
	if Prefs['Movie_Level'] in ['Extreme']:
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
			'Video FrameRate',
			# Part info
# ToDo
#			'File',
#			'size',
#			'indexes',
# ToDo end
			)

	return fieldnames

####################################################################################################
# This function will wrap a string if needed
####################################################################################################
@route(PREFIX + '/WrapStr')
def WrapStr(myStr):
	LineWrap = int(Prefs['Line_Length'])
	if Prefs['Line_Wrap']:		
		Log.Debug('Wrapped Output is: %s' %(fill(myStr, LineWrap)))
		return fill(myStr, LineWrap)
	else:
		return myStr

####################################################################################################
# This function will scan a movie section.
####################################################################################################
@route(PREFIX + '/scanMovieDB')
def scanMovieDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanMovieDB with an URL of %s***********" %(myMediaURL))
	Log.Debug('Movie Export level is %s' %(Prefs['Movie_Level']))
	global bScanStatusCount
	global bScanStatusCountOf
	bScanStatusCount = 0
	bScanStatusCountOf = 0
	try:
		mySepChar = ' - '
		myMedias = XML.ElementFromURL(myMediaURL).xpath('//Video')
		bScanStatusCountOf = len(myMedias)
		csvfile = io.open(myCSVFile,'wb')
		# Create output file, and print the header
		csvwriter = csv.DictWriter(csvfile, fieldnames=getMovieHeader())
		csvwriter.writeheader()
		for myMedia in myMedias:				
			myRow = {}
			# Add all for Simple Export
			# Get Media ID
			myRow['Media ID'] = GetRegInfo(myMedia, 'ratingKey')
			# Get Extended info if needed
			if Prefs['Movie_Level'] in ['Extended','Extreme']:
				myExtendedInfoURL = 'http://127.0.0.1:32400/library/metadata/' + GetRegInfo(myMedia, 'ratingKey')		
				ExtInfo = XML.ElementFromURL(myExtendedInfoURL).xpath('//Video')[0]
			# Get title
			myRow['Title'] = GetRegInfo(myMedia, 'title')
			# Get Studio
			myRow['Studio'] = GetRegInfo(myMedia, 'studio')
			# Get contentRating
			myRow['Content Rating'] = GetRegInfo(myMedia, 'contentRating')
			# Get Year
			myRow['Year'] = GetRegInfo(myMedia, 'year')
			# Get Rating
			myRow['Rating'] = GetRegInfo(myMedia, 'rating')
			# Get Summery
			myRow['Summary'] = GetRegInfo(myMedia, 'summary')
			# Get Genres
			if Prefs['Movie_Level'] in ['Extended','Extreme']:
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

			# And now for Basic Export
			if Prefs['Movie_Level'] in ['Basic','Extended','Extreme']:
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
				# Only if basic, and not Extended
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
				elif Prefs['Movie_Level'] in ['Extended','Extreme']:
					# Get Roles Extended
					myRoles = XML.ElementFromURL(myExtendedInfoURL).xpath('//Video//Role')
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
			# Here goes extended stuff, not part of basic or simple
			if Prefs['Movie_Level'] in ['Extended','Extreme']:
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
				addedAt = (Datetime.FromTimestamp(float(myMedia.get('addedAt')))).strftime('%m/%d/%Y')
				myRow['Added'] = addedAt.encode('utf8')
				# Get Updated at
				# If myMedia.get('updatedAt') has a value then change the time format else set it to blank.
				if myMedia.get('updatedAt'): updatedAt = (Datetime.FromTimestamp(float(myMedia.get('updatedAt')))).strftime('%m/%d/%Y')
				else: updatedAt = ""
				myRow['Updated'] = updatedAt.encode('utf8')
			if Prefs['Movie_Level'] == 'Extreme':
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
			# Everything is gathered, so let's write the row
			csvwriter.writerow(myRow)
			# Now for parts info, on a seperate row




# ToDo
#			if Prefs['Movie_Level'] == 'Extreme':

#				myRow = []
#				parts = ExtInfo.xpath('//part')
#				for part in parts:
#					File = part.get('file')
#					print File
				




#			'File',
#			'size',
#			'indexes',

# ToDo end
			bScanStatusCount += 1
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, GetRegInfo(myMedia, 'title')))
		return	
	except:
		Log.Critical("Detected an exception in scanMovieDB Extended")
		bScanStatus = 99
		raise	
	finally:
		Log.Debug("******* Ending scanMovieDB ***********")
		csvfile.close

####################################################################################################
# This function will return info from extended page for movies
####################################################################################################
@route(PREFIX + '/GetExtInfo')
def GetExtInfo(ExtInfo, myField):
	try:
		myLookUp = ExtInfo.xpath('Media/@' + myField)[0]
		if not myLookUp:
			myLookUp = ''
	except:
		myLookUp = ''
		Log.Debug('Failed to lookup field %s' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will return info from regular fields for a movies
####################################################################################################
@route(PREFIX + '/GetRegInfo')
def GetRegInfo(myMedia, myField, default = ''):
	try:
		myLookUp = myMedia.get(WrapStr(myField))
		if not myLookUp:
			myLookUp = WrapStr(default)
	except:
		myLookUp = WrapStr(default)
		Log.Debug('Failed to lookup field %s' %(myField))
	return myLookUp.encode('utf8')

####################################################################################################
# This function will scan a TV-Show section.
####################################################################################################
@route(PREFIX + '/scanShowDB')
def scanShowDB(myMediaURL, myCSVFile):
	Log.Debug("******* Starting scanShowDB with an URL of %s***********" %(myMediaURL))
	global bScanStatusCount
	global bScanStatusCountOf
	myMediaPaths = []
	bScanStatusCount = 0
	try:
		myMedias = XML.ElementFromURL(myMediaURL).xpath('//Directory')
		bScanStatusCountOf = len(myMedias)
		bScanStatusCountOf = len(myMedias)
		fieldnames = ('Media ID', 
				'Series Title',
				'Episode Title',
				'Year',
				'Season',
				'Episode',
				'Studio',
				'Content Rating',
				'Summary',
				'Rating',
				'Originally Aired',
				'Authors',
				'Genres',
				'Directors',
				'Roles',
				'Duration',
				'Added',
				'Updated')
		csvfile = io.open(myCSVFile,'wb')
		csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
		csvwriter.writeheader()
		for myMedia in myMedias:
			bScanStatusCount += 1
			ratingKey = myMedia.get("ratingKey")
			myURL = "http://127.0.0.1:32400/library/metadata/" + ratingKey + "/allLeaves"
			Log.Debug("Show %s of %s with a RatingKey of %s at myURL: %s" %(bScanStatusCount, bScanStatusCountOf, ratingKey, myURL))
			myMedias2 = XML.ElementFromURL(myURL).xpath('//Video')
			for myMedia2 in myMedias2:
				ratingKey = myMedia2.get('ratingKey')
				if not ratingKey:
					ratingKey = ''
				SerieTitle = myMedia2.get('grandparentTitle')
				if not SerieTitle:
					SerieTitle = ''
				EpisodeTitle = myMedia2.get("title")
				if not EpisodeTitle:
					EpisodeTitle = ''
				studio = myMedia2.get("studio")
				if not studio:
					studio = ''
				contentRating = myMedia2.get("contentRating")
				if not contentRating:
					contentRating = ''
				summary = myMedia2.get("summary")
				if not summary:
					summary = ''
				season = myMedia2.get("parentIndex")
				if not season:
					season = ''
				episode = myMedia2.get("index")
				if not episode:
					episode = ''
				rating = myMedia2.get("rating")
				if not rating:
					rating = ''
				year = myMedia2.get("year")
				if not year:
					year = ''
				originallyAvailableAt = myMedia2.get("originallyAvailableAt")
				if not originallyAvailableAt:
					originallyAvailableAt = ''
				# Get Authors
				Writer = myMedia2.xpath('Writer/@tag')
				if not Writer:
					Writer = ['']
				Author = ''
				for myWriter in Writer:
					if Author == '':
						Author = myWriter
					else:
						Author = Author + ' - ' + myWriter
				# Get Genres
				Genres = myMedia.xpath('Genre/@tag')
				if not Genres:
					Genres = ['']
				Genre = ''
				for myGenre in Genres:
					if Genre == '':
						Genre = myGenre
					else:
						Genre = Genre + ' - ' + myGenre
				# Get Directors
				Directors = myMedia2.xpath('Director/@tag')
				if not Directors:
					Directors = ['']
				Director = ''
				for myDirector in Directors:
					if Director == '':
						Director = myDirector
					else:
						Director = Director + ' - ' + myDirector
				# Get Roles
				Roles = myMedia.xpath('Role/@tag')
				if not Roles:
					Roles = ['']
				Role = ''
				for myRole in Roles:
					if Role == '':
						Role = myRole
					else:
						Role = Role + ' - ' + myRole
				# Get the duration of the movie
				duration = myMedia2.get('duration')
				if not duration:
					duration = '0'
				duration = ConvertTimeStamp(duration)
				addedAt = (Datetime.FromTimestamp(float(myMedia2.get('addedAt')))).strftime('%m/%d/%Y')
				# If myMedia.get('updatedAt') has a value then change the time format else set it to blank.
				if myMedia.get('updatedAt'): updatedAt = (Datetime.FromTimestamp(float(myMedia.get('updatedAt')))).strftime('%m/%d/%Y')
				else: updatedAt = ""
				csvwriter.writerow({'Media ID' : ratingKey.encode('utf8'),
					'Studio' : studio.encode('utf8'),
					'Roles' : Role.encode('utf8'),
					'Directors' : Director.encode('utf8'),
					'Genres' : Genre.encode('utf8'),
					'Originally Aired' : originallyAvailableAt.encode('utf8'),
					'Year' : year.encode('utf8'),
					'Authors' : Author.encode('utf8'),
					'Rating' : rating.encode('utf8'),
					'Season' : season.encode('utf8'),
					'Episode' : episode.encode('utf8'),
					'Summary' : summary.encode('utf8'),
					'Content Rating' : contentRating.encode('utf8'),
					'Series Title' : SerieTitle.encode('utf8'),
					'Episode Title' : EpisodeTitle.encode('utf8'),
					'Duration' : duration.encode('utf8'),
					'Added' : addedAt.encode('utf8'),
					'Updated' : updatedAt.encode('utf8')
					})
			Log.Debug("Media #%s from database: '%s'" %(bScanStatusCount, SerieTitle + '-' + EpisodeTitle))
		return
	except:
		Log.Critical("Detected an exception in scanShowDB")
		bScanStatus = 99
		raise # Dumps the error so you can see what the problem is
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

