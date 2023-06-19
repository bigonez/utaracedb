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
	#--	pCur.execute( "delete from uta100_athlete;" )								# clean the table of athlete
	#--	pCur.execute( "delete from sqlite_sequence where name='uta100_athlete';" )	# reset the auto increment field
	pCur.execute( "delete from uta100_raceresult;" )								# clean the table of race result
	pCur.execute( "delete from sqlite_sequence where name='uta100_raceresult';" )	# reset the auto increment field
	pCur.execute( "commit transaction;" )

	pCur.close()
	utaDb.commit()

def grabOverAll(utaDb):
	overallUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1?page={}"
	totalPages = 23
	overallRange = range(1, totalPages + 1)
	athleteQuery = "INSERT INTO uta100_athlete VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

	# grab the all overall page
	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Overall List', 'UTA100 2023', '-'*50))
	totalAthletes = 0
	pCur = utaDb.cursor()
	for i in overallRange:
		print(" Page {} ... ".format(i), end='', flush=True)

		# fetch the overall page
		response = requests.get(overallUrl.format(i))
		html_doc = response.text

		# initial the parsing tree
		overallSoup = BeautifulSoup(html_doc, 'lxml')

		# find the athlete list
		articleContainerTitle = overallSoup.find("tbody")

		# deal with each row in the page
		pageAthletes = 0
		for overallRecord in articleContainerTitle.find_all("tr"):
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
				ftpos,
				fcpos,
				fgpos,
				fstatus,
				fhref
			]

			# store into the database
			pCur.execute( athleteQuery, athleteData )

			pageAthletes += 1

		# commit the changes on database
		utaDb.commit()

		totalAthletes += pageAthletes
		print("\b\b\b\b\b, {}, {}".format(pageAthletes, totalAthletes))

		if i < totalPages:
			sleepAnimation(intervalTime)

	pCur.close()
	print("{}\n Total Overall Pages: {}, Total Athletes: {}\n{}".format('-'*50, totalPages, totalAthletes, '='*50))

def grabIndividual(utaDb):
	individualUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1/results/individuals/{}"
	overallQuery = "SELECT uta100_athlete.id AS id, bib, name, uta100_athlete.status AS status, uta100_status.abbr AS abbr FROM uta100_athlete \
					LEFT JOIN uta100_status ON uta100_athlete.status = uta100_status.id WHERE uta100_athlete.status IN (1, 2) ORDER BY uta100_athlete.id"
	raceResultQuery = "INSERT INTO uta100_raceresult VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	pCur = utaDb.cursor()

	# fetch the overall list first
	pRes = pCur.execute(overallQuery)
	overallList = pRes.fetchall()

	# grab the all individual page
	print("\n{}\n  {:18}{:>28}\n{}".format('='*50, 'Individual', 'UTA100 2023', '-'*50))
	totalAthletes = 0
	###for pid, fbib, fname, fstatus, fabbr in overallList:
	###	print(" No.{}, #{}, {}, {} ... ".format(pid, fbib, fname, fstatus, fabbr), end='', flush=True)
	###
	###	# fetch the individual page
	###	response = requests.get(individualUrl.format(bib))
	###	html_doc = response.text
	individualFile = "uta100_2023_individual_496.html"
	pid, fbib, fname, fstatus, fabbr = (400, 496, 'Steve ONORATO', 1, 'Finished')
	print(" No.{}, #{}, {}, {} ... ".format(pid, fbib, fname, fabbr), end='', flush=True)
	with open(individualFile, "r") as f:
		html_doc = f.read()
		########################################################################

		# initial the parsing tree
		overallSoup = BeautifulSoup(html_doc, 'lxml')

		# find the race log
		articleContainerTitle = overallSoup.find("tbody")

		# deal with each row in the page
		pageLogs = 0
		for logRecord in articleContainerTitle.find_all("tr"):
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

			# form the dataset of one race result log
			raceResultData = [
				pid,
				fbib,
				flocation,
				fsplittime,
				fracetime,
				ftpos,
				fcpos,
				fgpos,
				fspeed,
				fpace,
				ftod
			]

			# store into the database
			pCur.execute( raceResultQuery, raceResultData )

			pageLogs += 1

		# commit the changes on database
		utaDb.commit()

		totalAthletes += 1
		print("\b\b\b\b\b, {}".format(pageLogs))

		if totalAthletes < len(overallList):
			sleepAnimation(intervalTime)

	pCur.close()
	print("{}\n Total Athletes: {}\n{}".format('-'*50, totalAthletes, '='*50))

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

def main():

	# intital the SQLite3 database
	utaDbName = "uta100_2023.db3"
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
		cleanPreviousResultData(utaDb)
	else:
		utaDb = None

	# grab the overall information
	#--	grabOverAll(utaDb)

	# grab the overall information
	grabIndividual(utaDb)

	# close the database connection
	if utaDb:
		utaDb.close()

if __name__ == '__main__':
	main()
