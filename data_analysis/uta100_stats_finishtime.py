import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main1():
	ftSum = pd.read_csv('./uta100_stats_finishtime.csv', parse_dates=True)
	ftid   = np.array(ftSum['id'])
	ftHour = np.array(ftSum['finishhour'])
	ftStat = np.array(ftSum['total'])

	fig, ax = plt.subplots()

	hbars = ax.bar(ftid, ftStat, align='center', color="#6A5ACD")
	addlabels(ftid, ftStat)

	ax.set_xticks(ftid, labels=ftHour)
	ax.set_xlabel('Finish Hours')
	ax.set_ylabel('Finish Count')
	ax.set_ylim(top=100, bottom=0)

	ax.set_title('UTA100 2023 Stats (Finish Time)')
	plt.show()

def addlabels(x,y):
	for i in range(len(x)):
		plt.text(i+1, y[i]+1, y[i], ha = 'center')

def main2():
	stats_gender = pd.read_csv('./uta100_stats_gender_finishtime.csv', parse_dates=True)
	gfTotal  = np.array(stats_gender['total'])
	gfTotal.resize((2,20))
	#gfTotal = gfTotal.transpose()
	gfName  = np.array(stats_gender['gender'][::20])
	gfHours = np.array(stats_gender['finishhour'][:20])

	gfCount = {gfName[i]: gfTotal[i] for i in range(len(gfName))}

	fig, ax = plt.subplots()
	bottom = np.zeros(20)

	for name, gfcount in gfCount.items():
		p = ax.bar(gfHours, gfcount, label=name, bottom=bottom)
		bottom += gfcount

		ax.bar_label(p, label_type='center', fontstyle='italic')

	for i in range(len(gfHours)):
		plt.text(gfHours[i], gfTotal[0][i]+gfTotal[1][i]+1, gfTotal[0][i]+gfTotal[1][i], ha='center', fontweight='bold')

	ax.set_xlabel('Finish Hours')
	ax.set_ylabel('Finish Count')
	ax.set_ylim(top=100, bottom=0)
	ax.set_xticks(gfHours, labels=gfHours)
	ax.set_title('UTA100 2023 Stats (Finish Time)')
	ax.legend()
	plt.show()

if __name__ == '__main__':

	main1()
	main2()
