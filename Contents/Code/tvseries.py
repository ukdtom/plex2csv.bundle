####################################################################################################
#	Helper file for Plex2CSV
# This one handles TV-Shows
####################################################################################################

####################################################################################################
# This function will return the header for the CSV file for TV-Shows
####################################################################################################
def getTVHeader(PrefsLevel):
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
	if (PrefsLevel in ['Basic','Extended','Extreme', 'Extreme 2']):
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
	if PrefsLevel in ['Extended','Extreme', 'Extreme 2']:
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
			'Extras',
			'Audio Languages',
			'Subtitle Languages'
			)
	# Extreme fields
	if PrefsLevel in ['Extreme', 'Extreme 2']:
		fieldnames = fieldnames + (			
			'Part Duration',
			'Part File',
			'Part Size',
			'Part Indexed',
			'Part Container'			
			)
	# Extreme 2 fields
	if PrefsLevel in ['Extreme 2']:
		fieldnames = fieldnames + (			
			'PMS Media Path',
			''
			)
	return fieldnames

