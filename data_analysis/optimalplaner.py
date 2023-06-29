#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3, sys, os.path, time, datetime

def getProportionData(utaDb, useLimit, useStart):

	meanQuery = "SELECT location, AVG(proportion) AS mean FROM uta100_final_proportion"
	if useLimit:
		meanQuery += " WHERE pid >= {} AND pid <= {}".format(useStart, useStart + useLimit - 1)
	meanQuery += " GROUP BY location"

	pCur = utaDb.cursor()

	pCur.execute(meanQuery)
	meanList = pCur.fetchall()

	pCur.close()

	ProportionData = {}
	for cpid, proportion in meanList:
		ProportionData[cpid] = proportion

	return ProportionData

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

def main(RaceTime, UseLimit, UseStart):

	# intital the SQLite3 database
	utaDbName = "uta100_2023.db3"
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
	else:
		sys.exit(" !!! Failed to load the database")

	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Race Time Planner', 'UTA100 2023', '-'*50))
	print("{:>24}: {} hours\n{:>24}: {} [{}, {}]\n{}".format(
		"Expected Finish Time", RaceTime, "Athlete Dataset", UseLimit, UseStart, UseStart + UseLimit - 1, '-'*50
	))
	print("   {:>4}   {:^10}   {:^10}   {:^10}".format('No.', 'Full', 'Optimal', 'Diff'))

	FinalProportionData = getProportionData(utaDb, None, None)
	OptimalProportionData = getProportionData(utaDb, UseLimit, UseStart)

	ExpectRaceTime = round(RaceTime * 3600)										# unit: hours -> seconds

	FinalPercents   = proport2percent(FinalProportionData)
	OptimalPercents = proport2percent(OptimalProportionData)
	for cpid in range(len(FinalPercents)):
		finalTime   = round((FinalPercents[cpid + 1]   * ExpectRaceTime) / 60) * 60
		optimalTime = round((OptimalPercents[cpid + 1] * ExpectRaceTime) / 60) * 60
		print("  {:>4d}   {:>10}   {:>10}   {:>10}".format(
			cpid + 1, strRecetime(finalTime), strRecetime(optimalTime), strRecetime(finalTime - optimalTime, True)
		))

	utaDb.close()

	print("{}".format('='*50))

if __name__ == '__main__':
	startTime = time.time()

	RaceTime = float(sys.argv[1])
	UseLimit = int(sys.argv[2])
	if len(sys.argv) > 3:
		UseStart = int(sys.argv[3])
	else:
		UseStart = 1

	main(RaceTime, UseLimit, UseStart)

	finishTime = time.time()
	processTime = datetime.timedelta(seconds=(finishTime - startTime))

	print(" Total Processing Time: {}".format(strTimeDelta(processTime, 2)))
