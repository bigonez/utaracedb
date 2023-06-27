import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main1():
	stats_gender = pd.read_csv('./uta100_stats_gender.csv', parse_dates=True)
	gTotal  = np.array(stats_gender['total'])
	gTotal.resize((3,2))
	gTotal = gTotal.transpose()
	gName   = np.array(stats_gender['gender'][:2])
	gStatus = np.array(stats_gender['status'][:5:2])

	gCount = {gName[i]: gTotal[i] for i in range(len(gName))}

	width = 0.6  # the width of the bars: can also be len(x) sequence

	fig, ax = plt.subplots()
	bottom = np.zeros(3)

	for gender, gcount in gCount.items():
		p = ax.bar(gStatus, gcount, width, label=gender, bottom=bottom)
		bottom += gcount

		ax.bar_label(p, label_type='center')

	ax.set_title('UTA100 2023 Stats (Gender)')
	ax.legend()
	plt.show()

def main2():
	stats_gender = pd.read_csv('./uta100_stats_gender.csv', parse_dates=True)
	gTotal  = np.array(stats_gender['total'])
	gTotal.resize((3,2))
	#gTotal = gTotal.transpose()
	gName   = np.array(stats_gender['gender'][:2])
	gStatus = np.array(stats_gender['status'][:5:2])

	gCount = {gStatus[i]: gTotal[i] for i in range(len(gStatus))}

	width = 0.6  # the width of the bars: can also be len(x) sequence

	fig, ax = plt.subplots()
	bottom = np.zeros(2)

	for gender, gcount in gCount.items():
		p = ax.bar(gName, gcount, width, label=gender, bottom=bottom)
		bottom += gcount

		ax.bar_label(p, label_type='center')

	ax.set_title('UTA100 2023 Stats (Gender)')
	ax.legend()
	plt.show()

if __name__ == '__main__':

	#main1()
	main2()
