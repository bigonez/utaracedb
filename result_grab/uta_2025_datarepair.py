#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3, sys, os.path, time, datetime

def formFinalResultTable(utaDb):
	pCur = utaDb.cursor()

	pCur.execute("DROP TABLE IF EXISTS uta_finalresult")
	pCur.execute("CREATE TABLE IF NOT EXISTS uta_finalresult AS SELECT * FROM uta_full_racelog")

	pCur.close()
	utaDb.commit()

def defineCorrectRaceLogList():
	# correct race log list [
	#   (pid, event, location, correction),
	#   ( 59, 1, 5, 1800),
	#   (128, 1, 8, 3600),
	#   (252, 1, 8, 1200),
	#   (342, 1, 5, 3600),
	#   (566, 1, 5, 3600),
	#   ...
	# ]
	crtLogList = [
	]

	return crtLogList

def correctRaceLogTime(utaDb, crtLogList):
	pCur = utaDb.cursor()

	frQuery = "SELECT pid, event, location, racestamp, todstamp FROM uta_finalresult WHERE pid = ? AND event=? AND location IN (?, ?, ?)"
	uCurrentQuery = "UPDATE uta_finalresult SET splitstamp=?, splittime=?, racestamp=?, racetime=?, todstamp=?, todtime=? WHERE pid=? AND event=? AND location=?"
	uNextQuery = "UPDATE uta_finalresult SET splitstamp=?, splittime=? WHERE pid=? AND event=? AND location=?"

	print("\n . correct {} records with wrong race time\n   {}\n   athlete, event, location, shift, race time, timestamp".format(len(crtLogList), '-'*44))
	for crtLog in crtLogList:
		print(crtLog)
		pid, event, lid, timeShift = crtLog

		pRes = pCur.execute(frQuery, (pid, event, lid - 1, lid, lid + 1))
		frData = pRes.fetchall()

		Prs, Crs, Nrs, Cts = frData[0][2], frData[1][2], frData[2][2], frData[1][3]
		Crs += timeShift
		Cts += timeShift

		# correct the wrong race record
		currentData = [
			Crs - Prs, stampToHMS(Crs - Prs),
			Crs, stampToHMS(Crs),
			Cts, stampToHMS(Cts, True),
			pid,
			event,
			lid
		]
		pCur.execute(uCurrentQuery, currentData)
		print("   {}, {}, {}, {} ({})".format(pid, lid, timeShift, stampToHMS(Crs), Crs))

		# correct the following record's split stamp only
		nextData = [
			Nrs - Crs, stampToHMS(Nrs - Crs),
			pid,
			event,
			lid + 1
		]
		pCur.execute(uNextQuery, nextData)

	# commit the changes
	pCur.close()
	utaDb.commit()

def estimateRaceLogTime(utaDb, meanDict, mrtList):
	pCur = utaDb.cursor()

	rlQuery = "SELECT pid, event, location, racestamp, todstamp FROM uta_full_racelog WHERE pid=? AND event=? AND location IN (?, ?)"

	cmrtList = []
	estTSList = []
	extSSList = []
	for pid, event, lid in mrtList:
		lmean = meanDict.get(event).get(lid)

		pRes = pCur.execute(rlQuery, (pid, event, lid - 1, lid + 1))
		rlData = pRes.fetchall()

		leftRS, leftTS, rightRS = rlData[0][3], rlData[0][4], rlData[1][3]
		if leftRS and rightRS:
			# found the valid race timestamp of the previous & next location
			estSplitStamp = round((rightRS - leftRS) * lmean)

			estRaceStamp  = leftRS + estSplitStamp

			estTodStamp   = (leftTS + estSplitStamp) % 86400

			estData = (pid, event, lid, estSplitStamp, estRaceStamp, estTodStamp)
			estTSList.append(estData)

			extSplitStamp = rightRS - estRaceStamp
			extSSData = (pid, event, lid + 1, extSplitStamp)
			extSSList.append(extSSData)
		else:
			# it's a gap with the continous missing data
			estRaceStamp = None
			estRaceTime = None
			cmrtList.append((pid, event, lid, lmean, leftRS, leftTS, rightRS))

	# deal with the gap with the continous missing data
	for cmrtIdx in range(len(cmrtList)//2):

		pid, event, lid1, Xm, Ars,  Ats, tmp1 = cmrtList[2*cmrtIdx    ]
		pid, event, lid2, Ym, tmp2, tmp3, Drs = cmrtList[2*cmrtIdx + 1]

		# race stamp
		Brs = round((Ars * (1 - Xm) + Drs * Ym * Xm) / (1 + Xm * (Ym - 1)))
		Crs = round((Ars * (1 - Xm) * (1 - Ym) + Drs * Ym) / ( 1 + Xm * (Ym - 1)))
		# split stamp
		Bss, Css = Brs - Ars, Crs - Brs
		# TOD stamp
		Bts = Ats + Bss
		Cts = Bts + Css

		estB = (pid, event, lid1, Bss, Brs, Bts)
		estC = (pid, event, lid2, Css, Crs, Cts)
		estTSList.append(estB)
		estTSList.append(estC)

		extSS = Drs - Crs
		extSSData = (pid, event, lid2 + 1, extSS)
		extSSList.append(extSSData)

	pCur.close()

	return estTSList, extSSList

def storeEstimateRaceLog(utaDb, estRaceLogList, extSplitStampList):
	pCur = utaDb.cursor()

	updateTimeStampQuery = "UPDATE uta_finalresult SET splitstamp=?, splittime=?, racestamp=?, racetime=?, todstamp=?, todtime=? WHERE pid=? AND event=? AND location=?"
	updateSplitTSQuery   = "UPDATE uta_finalresult SET splitstamp=?, splittime=? WHERE pid=? AND event=? AND location=?"

	# save the racestamp, TOD stamp & split stamp on the gap
	print("\n . refill {} records with missing race time\n   {}\n   athlete, location, race time, timestamp".format(len(estRaceLogList), '-'*44))
	for estRaceLog in estRaceLogList:
		pid, event, lid, estSplitStamp, estRaceStamp, estTodStamp = estRaceLog
		estData = [
			estSplitStamp, stampToHMS(estSplitStamp),
			estRaceStamp,  stampToHMS(estRaceStamp),
			estTodStamp,   stampToHMS(estTodStamp, True),
			pid,
			event,
			lid
		]

		pCur.execute(updateTimeStampQuery, estData)
		print("   {}, {}, {} ({})".format(pid, lid, stampToHMS(estRaceStamp), estRaceStamp))

	# update the split stamp of the following record only
	for extSplitStamp in extSplitStampList:
		pid, event, lid, extSS = extSplitStamp
		extData = [
			extSS, stampToHMS(extSS),
			pid,
			event,
			lid
		]

		pCur.execute(updateSplitTSQuery, extData)

	# commit the changes
	pCur.close()
	utaDb.commit()

def getMissingRacetimeList(utaDb):
	pCur = utaDb.cursor()

	# fetch the mean list of each location
	meanDict = {}
	for event in [1,5]:
		meanQuery = "SELECT location, mean FROM uta_racelog_mean WHERE event=?"
		pRes = pCur.execute(meanQuery, (event,))
		meanList = pRes.fetchall()
		meanDict[event] = dict(meanList)

	# get the list which has the missing timestamp data
	mrtQuery = "SELECT pid, event, location FROM uta_missing_racelog"
	pRes = pCur.execute(mrtQuery)
	mrtList = pRes.fetchall()

	pCur.close()

	return meanDict, mrtList

def stampToHMS(ts:int, wl:bool=False) -> str:
	ts = ts % 86400
	hours   = ts // 3600
	minutes = (ts - hours * 3600) // 60
	seconds = ts % 60

	if wl:
		return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
	else:
		return "{:d}:{:02d}:{:02d}".format(hours, minutes, seconds)

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

def main():

	# intital the SQLite3 database
	utaDbName = "uta_2025.db3"
	if os.path.exists(utaDbName):
		utaDb = sqlite3.connect(utaDbName)
		formFinalResultTable(utaDb)
	else:
		sys.exit(" !!! Failed to load the database")

	print("{}\n  {:18}{:>28}\n{}".format('='*50, 'Data Repaire', 'UTA 2025', '-'*50))

	crtLogList = defineCorrectRaceLogList()
	correctRaceLogTime(utaDb, crtLogList)

	meanDict, mrtList = getMissingRacetimeList(utaDb)

	estRaceLogList, extSplitStampList = estimateRaceLogTime(utaDb, meanDict, mrtList)

	storeEstimateRaceLog(utaDb, estRaceLogList, extSplitStampList)

	utaDb.close()

	print("\n{}".format('='*50))

if __name__ == '__main__':
	startTime = time.time()

	main()

	finishTime = time.time()
	processTime = datetime.timedelta(seconds=(finishTime - startTime))

	print(" Total Processing Time: {}".format(strTimeDelta(processTime, 2)))
