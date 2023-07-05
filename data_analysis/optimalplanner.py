#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3, sys, os.path, time, datetime, math

def getProportionData(utaDb, raceTime, useLimit):

	optimalQuery = "SELECT location, AVG(proportion) AS mean, lpid, upid FROM uta100_final_proportion"
	if useLimit:
		optimalQuery += """ LEFT JOIN (SELECT MIN(id) AS lpid, MAX(id) AS upid FROM ( \
		  SELECT id, racetime, racestamp, ABS(racestamp - {}*3600) AS rsdiff \
		  FROM uta100_athlete \
		  WHERE status=1 \
		  ORDER BY rsdiff \
		  LIMIT {} \
		 )) \
		 WHERE pid >= lpid AND pid <= upid""".format(raceTime, useLimit)
	else:
		optimalQuery += " LEFT JOIN (SELECT MIN(id) AS lpid, MAX(id) AS upid FROM uta100_athlete WHERE status=1)"
	optimalQuery += " GROUP BY location"

	pCur = utaDb.cursor()

	pCur.execute(optimalQuery)
	meanList = pCur.fetchall()

	pCur.close()

	ProportionData = {}
	lpid, upid = 0, 0
	for cpid, proportion, lpid, upid in meanList:
		ProportionData[cpid] = proportion

	return ProportionData, lpid, upid

def proport2percent(ProportionData):
	CpPercents = {
		1: 0.0,
		2: 1.0
	}
	totalCp = len(ProportionData)

	Tp = 1.0
	Trace = Tp
	for cp in range(len(ProportionData)):
		Pcp = ProportionData[cp+2]

		Tp *= (1 - Pcp) / Pcp

		Trace += Tp

		CpPercents[cp+3] = Trace

	for cp in CpPercents.keys():
		CpPercents[cp] /= Trace

	return CpPercents

def strRecetime(racetime, sign=False):
	racetime = round(racetime)

	prefix = ''
	if sign:
		if racetime <= 0:
			prefix = ' '
		else:
			prefix = '-'
	if racetime < 0:
		racetime = -racetime

	hours   = racetime // 3600
	minutes = (racetime - hours * 3600) // 60
	seconds = racetime % 60

	return "{}{:d}:{:02d}:{:02d}".format(prefix, hours, minutes, seconds)

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

def main(RaceTime, UseLimit):

	# intital the SQLite3 database
	utaDbPath = os.path.abspath(os.path.dirname(__file__))
	utaDbName = os.path.join(utaDbPath, "uta100_2023.db3")
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
	else:
		sys.exit(" !!! Failed to load the database")

	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Race Time Planner', 'UTA100 2023', '-'*50))

	FinalProportionData, lpid, upid = getProportionData(utaDb, None, None)
	OptimalProportionData, lpid, upid = getProportionData(utaDb, RaceTime, UseLimit)

	utaDb.close()

	ExpectRaceTime = round(RaceTime * 3600)										# unit: hours -> seconds

	ArraiveIds = [6, 9, 11, 13, 15]
	FinalPercents   = proport2percent(FinalProportionData)
	OptimalPercents = proport2percent(OptimalProportionData)

	print("{:>27}: {} hours\n{:>27}: {} [{}, {}]".format(
		"Expected Finish Time", RaceTime, "Optimal Athlete Dataset", UseLimit, lpid, upid
	))
	print('-'*50 + "\n {:>4}   {:^18}   {:^18}".format('No.', 'Full', 'Optimal'))
	for cpid in FinalProportionData.keys():
		print("{:>4d}   {:>18.12f}   {:>18.12f}".format(
			cpid, FinalProportionData[cpid], OptimalProportionData[cpid]
		))
	print('-'*50 + "\n {:>4}   {:^18}    {:^18}".format('No.', 'Encrypt Full', 'Encrypt Optimal'))
	for cpid in FinalProportionData.keys():
		fp = math.exp(math.pi - FinalProportionData[cpid])
		op = math.exp(math.pi - OptimalProportionData[cpid])
		print("{:>4d}   {:>18.12f}   {:>18.12f}".format(
			cpid, fp, op
		))

	print('-'*50 + "\n {:>4}   {:^10}   {:^10}   {:^10}".format('No.', 'Full', 'Optimal', 'Diff'))
	for cpid in range(len(FinalPercents)):
		finalTime   = round((FinalPercents[cpid + 1]   * ExpectRaceTime) / 60) * 60
		optimalTime = round((OptimalPercents[cpid + 1] * ExpectRaceTime) / 60) * 60
		if (cpid + 1) in ArraiveIds:
			tailflag = '(*)'
		else:
			tailflag = ''
		print("{:>4d}   {:>10}   {:>10}   {:>10}   {}".format(
			cpid + 1, strRecetime(finalTime), strRecetime(optimalTime), strRecetime(finalTime - optimalTime, True), tailflag
		))

	print("{}".format('='*50))

if __name__ == '__main__':
	startTime = time.time()

	RaceTime = float(sys.argv[1])
	UseLimit = int(sys.argv[2])

	main(RaceTime, UseLimit)

	finishTime = time.time()
	processTime = datetime.timedelta(seconds=(finishTime - startTime))

	print(" Total Processing Time: {}".format(strTimeDelta(processTime, 2)))
