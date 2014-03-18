####################################################################################################
#	This plugin will create a list of medias in a section of Plex as a csv file
#
#	Made by dane22....A Plex Community member
#	
####################################################################################################

import os
import unicodedata
import string
import urllib
import time
import fnmatch
import io
import itertools

VERSION = ' V0.3.0.1'
NAME = 'Plex2csv'
ART = 'art-default.jpg'
ICON = 'icon-Plex2csv.png'
PREFIX = '/applications/Plex2csv'


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
	ValidatePrefs()
#	logPrefs()

####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
@route(PREFIX + '/MainMenu')
def MainMenu(random=0):
	Log.Debug("**********  Starting MainMenu  **********")
	oc = ObjectContainer()
	try:
		sections = XML.ElementFromURL('http://127.0.0.1:32400/library/sections/').xpath('//Directory')
		for section in sections:
			sectiontype = section.get('type')
			if sectiontype != "photo":
				title = section.get('title')
				key = section.get('key')
				Log.Debug('Title of section is %s with a key of %s' %(title, key))
				oc.add(DirectoryObject(key=Callback(DoExport, title=title, key=key), title='Export from section "' + title + '"', summary='Export media in section "' + title + '"'))
	except:
		Log.Critical("Exception happened in MainMenu")
		raise
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))
	Log.Debug("**********  Ending MainMenu  **********")
	return oc

####################################################################################################
# Called by the framework every time a user changes the prefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
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
				return ObjectContainer(header=NAME, message='Output directory created')
			else:
				return ObjectContainer(header=NAME, message='Output directory verified')
		else:
			raise Exception("Wrong path")
	except:
		Log.Critical('Bad export path')
		print 'Bad export path'
		return ObjectContainer(header=NAME, message="Wrong path specified for output!!!!!")
		

####################################################################################################
# Do the export
####################################################################################################
@route(PREFIX + '/DoExport')
def DoExport(title, key):
	Log.Debug("*******  Starting DoExport  ***********")
	if not os.path.exists(Prefs['Export_Path']):
#		oc.add(PopupDirectoryObject(title=title, summary='ged'))

		return ObjectContainer(header="Unsupported Appstore", message="Update check complete.")

	


