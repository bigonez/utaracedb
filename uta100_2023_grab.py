#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests, re, json, os, time
import sqlite3

intervalTime = 5
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

def cleanPreviousResultData(utaDb):
	pCur = utaDb.cursor()

	pCur.execute( "begin transaction;" )
	pCur.execute( "delete from uta100_athlete;" )								# clean the table of athlete
	pCur.execute( "delete from sqlite_sequence where name='uta100_athlete';" )	# reset the auto increment field
	pCur.execute( "delete from uta100_result;" )								# clean the table of race result
	pCur.execute( "delete from sqlite_sequence where name='uta100_result';" )	# reset the auto increment field
	pCur.execute( "commit transaction;" )

	pCur.close()
	utaDb.commit()

def grabOverAll(utaDb):
	###overallUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1?page={}"
	overallRange = range(1, 24)
	athleteQuery = "INSERT INTO uta100_athlete VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

	# grab the all overall page
	###for i in overallRange:
		###response = requests.get(overallUrl.format(i))
		###html_doc = response.text
	overallFile = "uta100_2023_overall_17.html"
	with open(overallFile, "r") as f:
		pageAthletes = 0

		html_doc = f.read()
		overallSoup = BeautifulSoup(html_doc, 'lxml')
		articleContainerTitle = overallSoup.find("tbody")

		# deal with each row in the page
		for overallRecord in articleContainerTitle.find_all("tr"):
			overallFields = overallRecord.find_all("td")
			# column 1
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
			# column 2
			fhref = hrefRoot + overallFields[1].find("a").get('href')
			name_bib = overallFields[1].text.replace('(','').replace(')','').split('#')
			fname, fbib = name_bib[0].strip(), int(name_bib[1])
			# column 3
			fracetime = overallFields[2].text.strip()
			if len(fracetime) == 0:
				fracetime = None
			# column 4
			category_pos = overallFields[3].text.replace(')','').replace('\n','').split('(')
			fcategory = CategoryList.index(category_pos[0]) + 1
			if len(category_pos) == 2:
				fcpos = int(category_pos[1])
			else:
				fcpos = None
			# column 5
			fgender = GenderList.index(overallFields[4].find('a').text) + 1
			has_gpos = overallFields[4].find('span')
			if has_gpos:
				fgpos = int(overallFields[4].find('span').text[1:-1])
			else:
				fgpos = None

			# form the dataset of one athlete
			athleteData = [
				fname,
				fcategory,
				fgender,
				fbib,
				fracetime,
				ftpos,
				fcpos,
				fgpos,
				fstatus,
				fhref
			]

			# store into the database
			pCur = utaDb.cursor()
			pCur.execute( athleteQuery, athleteData )
			pCur.close()

			pageAthletes += 1

		# commit the changes on database
		utaDb.commit()
		print("{} ({})".format(overallFile, pageAthletes))

		###time.sleep(intervalTime)

def grabIndividual(utaDb):
	###individualUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1/results/individuals/{}"
	pass

def main():

	# intital the SQLite3 database
	utaDbName = "uta100_2023.db3"
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
		cleanPreviousResultData(utaDb)
	else:
		utaDb = None

	# grab the overall information
	grabOverAll(utaDb)

	# close the database connection
	if utaDb:
		utaDb.close()

if __name__ == '__main__':
	main()
