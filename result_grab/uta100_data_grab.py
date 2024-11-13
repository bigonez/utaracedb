#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests, re, json, os, time, datetime
import sqlite3

intervalTime = 7
awaitTime = 300
pageRows = 50
hrefRoot = "https://www.multisportaustralia.com.au"
entryUrl = hrefRoot + "/races/ultra-trail-australia-2024/events/1"
utaDbName = "./uta100_2024.db3"

CategoryList = [
	"18-19",
	"20-34",
	"35-39",
	"40-44",
	"45-49",
	"50-54",
	"55-59",
	"60-64",
	"65-69",
	"70-74",
	"75-79"
]
GenderList = [
	"Male",
	"Female"
]
LocationList = [
	"Start",
	"Narrow Neck",
	"Medow Gap",
	"Foggy Knob Arrive",
	"Foggy Knob Depart",
	"Six Ft Track Arrive",
	"Six Ft Track Depart",
	"Aquatic Centre Arrive",
	"Aquatic Centre Depart",
	"Gordon Falls",
	"Fairmount Arrive",
	"Fairmount Depart",
	"QVH Arrive",
	"QVH Depart",
	"EAS",
	"Echo Point",
	"BoardWalk",
	"Finish"
]

def cleanPreviousResultData(utaDb):
	pCur = utaDb.cursor()

	pCur.execute( "begin transaction;" )
	pCur.execute( "delete from uta100_athlete;" )								# clean the table of athlete
	pCur.execute( "delete from sqlite_sequence where name='uta100_athlete';" )	# reset the auto increment field
	pCur.execute( "delete from uta100_racelog;" )								# clean the table of race result
	pCur.execute( "delete from sqlite_sequence where name='uta100_racelog';" )	# reset the auto increment field
	pCur.execute( "commit transaction;" )

	pCur.close()
	utaDb.commit()

def getPreviousInfo(hk100Db):
	try:
		pCur = hk100Db.cursor()
		pRes = pCur.execute( "SELECT max(id) AS pid FROM uta100_athlete" )
		lastPid = pRes.fetchone()[0]
		if lastPid is None :
			lastPid = 0

		pRes = pCur.execute("SELECT sl.id AS status, IFNULL(st.st, 0) AS st FROM uta100_status AS sl \
				LEFT JOIN (SELECT status, count(id) AS st FROM uta100_athlete GROUP BY status) AS st \
				ON sl.id = st.status ORDER BY sl.id ASC")
		statusList = []
		for slRec in pRes.fetchall():
			statusList.append(int(slRec[1]))

		pCur.close()
	except:
		lastPid = 0

	return lastPid, statusList

def grabOverAll(utaDb, overallUrl, skipAhead):
	athleteQuery = "INSERT INTO uta100_athlete VALUES(NULL{})"

	# grab the all overall page
	pCur = utaDb.cursor()
	while overallUrl:
		curPage = fetchOverallPage(overallUrl)
		print(" Overall Page {} ... ".format(curPage), end='', flush=True)

		# fetch the overall page
		while True:
			try:
				response = requests.get(overallUrl)
				break
			except:
				print("\n\t!!! Connection refused by the server, sleep {} seconds then try again !!!\n".format(awaitTime))
				time.sleep(awaitTime)
				continue
		html_doc = response.text

		# initial the parsing tree
		overallSoup = BeautifulSoup(html_doc, 'lxml')

		# find the athlete list
		articleContainerTitle = overallSoup.find("tbody")

		# deal with each row in the page
		totalAthletes = pageRows * (curPage - 1) + skipAhead
		overallRecords = articleContainerTitle.find_all("tr")
		if skipAhead > 0:
			for i in range(skipAhead):
				overallRecords.pop(0)
			skipAhead = 0
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
			elif tpos == 'DNS':
				fstatus = 3
				ftpos= None
			else:
				fstatus = 0
				ftpos= None
			# column 2, Name, BIB & Link to Individual Page
			fhref = hrefRoot + overallFields[1].find("a").get('href')
			name_bib = overallFields[1].text.replace('(','').replace(')','').split('#')
			fname = name_bib[0].strip()
			if name_bib[1].strip() != '':
				fbib = int(name_bib[1].strip())
			else:
				fbib = ''
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
	pid, fbib, fname, fstatus, fhref = overallRow
	print(" . {}, #{}, {}, {} ... ".format(pid, fbib, fname, fstatus), end='', flush=True)
	if fstatus not in [1, 2]:
		# status not be Finished or DNF
		print("\b\b\b\b\b, 0 ")
		return

	raceLogQuery = "INSERT INTO uta100_racelog VALUES(NULL{})"
	pCur = utaDb.cursor()

	# fetch the individual page
	while True:
		try:
			response = requests.get(fhref)
			break
		except:
			print("\n\t!!! Connection refused by the server, sleep {} seconds then try again !!!\n".format(awaitTime))
			time.sleep(awaitTime)
			continue
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
		# column 8: Time of Day
		ftod = logFields[7].text.strip()
		ftodstamp = HmsToSeconds(ftod)
		if (ftodstamp + 43200) < lastTodStamp:
			ftodstamp += 86400
		lastTodStamp = ftodstamp

		# form the dataset of one race result log
		raceLogData = [
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
		pCur.execute( raceLogQuery.format(", ?"*len(raceLogData)), raceLogData )

		pageLogs += 1

	# commit the changes on database
	pCur.close()
	utaDb.commit()

	print("\b\b\b\b\b, {} ".format(pageLogs))

	# display the waiting animation
	sleepAnimation(intervalTime)

def sleepAnimation(itime):
	print('>', end='', flush=True)
	time.sleep(1)
	for i in range(itime-1):
		print("\b ", end='>', flush=True)
		time.sleep(1)
	print("\b "+"\b"*(i+2), end='', flush=True)

def fetchOverallPage(overallUrl):
	match = re.search(r"\?page=(\d*)$", overallUrl)
	if match:
		return int(match.group(1))
	else:
		return 1

def asIntField(s):
	if s.isnumeric():
		return int(s)
	else:
		return None

def asFloatField(s):
	match = re.search(r"^(\d*\.\d*)$", s)
	if match:
		return float(match.group(1))
	else:
		return asIntField(s)

def asPaceField(s):
	if re.search(r"^\d+:\d+$", s):
		return s
	else:
		return None

def HmsToSeconds(timestr):
	hms = re.search(r"^(\d+):(\d+):(\d+)$", timestr)
	if hms:
		h, m, s = int(hms.group(1)), int(hms.group(2)), int(hms.group(3))
		return h * 3600 + m * 60 + s
	else:
		return None

def strTimeDelta(td, digits):
	if td.days > 0: prefix = "{} days, ".format(td.days)
	else:           prefix = ""

	if digits < 0:  digits = 0
	if digits > 6:  digits = 6
	if digits > 0:  sw = 3 + digits
	else:           sw = 2

	hours   = td.seconds // 3600
	minutes = (td.seconds - hours * 3600) // 60
	seconds = round(td.total_seconds() % 60, digits)

	return prefix + "{:d}:{:02d}:{:0{}.{}f}".format(hours, minutes, seconds, sw, digits)

def main(entryUrl, utaDbName):

	# intital the SQLite3 database
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
		#-- cleanPreviousResultData(utaDb)
		lastPid, statusList = getPreviousInfo(utaDb)
	else:
		utaDb = None
		print("\t!!! The database, {}, is missing. !!!".format(utaDbName))
		return

	# grab the overall information for the offical race result web site
	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Race Result', 'UTA100 2024', '-'*50))

	overallUrl = entryUrl
	if lastPid > 0:
		overallUrl += "?page={}".format(lastPid // pageRows + 1)

	totalPages = lastPid // pageRows + 1
	totalAthletes = lastPid
	totalStatus = statusList
	lastPage = 0
	for overallRow, curPage in grabOverAll(utaDb, overallUrl, lastPid % pageRows):
		if curPage != lastPage:
			lastPage = curPage
			# display the waiting animation
			sleepAnimation(intervalTime)

		# grab the individual race result for finished & DNF only
		grabIndividual(utaDb, overallRow)

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
		'DNS', totalStatus[2],
		'='*50
	))

if __name__ == '__main__':
	startTime = time.time()

	main(entryUrl, utaDbName)

	finishTime = time.time()
	processTime = datetime.timedelta(seconds=(finishTime - startTime))

	print(" Total Processing Time: {}".format(strTimeDelta(processTime, 2)))
