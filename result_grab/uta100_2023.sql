/*
////////////////////////////////////////////////////////////////////////////////////////////////
//  UTA 100 2023 Result Dataset
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
INSERT INTO uta100_category VALUES(NULL, '18-24');
INSERT INTO uta100_category VALUES(NULL, '25-29');
INSERT INTO uta100_category VALUES(NULL, '30-34');
INSERT INTO uta100_category VALUES(NULL, '35-39');
INSERT INTO uta100_category VALUES(NULL, '40-44');
INSERT INTO uta100_category VALUES(NULL, '45-49');
INSERT INTO uta100_category VALUES(NULL, '50-54');
INSERT INTO uta100_category VALUES(NULL, '55-59');
INSERT INTO uta100_category VALUES(NULL, '60-64');
INSERT INTO uta100_category VALUES(NULL, '65-69');
INSERT INTO uta100_category VALUES(NULL, '70-74');
INSERT INTO uta100_category VALUES(NULL, '75+'  );

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
INSERT INTO uta100_location VALUES(NULL, 'Start',                 0.0,  NULL);
INSERT INTO uta100_location VALUES(NULL, 'Scenic World',          4.1,  NULL);
INSERT INTO uta100_location VALUES(NULL, 'Furber Pass',           6.2,  NULL);
INSERT INTO uta100_location VALUES(NULL, 'Golden Stairs',         10.1, '10:22');
INSERT INTO uta100_location VALUES(NULL, 'Duncan Pass',           21.2, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Foggy Knob Arrive',     31.2, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Foggy Knob Depart',     31.2, '15:00');
INSERT INTO uta100_location VALUES(NULL, 'IronPot',               33.6, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Six Ft Track Arrive',   44.7, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Six Ft Track Depart',   44.7, '18:50');
INSERT INTO uta100_location VALUES(NULL, 'Aquatic Centre Arrive', 55.7, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Aquatic Centre Depart', 55.7, '22:00');
INSERT INTO uta100_location VALUES(NULL, 'Fairmount Arrive',      69.1, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Fairmount Depart',      69.1, '02:35');
INSERT INTO uta100_location VALUES(NULL, 'QVH Arrive',            78.1, NULL);
INSERT INTO uta100_location VALUES(NULL, 'QVH Depart',            78.1, '05:45');
INSERT INTO uta100_location VALUES(NULL, 'TWM',                   94.1, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Furber Stairs',         98.9, NULL);
INSERT INTO uta100_location VALUES(NULL, 'BoardWalk',             99.8, NULL);
INSERT INTO uta100_location VALUES(NULL, 'Finish',               100.1, '11:54');

-- Status table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_status;
CREATE TABLE uta100_status (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    status      TEXT NOT NULL,
    abbr        TEXT NOT NULL
);
INSERT INTO uta100_status VALUES(NULL, 'Finished', 'Finished');
INSERT INTO uta100_status VALUES(NULL, 'Did Not Finish', 'DNF');
INSERT INTO uta100_status VALUES(NULL, 'Not Yet Started', 'NYS');


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

-- Result table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta100_raceresult;
CREATE TABLE uta100_raceresult (
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
    . Race Result with Full Location
    . Missing Race Result
*/

-- Athlete & Location view ---------------------------------------------------------------------
DROP VIEW IF EXISTS uta100_athlete_location;
CREATE VIEW uta100_athlete_location AS
    SELECT A.id AS pid, bib, L.id AS location, L.name AS name, odometer
    FROM uta100_location AS L
    JOIN uta100_athlete AS A
    WHERE A.status = 1
    ORDER BY pid, location;

-- Race Result with Full Location view ---------------------------------------------------------
DROP VIEW IF EXISTS uta100_full_raceresult;
CREATE VIEW uta100_full_raceresult AS
    SELECT AL.*, RR.splittime, splitstamp, racetime, racestamp, tpos, cpos, gpos, speed, pace, todtime, todstamp
    FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_raceresult AS RR
    USING (pid, location)
    ORDER BY AL.pid, AL.location;

-- Missing Race Result view --------------------------------------------------------------------
DROP VIEW IF EXISTS uta100_missing_raceresult;
CREATE VIEW uta100_missing_raceresult AS
    SELECT AL.*, racetime, racestamp FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_raceresult AS RR
    USING (pid, location)
    WHERE RR.id IS NULL
    ORDER BY AL.pid, AL.location;


------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------
