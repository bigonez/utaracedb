#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests, re, json, os, time
import sqlite3

intervalTime = 10
hrefRoot = "https://www.multisportaustralia.com.au"

CategoryList = [
	"18-24",
	"25-29",
	"30-34",
	"35-39",
	"40-44",
	"45-49",
	"50-54",
	"55-59",
	"60-64",
	"65-69",
	"70-74",
	"75+"
]
GenderList = [
	"Male",
	"Female"
]
LocationList = [
	"Start",
	"Scenic World",
	"Furber Pass",
	"Golden Stairs",
	"Duncan Pass",
	"Foggy Knob Arrive",
	"Foggy Knob Depart",
	"IronPot",
	"Six Ft Track Arrive",
	"Six Ft Track Depart",
	"Aquatic Centre Arrive",
	"Aquatic Centre Depart",
	"Fairmount Arrive",
	"Fairmount Depart",
	"QVH Arrive",
	"QVH Depart",
	"TWM",
	"Furber Stairs",
	"BoardWalk",
	"Finish"
]

def cleanPreviousResultData(utaDb):
	pCur = utaDb.cursor()

	pCur.execute( "begin transaction;" )
	pCur.execute( "delete from uta100_athlete;" )									# clean the table of athlete
	pCur.execute( "delete from sqlite_sequence where name='uta100_athlete';" )		# reset the auto increment field
	pCur.execute( "delete from uta100_raceresult;" )								# clean the table of race result
	pCur.execute( "delete from sqlite_sequence where name='uta100_raceresult';" )	# reset the auto increment field
	pCur.execute( "commit transaction;" )

	pCur.close()
	utaDb.commit()

def grabOverAll(utaDb, overallUrl):
	athleteQuery = "INSERT INTO uta100_athlete VALUES(NULL{})"

	# grab the all overall page
	curPage = 0
	totalAthletes = 0
	pCur = utaDb.cursor()
	while overallUrl:
		curPage += 1
		print(" Overall Page {} ... ".format(curPage), end='', flush=True)

		# fetch the overall page
		response = requests.get(overallUrl)
		html_doc = response.text

		# initial the parsing tree
		overallSoup = BeautifulSoup(html_doc, 'lxml')

		# find the athlete list
		articleContainerTitle = overallSoup.find("tbody")

		# deal with each row in the page
		overallRecords = articleContainerTitle.find_all("tr")
		pageAthletes = len(overallRecords)
		totalAthletes += pageAthletes
		print("\b\b\b\b\b, {}, {}".format(pageAthletes, totalAthletes))

		for overallRecord in overallRecords:
			overallFields = overallRecord.find_all("td")
			# column 1: Position & Status
			tpos = overallFields[0].text
			if tpos.isnumeric():
				fstatus = 1
				ftpos = int(tpos)
			elif tpos == 'DNF':
				fstatus = 2
				ftpos= None
			elif tpos == 'NYS':
				fstatus = 3
				ftpos= None
			else:
				fstatus = 0
				ftpos= None
			# column 2, Name, BIB & Link to Individual Page
			fhref = hrefRoot + overallFields[1].find("a").get('href')
			name_bib = overallFields[1].text.replace('(','').replace(')','').split('#')
			fname, fbib = name_bib[0].strip(), int(name_bib[1])
			# column 3: Race Time
			fracetime = overallFields[2].text.strip()
			fracestamp = HmsToSeconds(fracetime)
			if len(fracetime) == 0:
				fracetime = None
			# column 4: Category & Position
			category_pos = overallFields[3].text.replace(')','').replace('\n','').split('(')
			fcategory = CategoryList.index(category_pos[0]) + 1
			if len(category_pos) == 2:
				fcpos = int(category_pos[1])
			else:
				fcpos = None
			# column 5: Gender & Position
			fgender = GenderList.index(overallFields[4].find('a').text) + 1
			has_gpos = overallFields[4].find('span')
			if has_gpos:
				fgpos = int(overallFields[4].find('span').text[1:-1])
			else:
				fgpos = None

			# form the dataset of one athlete
			athleteData = [
				fname,
				fbib,
				fcategory,
				fgender,
				fracetime,
				fracestamp,
				ftpos,
				fcpos,
				fgpos,
				fstatus,
				fhref
			]

			# store into the database
			pCur.execute( athleteQuery.format(", ?"*len(athleteData)), athleteData )
			pid = pCur.lastrowid

			overallRow = (pid, fbib, fname, fstatus, fhref)
			yield overallRow, curPage

		# commit the changes on database
		utaDb.commit()

		# find the URL to the next page
		paginationBlock = overallSoup.find("ul", {"class": "pagination"})
		navigateBtns = paginationBlock.find_all("a")
		if len(navigateBtns) == 1:
			navigateBtn = navigateBtns[0]
		elif len(navigateBtns) == 2:
			navigateBtn = navigateBtns[1]
		else:
			navigateBtn = None

		if navigateBtn and navigateBtn.text.find('Next') >= 0:
			# get the href attribute as the URL of the next page
			overallUrl = navigateBtn.get("href")
		else:
			# no more overall page
			overallUrl = None

	pCur.close()

def grabIndividual(utaDb, overallRow):
	raceResultQuery = "INSERT INTO uta100_raceresult VALUES(NULL{})"
	pCur = utaDb.cursor()

	pid, fbib, fname, fstatus, fhref = overallRow
	print("  {}, #{}, {}, {} ... ".format(pid, fbib, fname, fstatus), end='', flush=True)

	# fetch the individual page
	response = requests.get(fhref)
	html_doc = response.text

	# initial the parsing tree
	overallSoup = BeautifulSoup(html_doc, 'lxml')

	# find the race log
	articleContainerTitle = overallSoup.find("tbody")

	# deal with each row in the page
	pageLogs = 0
	lastTodStamp = 0
	logRecords = articleContainerTitle.find_all("tr")
	for logRecord in logRecords:
		logFields = logRecord.find_all("td")

		# column 1: Location
		locationName = logFields[0].text.strip()
		flocation = LocationList.index(locationName) + 1
		# column 2: split time
		fsplittime = logFields[1].text.strip()
		# column 3: race time
		fracetime = logFields[2].text.strip()
		# column 4: Total Position
		ftpos = asIntField(logFields[3].text.strip())
		# column 5: Gender Position
		fgpos = asIntField(logFields[4].text.strip())
		# column 6: Category Position
		fcpos = asIntField(logFields[5].text.strip())
		# column 7: Speed & Pace
		speedStr, paceStr = logFields[6].text.split('/')
		fspeed, fpace = asFloatField(speedStr.strip()), asPaceField(paceStr.strip())
		# column 8: Location
		ftod = logFields[7].text.strip()
		ftodstamp = HmsToSeconds(ftod)
		if (ftodstamp + 43200) < lastTodStamp:
			ftodstamp += 86400
		lastTodStamp = ftodstamp

		# form the dataset of one race result log
		raceResultData = [
			pid,
			fbib,
			flocation,
			fsplittime,
			HmsToSeconds(fsplittime),
			fracetime,
			HmsToSeconds(fracetime),
			ftpos,
			fcpos,
			fgpos,
			fspeed,
			fpace,
			ftod,
			ftodstamp
		]

		# store into the database
		pCur.execute( raceResultQuery.format(", ?"*len(raceResultData)), raceResultData )

		pageLogs += 1

	# commit the changes on database
	pCur.close()
	utaDb.commit()

	print("\b\b\b\b\b, {} ".format(pageLogs))

def sleepAnimation(itime):
	print('>', end='', flush=True)
	time.sleep(1)
	for i in range(itime-1):
		print("\b ", end='>', flush=True)
		time.sleep(1)
	print("\b "+"\b"*(i+2), end='', flush=True)

def asIntField(s):
	if s.isnumeric():
		return int(s)
	else:
		return None

def asFloatField(s):
	try:
		return float(s)
	except:
		return None

def asPaceField(s):
	if re.search("^\d+:\d+$", s):
		return s
	else:
		return None

def HmsToSeconds(timestr):
	hms = re.search("^(\d+):(\d+):(\d+)$", timestr)
	if hms:
		h, m, s = int(hms.group(1)), int(hms.group(2)), int(hms.group(3))
		return h * 3600 + m * 60 + s
	else:
		return None

def main():

	# intital the SQLite3 database
	utaDbName = "uta100_2023.db3"
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
		cleanPreviousResultData(utaDb)
	else:
		utaDb = None

	# grab the overall information for the offical race result web site
	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Race Result', 'UTA100 2023', '-'*50))
	overallUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1"

	totalPages = 0
	totalAthletes = 0
	totalStatus = [0, 0, 0]
	for overallRow, curPage in grabOverAll(utaDb, overallUrl):
		rowStatus = overallRow[3]
		if rowStatus in [1, 2]:
			# grab the individual race result for finished & DNF only
			grabIndividual(utaDb, overallRow)

			# display the waiting animation
			sleepAnimation(intervalTime)

		# update the stats
		totalPages = curPage
		totalAthletes += 1
		rowStatus = overallRow[3]
		if rowStatus > 0:
			totalStatus[rowStatus - 1] += 1

	# close the database connection
	if utaDb:
		utaDb.close()

	# display the summary information
	print("{}\n  {:>20}: {}\n  {:>20}: {}\n  {:>20}: {}\n  {:>20}: {}\n  {:>20}: {}\n{}".format(
		'-'*50,
		'Total Overall Pages', totalPages,
		'Total Athletes', totalAthletes,
		'Finished', totalStatus[0],
		'DNF', totalStatus[1],
		'NYS', totalStatus[2],
		'='*50
	))

if __name__ == '__main__':
	main()
