import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main1():
	stats_category = pd.read_csv('./uta100_stats_category.csv', parse_dates=True)
	cTotal  = np.array(stats_category['total'])
	cTotal.resize((3,12))
	cTotal = cTotal.transpose()
	cName   = np.array(stats_category['category'][:12])
	cStatus = np.array(stats_category['status'][:25:12])

	cCount = {cName[i]: cTotal[i] for i in range(len(cName))}

	width = 0.6  # the width of the bars: can also be len(x) sequence

	fig, ax = plt.subplots()
	bottom = np.zeros(3)

	for category, ccount in cCount.items():
		p = ax.bar(cStatus, ccount, width, label=category, bottom=bottom)
		bottom += ccount

		ax.bar_label(p, label_type='center')

	ax.set_title('UTA100 2023 Stats (Category)')
	ax.legend()
	plt.show()

def main2():
	stats_category = pd.read_csv('./uta100_stats_category.csv', parse_dates=True)
	cTotal  = np.array(stats_category['total'])
	cTotal.resize((3,12))
	#cTotal = cTotal.transpose()
	cName   = np.array(stats_category['category'][:12])
	cStatus = np.array(stats_category['status'][:25:12])

	cCount = {cStatus[i]: cTotal[i] for i in range(len(cStatus))}

	width = 0.6  # the width of the bars: can also be len(x) sequence

	fig, ax = plt.subplots()
	bottom = np.zeros(12)

	for category, ccount in cCount.items():
		p = ax.bar(cName, ccount, width, label=category, bottom=bottom)
		bottom += ccount

		ax.bar_label(p, label_type='center')

	ax.set_title('UTA100 2023 Stats (Category)')
	ax.legend()
	plt.show()

if __name__ == '__main__':

	#main1()
	main2()
