####################################################################################################
#	Helper file for Plex2CSV
# This one handles global constants
####################################################################################################

# APP specific stuff
VERSION = ' V0.0.4.14'
NAME = 'plex2csv'
DESCRIPTION = 'Export Plex libraries to CSV-Files'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PREFIX = '/applications/Plex2csv'
APPGUID = '7608cf36-742b-11e4-8b39-00089bd210b2'
PLAYLIST = 'playlist.png'

# How many items we ask for each time, when accessing a section or Show
CONTAINERSIZEMOVIES = 30
CONTAINERSIZETV = 10
CONTAINERSIZEEPISODES = 30
CONTAINERSIZEAUDIO = 10
CONTAINERSIZEPHOTO = 20

# For slow PMS HW, we might need to wait some time here
PMSTIMEOUT = 30
