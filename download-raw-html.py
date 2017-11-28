from lxml import html
import requests
import tal_util as tal
from datetime import date, time, timedelta
import csv
import glob
from bs4 import BeautifulSoup


URL_TRANSCRIPT_FORMAT = 'https://www.thisamericanlife.org/radio-archives/episode/{}/transcript'
RAW_DATA_FILENAME_FORMAT = 'raw-html/episode_{}.html'

# Download raw-html for each of the target episodes and returns a list of paths to those episodes
def downloadEpisodes(epNums, urlFormat, outputPathFormat):
    result = []
    for i in epNums:
        url = urlFormat.format(i)
        outputPath = outputPathFormat.format(i)

        print "  Downloading Data From: {}".format(url)
        print "  Writing Data To: {}".format(outputPath)

        html = requests.get(url)
        outputFile = open(outputPath, 'w')
        outputFile.write(html.content)
        outputFile.close()

        result.append(outputPath)
    return result

# Run
print "\n\n----------"
print "\n\nDownloading Raw HTML"

# Figure out how many episodes we already have in the raw data set
epCount = tal.getCurrentEpisodeCount("raw-html/")
print "Current Episode Count: {}".format(epCount)

# Figure out which episodes we must be missing from the raw data set, up to a specific theoretical maximum
missingEps = tal.identifyMissingEpisodes(epCount, RAW_DATA_FILENAME_FORMAT)
print "Missing Episodes: {}".format(missingEps)

# Download raw-html for any episodes we must be missing
downloadedEps = downloadEpisodes(missingEps, URL_TRANSCRIPT_FORMAT, RAW_DATA_FILENAME_FORMAT)
print "Downloaded Episodes: {}".format(downloadedEps)

