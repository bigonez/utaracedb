import os, sqlite3
import numpy as np
import matplotlib.pyplot as plt
import json

# Polynomial fitting degree
pfDegree = 3

def polyFit(x, y, degree=2):
    """
    Fit a polynomial of a given degree to the data points (x, y).
    Returns the coefficients of the polynomial.
    """
    coeffs = np.polyfit(x, y, degree)
    return coeffs

def SecondsToHms(timestamp):
    prefix = ""
    timestamp = round(timestamp)
    if timestamp < 0:
        prefix = '-'
        timestamp = - timestamp

    hours   = timestamp // 3600
    minutes = (timestamp - hours * 3600) // 60
    seconds = round(timestamp  % 60)

    return prefix + "{:d}:{:02d}:{:02d}".format(hours, minutes, seconds)

# Using vectorize()
array_seconds_to_hms = np.vectorize(SecondsToHms)

def cleanPolynomialFitData(utaDb):
	pCur = utaDb.cursor()

	pCur.execute( "begin transaction;" )
	pCur.execute( "delete from uta_pfcoeffs;" )								# clean the table of polynomial fitting data
	pCur.execute( "delete from sqlite_sequence where name='uta_pfcoeffs';" )	# reset the auto increment field
	pCur.execute( "delete from uta_pfresidual;" )								# clean the table of polynomial fitting data
	pCur.execute( "delete from sqlite_sequence where name='uta_pfresidual';" )	# reset the auto increment field
	pCur.execute( "commit transaction;" )

	pCur.close()
	utaDb.commit()

def plotFitData(event, location, x, y, coeffs, degree):
    """
    Plot the original data points and the polynomial fit.
    """
    # Generate x values for the fitted curve
    x_fit = np.linspace(min(x), max(x), 100)
    # Calculate the fitted y values
    y_fit = np.polyval(coeffs, x_fit)

    # Plot the original data points
    plt.scatter(x, y, label='Data', color='blue')
    # Plot the fitted polynomial curve
    plt.plot(x_fit, y_fit, 'r-', label=f'Polynomial Fit (degree={degree})')

    plt.xlabel('Total Stamp (hours)')
    plt.ylabel('Race Stamp (hours)')
    plt.title(f'Polynomial Fit (degree={degree}) @ Event {event}, Location {location}')
    plt.legend()
    plt.grid()
    plt.show()

def main(utaDb, pfDegree=3):
    """
    Main function to perform polynomial fitting on
    """
    totalEvents = [1, 5]
    totalCPs = { 1: 22, 5: 29 }

    pfSourceQuery = "SELECT event, location, pid, racestamp, totalstamp FROM uta_percentage WHERE event=? AND location=?"
    pfCoeffsQuery = "INSERT INTO uta_pfcoeffs (event, location, degree, coeffs) VALUES (?, ?, ?, ?)"
    pfResidualQuery = "INSERT INTO uta_pfresidual (event, location, pid, racestamp, totalstamp, fittedstamp, residualstamp, racetime, totaltime, fittedtime, residualtime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    pCur = utaDb.cursor()

    for event in totalEvents:
        for location in range(2, totalCPs[event]):
            pRes = pCur.execute( pfSourceQuery, (event, location))
            pData = pRes.fetchall()
            print(event, location, len(pData))

            data1 = np.array(pData)

            cpids = data1[:, 2].astype(int)
            racestamp = data1[:, 3].astype(float)  # racestamp
            totalstamp = data1[:, 4].astype(float) # totalstamp
            racehour  = racestamp / 3600    # racestamp
            totalhour = totalstamp / 3600    # totalstamp

            # Fit a polynomial of degree ? to the data
            coeffs = polyFit(totalhour, racehour, degree=pfDegree)

            # Calculate the fitted values
            fitted_racehour = np.polyval(coeffs, totalhour)
            # Convert fitted racehour back to seconds
            fitted_racestamp = np.round(fitted_racehour * 3600).astype(int)  # Convert back to seconds
            # Convert fitted racestamp to h:m:s format
            fitted_racestampstr = array_seconds_to_hms(fitted_racestamp)
            fitted_racestampstr = fitted_racestampstr.astype(str)

            # Calculate the residuals
            residual_racehour = racehour - fitted_racehour
            # Convert residuals racehour back to seconds
            residual_racestamp = np.round(residual_racehour * 3600).astype(int)  # Convert back to seconds
            # Convert residuals racestamp to h:m:s format
            residual_racestr = array_seconds_to_hms(residual_racestamp)
            residual_racestr = residual_racestr.astype(str)

            # Plot the fit data
            #?  plotFitData(event, location, totalhour, racehour, coeffs, degree=pfDegree)

            # Save the polynomial fit data to the database
            pCur.execute( "begin transaction;" )

            # Save the polynomial coefficients to the database
            pfCoeffsData = (event, location, pfDegree, json.dumps(list(coeffs)))
            pCur.execute(pfCoeffsQuery, pfCoeffsData)

            # Save the polynomial fit results to the database
            for i in range(len(cpids)):
                # Prepare the data for saving
                pfResidualData = (
                    event, location, int(cpids[i]),
                    racestamp[i], totalstamp[i],
                    int(fitted_racestamp[i]), int(residual_racestamp[i]),
                    SecondsToHms(racestamp[i]), SecondsToHms(totalstamp[i]),
                    fitted_racestampstr[i], residual_racestr[i]
                )
                # Save the data to the database
                pCur.execute(pfResidualQuery, pfResidualData)
            pCur.execute("COMMIT;")

            # Commit the changes to the database
            utaDb.commit()

    pCur.close()

if __name__ == '__main__':
    utaDbName = os.path.join(os.path.dirname(__file__), "uta_2025.db3")
    utaDb = None
    # intital the SQLite3 database
    if os.path.exists(utaDbName):
        utaDb = sqlite3.connect(utaDbName)
        cleanPolynomialFitData(utaDb)

    main(utaDb, pfDegree)

    # close the database connection
    if utaDb:
        utaDb.close()
