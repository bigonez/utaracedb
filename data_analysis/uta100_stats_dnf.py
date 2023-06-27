import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits import mplot3d

def main():
	dnfSum = pd.read_csv('./uta100_stats_dnf.csv', parse_dates=True)
	dnfStat  = np.array(dnfSum['dnf'])
	cpname   = np.array(dnfSum['name'])
	cpid     = np.array(dnfSum['id'])
	odometer = np.array(dnfSum['odometer'])

	fig, ax = plt.subplots()

	hbars = ax.barh(cpid, dnfStat, align='center')
	ax.set_yticks(cpid, labels=cpname)
	ax.invert_yaxis()  # labels read top-to-bottom
	ax.set_xlabel('DNF Count')

	ax.bar_label(hbars, fmt='%.0f')
	ax.set_xlim(right=50)

	ax.set_title('UTA100 2023 Stats (DNF)')
	plt.show()

if __name__ == '__main__':

	main()
