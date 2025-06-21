/*
////////////////////////////////////////////////////////////////////////////////////////////////
//  UTA 2025 Race Result Dataset
////////////////////////////////////////////////////////////////////////////////////////////////
*/

------------------------------------------------------------------------------------------------
BEGIN TRANSACTION;
------------------------------------------------------------------------------------------------


-- Polynomial Fitting view & tables ------------------------------------------------------------
DROP VIEW IF EXISTS uta_percentage;
CREATE VIEW uta_percentage AS
    SELECT R.event, R.pid, A.name, R.bib, R.location, R.name AS alias,
      R.racetime, A.racetime AS totaltime, R.racestamp, A.racestamp AS totalstamp, R.racestamp * 100. / A.racestamp AS proportion
      FROM uta_finalresult AS R
      JOIN uta_athlete AS A
      ON A.id = R.pid
      ORDER BY R.event, R.pid, R.location;

DROP TABLE IF EXISTS uta_pfresidual;
CREATE TABLE uta_pfresidual (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event       INTEGER NOT NULL,                                               --  Event Id
    location    INTEGER NOT NULL,                                               --  Location Id
    pid         INTEGER NOT NULL,                                               --  Athlete Id

    racestamp   INTEGER NOT NULL,                                               --  Race Timestamp
    totalstamp  INTEGER NOT NULL,                                               --  Total Timestamp
    fittedstamp INTEGER NOT NULL,                                               --  Fitted Timestamp
    residualstamp INTEGER NOT NULL,                                             --  Residual Timestamp

    racetime    TEXT NOT NULL,                                                  --  Race Time
    totaltime   TEXT NOT NULL,                                                  --  Total Time
    fittedtime  TEXT NOT NULL,                                                  --  Fitted Time
    residualtime TEXT NOT NULL                                                  --  Residual Time
);

DROP TABLE IF EXISTS uta_pfcoeffs;
CREATE TABLE uta_pfcoeffs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event       INTEGER NOT NULL,                                               --  Event Id
    location    INTEGER NOT NULL,                                               --  Location Id

    degree      INTEGER NOT NULL,                                               --  Polynomial Degree
    coeffs      TEXT    NOT NULL                                                --  Coefficients (JSON)
);


------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------
