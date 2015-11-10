####################################################################################################
#	Helper file for Plex2CSV
# Written by dane22 on the Plex Forums, UKDTOM on GitHub
#
# This one contains the valid fields and attributes for movies
# 
# To disable a field not needed, simply put a # sign in front of the line, and it'll be ommited.
# After above, a PMS restart is sadly req. though
# Note though, that this will be overwritten, if/when this plugin is updated
####################################################################################################

# Fields that contains a timestamp
dateTimeFields = ['addedAt', 'updatedAt', 'lastViewedAt', 'duration']

timeFields =['Media/Part/@duration']

# Define rows and element name for level 1 (Single call)
Level_1 = [
	('Media ID' , '@ratingKey'),
	('Title' , '@title'),
	('Sort title' , '@titleSort'),
	('Studio' , '@studio'),
	('Content Rating' , '@contentRating'),
	('Year' , '@year'),
	('Rating' , '@rating'),
	('Summary' , '@summary'),
	('Genres' , 'Genre/@tag')
]	

# Define rows and element name for level 2 (Single Call)
Level_2 = [
	('View Count' , '@viewCount'),
	('Last Viewed at' , '@lastViewedAt'),
	('Tagline' , '@tagline'),
	('Release Date' , '@originallyAvailableAt'),
	('Writers' , 'Writer/@tag'),
	('Country' , 'Country/@tag'),
	('Duration' , '@duration'),
	('Directors' , 'Director/@tag'),
	('Roles' , 'Role/@tag'),
	('IMDB Id' , '@guid')
	]

# Define rows and element name for level 3 (One call pr. movie)
Level_3 = [
	('Labels' , 'Label/@tag'),
	('Locked Fields' , 'Field/@name'),
	('Extras' , 'Extras/@size'),
	('Collections' , 'Collection/@tag'),
	('Original Title' , '@originalTitle'),
	('Added' , '@addedAt'),	
	('Updated' , '@updatedAt'),
	('Audio Languages' , 'Media/Part/Stream[@streamType=2]/@languageCode'),	
	('Audio Title' , 'Media/Part/Stream[@streamType=2]/@title'),
	('Subtitle Languages' , 'Media/Part/Stream[@streamType=3]/@languageCode'),
	('Subtitle Title' , 'Media/Part/Stream[@streamType=3]/@title'),
	('Subtitle Codec' , 'Media/Part/Stream[@streamType=3]/@codec')
	]

# Define rows and element name for level 4 (One call pr. movie)
Level_4 = [
	('Video Resolution' , 'Media/@videoResolution'),
	('Bitrate' , 'Media/@bitrate'),
	('Width' , 'Media/@width'),
	('Height' , 'Media/@height'),
	('Aspect Ratio' , 'Media/@aspectRatio'),
	('Audio Channels' , 'Media/@audioChannels'),
	('Audio Codec' , 'Media/@audioCodec'),
	('Video Codec' , 'Media/@videoCodec'),
	('Container' , 'Media/@container'),
	('Video FrameRate' , 'Media/@videoFrameRate')
	]

# Define rows and element name for level 5 (Part info) (One call pr. movie)
Level_5 = [
	('Part File' , 'Media/Part/@file'),
	('Part Size' , 'Media/Part/@size'),
	('Part Indexed' , 'Media/Part/@indexes'),
	('Part Duration' , 'Media/Part/@duration'),
	('Part Container' , 'Media/Part/@container'),
	('Part Optimized for Streaming' , 'Media/Part/@optimizedForStreaming')
	]

# Define rows and element name for level 6 (Video Stream Info) (One call pr. movie)
Level_6 = [
	('Video Stream pixelFormat' , 'Media/Part/Stream[@streamType=1]/@pixelFormat'),
	('Video Stream profile' , 'Media/Part/Stream[@streamType=1]/@profile'),
	('Video Stream refFrames' , 'Media/Part/Stream[@streamType=1]/@refFrames'),
	('Video Stream scanType' , 'Media/Part/Stream[@streamType=1]/@scanType'),
	('Video Stream streamIdentifier' , 'Media/Part/Stream[@streamType=1]/@streamIdentifier'),
	('Video Stream width' , 'Media/Part/Stream[@streamType=1]/@width'),
	('Video Stream pixelAspectRatio' , 'Media/Part/Stream[@streamType=1]/@pixelAspectRatio'),
	('Video Stream height' , 'Media/Part/Stream[@streamType=1]/@height'),
	('Video Stream hasScalingMatrix' , 'Media/Part/Stream[@streamType=1]/@hasScalingMatrix'),
	('Video Stream frameRateMode' , 'Media/Part/Stream[@streamType=1]/@frameRateMode'),
	('Video Stream frameRate' , 'Media/Part/Stream[@streamType=1]/@frameRate'),
	('Video Stream codecID' , 'Media/Part/Stream[@streamType=1]/@codecID'),
	('Video Stream chromaSubsampling' , 'Media/Part/Stream[@streamType=1]/@chromaSubsampling'),
	('Video Stream cabac' , 'Media/Part/Stream[@streamType=1]/@cabac'),
	('Video Stream bitDepth' , 'Media/Part/Stream[@streamType=1]/@bitDepth'),
	('Video Stream anamorphic' , 'Media/Part/Stream[@streamType=1]/@anamorphic'),
	('Video Stream language Code' , 'Media/Part/Stream[@streamType=1]/@languageCode'),
	('Video Stream language' , 'Media/Part/Stream[@streamType=1]/@language'),
	('Video Stream bitrate' , 'Media/Part/Stream[@streamType=1]/@bitrate'),
	('Video Stream Codec' , 'Media/Part/Stream[@streamType=1]/@codec')
	]

# Define rows and element name for extreme level 7 (One call pr. movie)
Level_7 = [
	]

# Define rows and element name for extreme level 8 (One call pr. movie)
Level_8 = [
	]

# Define rows and element name for extreme level 9 (One call pr. movie)
Level_9 = {
	}

# Define rows and element name for level 666 (Two calls pr. movie)
Level_666 = [
	('PMS Media Path' , 'hash')
	]

