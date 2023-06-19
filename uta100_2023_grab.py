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
	overallUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1?page={}"
	totalPages = 23
	overallRange = range(1, totalPages + 1)
	athleteQuery = "INSERT INTO uta100_athlete VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

	# grab the all overall page
	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Overall List', 'UTA100 2023', '-'*50))
	totalAthletes = 0
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
			pCur = utaDb.cursor()
			pCur.execute( athleteQuery, athleteData )
			pCur.close()

			pageAthletes += 1

		# commit the changes on database
		utaDb.commit()

		totalAthletes += pageAthletes
		print("\b\b\b\b\b, {}, {}".format(pageAthletes, totalAthletes))

		if i < totalPages:
			sleepAnimation(intervalTime)

	print("{}\n Total Overall Pages: {}, Total Athletes: {}\n{}".format('-'*50, totalPages, totalAthletes, '='*50))

def grabIndividual(utaDb):
	###individualUrl = "https://www.multisportaustralia.com.au/races/ultra-trail-australia-2023/events/1/results/individuals/{}"
	pass

def sleepAnimation(itime):
	print('>', end='', flush=True)
	time.sleep(1)
	for i in range(itime-1):
		print("\b ", end='>', flush=True)
		time.sleep(1)
	print("\b "+"\b"*(i+2), end='', flush=True)

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
