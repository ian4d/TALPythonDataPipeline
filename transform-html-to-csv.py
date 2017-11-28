from lxml import html
import requests
import os, os.path
import tal_util as tal
from datetime import date, time, timedelta
import csv
import glob
from bs4 import BeautifulSoup

debug = True

RAW_DATA_FILENAME_FORMAT = './raw-html/episode_{}.html'
CSV_DATA_FILENAME_FORMAT = './episode-csv/episode-{}.csv'

header = ["episode-number","episode-title","air-date","act-number","act-name","speaker-role","speaker-name","time-start","speaker-text"]


def generateFilePathsFromEpNumList(list):
    missingEpFilePaths = []
    for epNum in missingEps:
        filePath = RAW_DATA_FILENAME_FORMAT.format(epNum)
        missingEpFilePaths.append(filePath)
    return missingEpFilePaths


# Calls the parseRawHTML method on each of a list of files
def parseRawHTMLForAllFiles(fileList):
    for filePath in fileList:
        parseRawHTML(filePath)

# Parse the file at the provided path
def parseRawHTML(filePath):
    # Prepare CSV data store
    data = []
    
    # Container for all data
    wrapper = extractCoreContent(filePath)
    if not wrapper:
        return

    # meta block
    meta = extractMetadataFromWrapper(wrapper)

    # Episode Number, title, air_date
    episode_num = extractEpisodeNumber(meta)
    episode_title = extractEpisodeTitle(meta)
    air_date = extractAirDate(meta)

    # Parse all acts
    for parsed_act in parseAllActs(wrapper):
        parsed_act = [episode_num, episode_title, air_date] + parsed_act
        parsed_act = tal.encodeForOutput(parsed_act)
        data.append(parsed_act)

    # Write output, do something with data   
    outputPath = generateOutputPath(episode_num, CSV_DATA_FILENAME_FORMAT)
    writeOutput(data, outputPath)

# Writes output data
def writeOutput(data, outputPath):
    output_file = open(outputPath, 'w')
    csv_writer = csv.writer(output_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(header)
    for entry in data:
        csv_writer.writerow(entry)
    output_file.close()

def generateOutputPath(episode_num, fileNameFormat):
    return fileNameFormat.format(episode_num)

# Extracts the core page content from the file at filePath
def extractCoreContent(filePath):
    page = open(filePath)
    soup = BeautifulSoup(page, 'html.parser')
    page.close()

    # Container for all meta
    return soup.find('div', class_='radio-wrapper')

def extractMetadataFromWrapper(wrapper):
    return wrapper.find('div', class_='radio')

# Extracts the episode number from the provided meta info block
def extractEpisodeNumber(meta):
    return meta.find('div', class_='radio-episode-num').string.strip(':')

# Extracts the episode title from the provided meta block
def extractEpisodeTitle(meta):
    return meta.h2.a.string

# Extracts the air date from the provided meta block
def extractAirDate(meta):
    # Air Date
    air_date_string = meta.find('div',class_='radio-date').string.replace('Originally aired ','')
    air_date_components = air_date_string.split('.')
    air_date_month = int(air_date_components[0])
    air_date_day = int(air_date_components[1])
    air_date_year = int(air_date_components[2])
    air_date = date(month=air_date_month, day=air_date_day, year=air_date_year)
    return air_date


# Get act name
def extractActName(act):
    return act.h3.string.strip('.')

def extractAllSegmentsFromAct(act):
    # Iterate over list of components of act
    act_content = act.find('div',class_='act-inner')
    return act_content.find_all('div')

# Extract the speaker's role from a segment
def extractSpeakerRoleFromSegment(segment):
    return segment['class'][0]

# Extract the speaker's name from the segment
def extractSpeakerNameFromSegment(segment):
    speaker_name = segment.h4
    if speaker_name is None:
        speaker_name = 'Unspecified'
    else:
        speaker_name = speaker_name.text
    return speaker_name

# Extracts all parts from a segment
def extractAllPartsFromSegment(segment):
    return segment.find_all('p')

# Extracts the start time from a segment part
def extractStartTimeFromPart(part):
    return part['begin']

# Extracts the text from a segment part
def extractTextFromPart(part):
    return part.string

# Parse every act. Expects an html wrapper input, should return a row every part of every act
def parseAllActs(wrapper):
    results = []
    act_list = wrapper.find_all('div', class_='act')
    act_num = 0
    for act in act_list:
        act_num += 1
        act_segments = parseAct(act)
        for segment in act_segments:
            entry = [act_num] + segment
            results.append(entry)
    return results

# Parse a single act
def parseAct(act):
    act_name = extractActName(act)
    results = []
    for segment in extractAllSegmentsFromAct(act):
        segment_parts = parseSegment(segment)
        for part in segment_parts:
            entry = [act_name] + part
            results.append([act_name] + part)
    return results


# Parses a single segment for each of its parts
# Returns a list of partially completed rows
def parseSegment(segment):
    # Extract Speaker Role, Name, Parts
    speaker_role = extractSpeakerRoleFromSegment(segment)
    speaker_name = extractSpeakerNameFromSegment(segment)
    results = []
    for part in extractAllPartsFromSegment(segment):
        entry = [speaker_role, speaker_name] + parseSegmentPart(part)
        results.append(entry)
    return results

# Parse a single part of a segment
# Returns two components of a single entry
def parseSegmentPart(part):
    if part is None:
        return
    # Extract speech start time and speech text
    time_start = extractStartTimeFromPart(part)
    # Get the text
    segment_text = extractTextFromPart(part)
    result = [time_start, segment_text]
    return result


print "\n\n----------"
print "\n\nTransforming Raw HTML to CSV"

# Figure out how many episodes we already have
epCount = tal.getCurrentEpisodeCount("episode-csv/")
print "Current Episode Count: {}".format(epCount)

# Figure out which episodes we must be missing
missingEps = tal.identifyMissingEpisodes(epCount, CSV_DATA_FILENAME_FORMAT)
print "Missing Episodes: {}".format(missingEps)


missingEpFilePaths = generateFilePathsFromEpNumList(missingEps)
print "Missing Episode Paths: {}".format(missingEpFilePaths)

# Parse raw-html for each episode which is missing
parseRawHTMLForAllFiles(missingEpFilePaths)




    









