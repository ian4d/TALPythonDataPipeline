import os, os.path

# Count how many episodes we presume to have data for
def getCurrentEpisodeCount(filePath):
    print "\n\nGetting episode count in location {}".format(filePath)
    fileList = [name for name in os.listdir(filePath)]
    return len(fileList)

# Returns a list of missing episodes up to the provided count + 1
def identifyMissingEpisodes(epCount, fileNameFormat):
    result = []
    greatestEpisodeNumber = 0
    for i in xrange(1, epCount+1):
        filePath = fileNameFormat.format(i)
        if not (os.path.exists(filePath) and os.path.isfile(filePath)):
            result.append(i)
        else:
            greatestEpisodeNumber = max(i, greatestEpisodeNumber)
    result.append(greatestEpisodeNumber + 1)
    return result

# Encodes a row for output
def encodeForOutput(row):
    utf_row = []
    for entry in row:
        if isinstance(entry, (str, unicode)):
            utf_row.append(entry.encode('utf-8'))
        else:
            utf_row.append(entry)
    return utf_row