import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits import mplot3d

def main():
	timeStamp = pd.read_csv('./uta100_racestamp.csv', parse_dates=True)
	newStamp = np.array(timeStamp['racestamp']) / 3600.0
	newStamp.resize((834,20))

	pid = np.array(range(1, 835))
	location = np.array(range(1, 21))
	odometer = np.array([ 0.0,  4.1,  6.2, 10.1, 21.2, 31.2, 31.2, 33.6, 44.7, 44.7,
				55.7, 55.7, 69.1, 69.1, 78.1, 78.1, 94.1, 98.9, 99.8,100.1])

	X, Y = np.meshgrid(pid, location)
	O = odometer[Y-1]
	Z = newStamp[X-1, Y-1]

	fig = plt.figure()
	ax = plt.axes(projection ='3d')
	ax.plot_surface(X, O, Z, cmap='rainbow', alpha=0.8)
	ax.set_title('UTA100 2023 Race Time (hours)')
	plt.show()

if __name__ == '__main__':

	main()
