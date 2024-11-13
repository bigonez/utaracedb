/*
////////////////////////////////////////////////////////////////////////////////////////////////
//  UTA 100 2024 Race Result Dataset
////////////////////////////////////////////////////////////////////////////////////////////////
*/

------------------------------------------------------------------------------------------------
BEGIN TRANSACTION;
------------------------------------------------------------------------------------------------


/*
    Auxiliary Tables

    Tables:
    . Category
    . Gender
    . Location
    . Status
*/

-- Category table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_category;
CREATE TABLE uta100_category (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    category    TEXT NOT NULL
);
INSERT INTO uta100_category VALUES(NULL, '18-19');
INSERT INTO uta100_category VALUES(NULL, '20-34');
INSERT INTO uta100_category VALUES(NULL, '35-39');
INSERT INTO uta100_category VALUES(NULL, '40-44');
INSERT INTO uta100_category VALUES(NULL, '45-49');
INSERT INTO uta100_category VALUES(NULL, '50-54');
INSERT INTO uta100_category VALUES(NULL, '55-59');
INSERT INTO uta100_category VALUES(NULL, '60-64');
INSERT INTO uta100_category VALUES(NULL, '65-69');
INSERT INTO uta100_category VALUES(NULL, '70-74');
INSERT INTO uta100_category VALUES(NULL, '75-79');

-- Gender table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_gender;
CREATE TABLE uta100_gender (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    gender      TEXT NOT NULL,
    abbr        TEXT NOT NULL
);
INSERT INTO uta100_gender VALUES(NULL, 'Male',   'M');
INSERT INTO uta100_gender VALUES(NULL, 'Female', 'F');

-- Location table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_location;
CREATE TABLE uta100_location (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    name        TEXT NOT NULL,
    odometer    REAL NOT NULL,
    cuteoff     TEXT
);
INSERT INTO uta100_location VALUES(NULL, 'Start',                 0.0,  '07:25');
INSERT INTO uta100_location VALUES(NULL, 'Narrow Neck',           2.8,  NULL);
INSERT INTO uta100_location VALUES(NULL, 'Medow Gap',             16.5, '10:45');
INSERT INTO uta100_location VALUES(NULL, 'Foggy Knob Arrive',     24.0, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Foggy Knob Depart',     24.0, '12:20');
INSERT INTO uta100_location VALUES(NULL, 'Six Ft Track Arrive',   37.6, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Six Ft Track Depart',   37.6, '16:05 ');
INSERT INTO uta100_location VALUES(NULL, 'Aquatic Centre Arrive', 56.1, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Aquatic Centre Depart', 56.1, '21:00');
INSERT INTO uta100_location VALUES(NULL, 'Gordon Falls',          63.7, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Fairmount Arrive',      66.9, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Fairmount Depart',      66.9, '00:50');
INSERT INTO uta100_location VALUES(NULL, 'QVH Arrive',            78.3, NULL);
INSERT INTO uta100_location VALUES(NULL, 'QVH Depart',            78.3, '04:55');
INSERT INTO uta100_location VALUES(NULL, 'EAS',                   91.5, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Echo Point',            97.4, NULL);
INSERT INTO uta100_location VALUES(NULL, 'BoardWalk',             99.8, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Finish',               100.1, '11:25');

-- Status table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_status;
CREATE TABLE uta100_status (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    status      TEXT NOT NULL,
    abbr        TEXT NOT NULL
);
INSERT INTO uta100_status VALUES(NULL, 'Finished', 'Finished');
INSERT INTO uta100_status VALUES(NULL, 'Did Not Finish', 'DNF');
INSERT INTO uta100_status VALUES(NULL, 'Did Not Start', 'DNS');


/*
    Athlete & Result Tables

    Tables:
    . Athlete
    . Result
*/

-- Athlete table -------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_athlete;
CREATE TABLE uta100_athlete (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    name        TEXT NOT NULL,                                                  --  name
    bib         INTEGER NOT NULL,                                               --  bib number
    category    INTEGER NOT NULL,                                               --  category id
    gender      INTEGER NOT NULL,                                               --  gender id
    racetime    TEXT,                                                           --  race time
    racestamp   INTEGER,                                                        --  seconds of race time
    tpos        INTEGER,                                                        --  ovarall position
    cpos        INTEGER,                                                        --  category position
    gpos        INTEGER,                                                        --  gender position
    status      INTEGER NOT NULL,                                               --  status id
    link        TEXT NOT NULL                                                   --  link to athlete's race details
);

-- Race Log table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_racelog;
CREATE TABLE uta100_racelog (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    pid         INTEGER NOT NULL,                                               --  athlete Id
    bib         INTEGER NOT NULL,                                               --  bib number
    location    INTEGER NOT NULL,                                               --  location Id
    splittime   TEXT NOT NULL,                                                  --  the split time
    splitstamp  INTEGER NOT NULL,                                               --  seconds of split time
    racetime    TEXT NOT NULL,                                                  --  the race time
    racestamp   INTEGER NOT NULL,                                               --  seconds of race time
    tpos        INTEGER,                                                        --  overall position
    cpos        INTEGER,                                                        --  category position
    gpos        INTEGER,                                                        --  gender position
    speed       REAL,                                                           --  speed
    pace        REAL,                                                           --  pace
    todtime     TEXT NOT NULL,                                                  --  time of day
    todstamp    INTEGER NOT NULL                                                --  seconds of TOD
);


/*
    Analysis Views

    Tables:
    . Athlete & Location
    . Race Log with Full Location
    . Missing Race Log
    . Race Time Proportion
    . Race Time Proportion's Mean
    . Race Time Proportion's Standard Deviation
    . Potential Log Error
*/

-- Athlete & Location view ---------------------------------------------------------------------
DROP VIEW IF EXISTS uta100_athlete_location;
CREATE VIEW uta100_athlete_location AS
    SELECT A.id AS pid, bib, L.id AS location, L.name AS name, odometer
    FROM uta100_location AS L
    JOIN uta100_athlete AS A
    WHERE A.status = 1
    ORDER BY pid, location;

-- Race Logged Record with Full Location view --------------------------------------------------
DROP VIEW IF EXISTS uta100_full_racelog;
CREATE VIEW uta100_full_racelog AS
    SELECT AL.*, splittime, splitstamp, racetime, racestamp, tpos, cpos, gpos, speed, pace, todtime, todstamp
    FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_racelog AS RR
    USING (pid, location)
    ORDER BY AL.pid, AL.location;

-- Missing Race Record view --------------------------------------------------------------------
DROP VIEW IF EXISTS uta100_missing_racelog;
CREATE VIEW uta100_missing_racelog AS
    SELECT AL.*, splittime, splitstamp, racetime, racestamp, todtime, todstamp FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_racelog AS RR
    USING (pid, location)
    WHERE RR.id IS NULL
    ORDER BY AL.pid, AL.location;

-- Race Time Proportion of each athlete x middle location --------------------------------------
DROP VIEW IF EXISTS uta100_racelog_proportion;
CREATE VIEW uta100_racelog_proportion AS
    SELECT C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta100_full_racelog AS P, uta100_full_racelog AS C, uta100_full_racelog AS N
      WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.location, C.pid;

-- Race Time Proportion's Mean of each middle location -----------------------------------------
DROP VIEW IF EXISTS uta100_racelog_mean;
CREATE VIEW uta100_racelog_mean AS
    SELECT location, COUNT(pid) AS total, AVG(proportion) AS mean
    FROM uta100_racelog_proportion
    GROUP BY location;

-- Race Time Proportion's Standard Deviation of each middle location ---------------------------
DROP VIEW IF EXISTS uta100_racelog_std;
CREATE VIEW uta100_racelog_std AS
    SELECT lm.location AS location, lm.total AS total, lm.mean AS mean, SQRT(SUM(sq)/total) AS std
    FROM uta100_racelog_mean AS lm
    LEFT JOIN
     (SELECT P.location, pid, proportion, mean, (proportion - mean) * (proportion - mean) AS sq
      FROM uta100_racelog_proportion AS P
      JOIN uta100_racelog_mean AS M
      WHERE P.location = M.location) AS sq
    ON lm.location = sq.location
    GROUP BY lm.location;

-- Log Error Detaction by 6 times of stanard deviation -----------------------------------------
DROP VIEW IF EXISTS uta100_racelog_error;
CREATE VIEW uta100_racelog_error AS
    SELECT pid, P.location, proportion, mean, std,
      proportion - mean AS ldiff,
      mean - std * 6.0 AS lmin, mean + std * 6.0 AS lmax,
      proportion < (mean - std * 6.0) OR proportion > (mean + std * 6.0) AS oor
    FROM uta100_racelog_proportion AS P
    LEFT JOIN uta100_racelog_std AS S
    ON P.location = S.location
    WHERE oor = 1 ORDER BY pid, P.location;

-- Changes between the original log and the repaired dataset -----------------------------------
DROP VIEW IF EXISTS uta100_repair_changes;
CREATE VIEW uta100_repair_changes AS
    SELECT RL.pid, RL.location,
        RL.splittime AS Ast, RL.splitstamp AS Ass,
        FR.splittime AS Bst, FR.splitstamp AS Bss,
        RL.racetime AS Art, RL.racestamp AS Ars,
        FR.racetime AS Brt, FR.racestamp AS Brs, FR.racestamp - RL.racestamp AS Drs,
        RL.todtime AS Att, RL.todstamp AS Ats,
        FR.todtime AS Btt, FR.todstamp AS Bts
    FROM uta100_finalresult AS FR, uta100_full_racelog AS RL
    WHERE RL.pid = FR.pid AND RL.location = FR.location AND
        (FR.racestamp <> RL.racestamp OR FR.splitstamp <> RL.splitstamp OR RL.racestamp IS NULL);

-- proportion data based on the final race result ----------------------------------------------
DROP VIEW IF EXISTS uta100_final_proportion;
CREATE VIEW uta100_final_proportion AS
    SELECT C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta100_finalresult AS P, uta100_finalresult AS C, uta100_finalresult AS N
      WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.location, C.pid;

-- Final Proportion's Mean of each middle location ---------------------------------------------
DROP VIEW IF EXISTS uta100_final_mean;
CREATE VIEW uta100_final_mean AS
    SELECT location, COUNT(pid) AS total, AVG(proportion) AS mean
    FROM uta100_final_proportion
    GROUP BY location;

-- Final Proportion's Standard Deviation of each middle location -------------------------------
DROP VIEW IF EXISTS uta100_final_std;
CREATE VIEW uta100_final_std AS
    SELECT lm.location AS location, lm.total AS total, lm.mean AS mean, SQRT(SUM(sq)/total) AS std
    FROM uta100_final_mean AS lm
    LEFT JOIN
     (SELECT P.location, pid, proportion, mean, (proportion - mean) * (proportion - mean) AS sq
      FROM uta100_final_proportion AS P
      JOIN uta100_final_mean AS M
      WHERE P.location = M.location) AS sq
    ON lm.location = sq.location
    GROUP BY lm.location;


------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------
