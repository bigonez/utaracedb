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
    . Event
    . Category
    . Gender
    . Location
    . Status
*/

-- Event table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_event;
CREATE TABLE uta_event (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event    TEXT NOT NULL
);
INSERT INTO uta_event VALUES(1, '100');
INSERT INTO uta_event VALUES(5, 'Miler');

-- Category table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_category;
CREATE TABLE uta_category (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    category    TEXT NOT NULL
);
INSERT INTO uta_category VALUES(4, '18-19');
INSERT INTO uta_category VALUES(5, '20-34');
INSERT INTO uta_category VALUES(7, '35-39');
INSERT INTO uta_category VALUES(8, '40-44');
INSERT INTO uta_category VALUES(9, '45-49');
INSERT INTO uta_category VALUES(10, '50-54');
INSERT INTO uta_category VALUES(11, '55-59');
INSERT INTO uta_category VALUES(12, '60-64');
INSERT INTO uta_category VALUES(13, '65-69');
INSERT INTO uta_category VALUES(14, '70-74');
INSERT INTO uta_category VALUES(15, '75-79');

-- Gender table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_gender;
CREATE TABLE uta_gender (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    gender      TEXT NOT NULL,
    abbr        TEXT NOT NULL
);
INSERT INTO uta_gender VALUES(1, 'Male',   'M');
INSERT INTO uta_gender VALUES(2, 'Female', 'F');
INSERT INTO uta_gender VALUES(0, 'Unknown', 'U');

-- Location table ------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_location;
CREATE TABLE uta_location (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event       INTEGER NOT NULL,                                               --  event id
    location    INTEGER NOT NULL,                                               --  location id

    name        TEXT NOT NULL,
    abbr        TEXT,
    alias       TEXT,
    odometer    REAL NOT NULL,
    cuteoff     TEXT
);
-- locations for UTA100 ------------------------------------------------------------------------
INSERT INTO uta_location VALUES(NULL, 1, 1,  'Start',                 'Start',           'Scenic World',                0.0, '07:25');
INSERT INTO uta_location VALUES(NULL, 1, 2,  'Narrow Neck',           'Narrow Neck',     'Narrow Neck',                 2.8, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 3,  'Medow Gap',             'CP1',             'Medow Gap',                   16.7, '11:45');
INSERT INTO uta_location VALUES(NULL, 1, 4,  'Foggy Knob Arrive',     'CP2',             NULL,                          24.2, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 5,  'Foggy Knob Depart',     'CP2',             'Foggy Knob',                  24.2, '13:45');
INSERT INTO uta_location VALUES(NULL, 1, 6,  'Six Ft Track Arrive',   'CP3',             NULL,                          37.8, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 7,  'Six Ft Track Depart',   'CP3',             'Six Foot Track Outbound',     37.8, '16:35 ');
INSERT INTO uta_location VALUES(NULL, 1, 8,  'SIXFT-WP',              'SIXFT-WP',        'Six Foot Track WP',           46.0, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 9,  'Aquatic Centre Arrive', 'CP4',             NULL,                          56.5, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 10, 'Aquatic Centre Depart', 'CP4',             'Katoomba Aquatic Centre',     56.5, '21:35');
INSERT INTO uta_location VALUES(NULL, 1, 11, 'Cliff Drive',           'Cliff Drive',     'Cliff Drive',                 58.1, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 12, 'Echo Point',            'Echo Point',      'Echo Point',                  59.8, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 13, 'Gordon Falls',          'Gordon Falls',    'Gordon Falls',                65.3, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 14, 'Fairmount Arrive',      'CP5',             NULL,                          68.5, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 15, 'Fairmount Depart',      'CP5',             'Fairmount Resort',            68.5, '01:20');
INSERT INTO uta_location VALUES(NULL, 1, 16, 'QVH Arrive',            'CP6',             NULL,                          79.6, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 17, 'QVH Depart',            'CP6',             'Queen Victoria Hospital',     79.6, '05:10');
INSERT INTO uta_location VALUES(NULL, 1, 18, 'EAS-A',                 'EAS-A',           'Emergency Aid Station',       92.8, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 19, 'Treatment Works',       'Treatment Works', 'Treatment Works',             95.9, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 20, 'Furber Stairs',         'Furber Stairs',   'Furber Stairs',               100.4, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 21, 'BoardWalk',             'BoardWalk',       'BoardWalk',                   101.3, NULL);
INSERT INTO uta_location VALUES(NULL, 1, 22, 'Finish',                'Finish',          'Scenic World',                101.7, '11:42');
-- locations for UTA Miler ---------------------------------------------------------------------
INSERT INTO uta_location VALUES(NULL, 5, 1,  'Start',                 'Start',           'Grand Canyon Start',          0.0, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 2,  'Govett''s Leap',        'CP1',             'Govett''s Leap',              9.9, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 3,  'Perrys Lookdown',       'CP2',             'Perrys Lookdown',             16.7, '09:25');
INSERT INTO uta_location VALUES(NULL, 5, 4,  'Fortress Ridge',        'CP3',             'Fortress Ridge Trail Head',   27.4, '13:00');
INSERT INTO uta_location VALUES(NULL, 5, 5,  'Forress Ridge 2',       'CP3-2',           'Fortress Ridge Trail Head-2', 32.4, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 6,  'Hydro Majestic',        'CP4',             NULL,                          46.9, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 7,  'Hydro Majestic Dep',    'CP4',             'Hydro Majestic Hotel',        46.9, '18:00');
INSERT INTO uta_location VALUES(NULL, 5, 8,  'Narrow Neck',           'CP5',             'Narrow Neck',                 54.8, '20:00');
INSERT INTO uta_location VALUES(NULL, 5, 9,  'Medow Gap',             'CP6',             'Medow Gap',                   70.0, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 10, 'Foggy Knob Arr',        'CP7',             NULL,                          77.5, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 11, 'Foggy Knob Dep',        'CP7',             'Foggy Knob',                  77.5, '01:10');
INSERT INTO uta_location VALUES(NULL, 5, 12, 'Six Ft Track Arrive',   'CP8',             'Six Foot Track Outbound',     91.0, '05:00');
INSERT INTO uta_location VALUES(NULL, 5, 13, 'SIXFT-WP',              'SIXFT-WP',        'Six Foot Track WP',           106.4, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 14, 'Six Foot Arrive 2nd',   'CP9-2',           NULL,                          106.7, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 15, 'Six Foot Depart 2nd',   'CP9-2',           'Six Foot Track Inbound',      106.7, '09:00');
INSERT INTO uta_location VALUES(NULL, 5, 16, 'Aquatic Centre Arrive', 'CP10',            NULL,                          117.5, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 17, 'Aquatic Centre Depart', 'CP10',            'Katoomba Aquatic Centre',     117.5, '11:50');
INSERT INTO uta_location VALUES(NULL, 5, 18, 'Cliff Drive',           'Cliff Drive',     'Cliff Drive',                 119.1, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 19, 'Echo Point',            'Echo Point',      'Echo Point',                  120.7, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 20, 'Gordon Falls',          'Gordon Falls',    'Gordon Falls',                126.2, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 21, 'Fairmont Arrive',       'CP11',            NULL,                          129.4, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 22, 'Fairmont Depart',       'CP11',            'Fairmont Resort',             129.4, '15:35');
INSERT INTO uta_location VALUES(NULL, 5, 23, 'QVH Arrive',            'CP12',            NULL,                          140.5, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 24, 'QVH Depart',            'CP12',            'Queen Victoria Hospital',     140.5, '19:10');
INSERT INTO uta_location VALUES(NULL, 5, 25, 'EAS-Arr',               'EAS-Arr',         'Emergency Aid Station',       153.7, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 26, 'Treatment Works',       'Treatment Works', 'Treatment Works',             156.8, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 27, 'Furber',                'Furber',          'Furber',                      161.2, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 28, 'BoardWalk',             'BoardWalk',       'BoardWalk',                   162.2, NULL);
INSERT INTO uta_location VALUES(NULL, 5, 29, 'Finish',                'Finish',          'Scenic World',                162.8, '01:30');

-- Status table --------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_status;
CREATE TABLE uta_status (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    status      TEXT NOT NULL,
    abbr        TEXT NOT NULL
);
INSERT INTO uta_status VALUES(NULL, 'Finished', 'Finished');
INSERT INTO uta_status VALUES(NULL, 'Did Not Finish', 'DNF');
INSERT INTO uta_status VALUES(NULL, 'Did Not Start', 'DNS');


/*
    Athlete & Result Tables

    Tables:
    . Athlete
    . Result
*/

-- Athlete table -------------------------------------------------------------------------------
DROP TABLE IF EXISTS uta_athlete;
CREATE TABLE uta_athlete (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event       INTEGER NOT NULL,                                               --  event id

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
DROP TABLE IF EXISTS uta_racelog;
CREATE TABLE uta_racelog (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,                              --  Id

    event       INTEGER NOT NULL,                                               --  event id

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
DROP VIEW IF EXISTS uta_athlete_location;
CREATE VIEW uta_athlete_location AS
    SELECT A.id AS pid, A.event AS event, bib, L.location AS location, L.name AS name, odometer
    FROM uta_location AS L
    JOIN uta_athlete AS A
    WHERE A.status = 1 AND A.event = L.event
    ORDER BY pid, location;

-- Race Logged Record with Full Location view --------------------------------------------------
DROP VIEW IF EXISTS uta_full_racelog;
CREATE VIEW uta_full_racelog AS
    SELECT AL.*, splittime, splitstamp, racetime, racestamp, tpos, cpos, gpos, speed, pace, todtime, todstamp
    FROM uta_athlete_location AS AL
    LEFT JOIN uta_racelog AS RR
    USING (pid, location)
    ORDER BY AL.pid, AL.location;

-- Missing Race Record view --------------------------------------------------------------------
DROP VIEW IF EXISTS uta_missing_racelog;
CREATE VIEW uta_missing_racelog AS
    SELECT AL.*, splittime, splitstamp, racetime, racestamp, todtime, todstamp FROM uta_athlete_location AS AL
    LEFT JOIN uta_racelog AS RR
    USING (pid, location)
    WHERE RR.id IS NULL
    ORDER BY AL.pid, AL.location;

-- Race Time Proportion of each athlete x middle location --------------------------------------
DROP VIEW IF EXISTS uta_racelog_proportion;
CREATE VIEW uta_racelog_proportion AS
    SELECT C.event, C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta_full_racelog AS P, uta_full_racelog AS C, uta_full_racelog AS N
      WHERE P.event = C.event AND C.event = N.event AND P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.event, C.location, C.pid;

-- Race Time Proportion's Mean of each middle location -----------------------------------------
DROP VIEW IF EXISTS uta_racelog_mean;
CREATE VIEW uta_racelog_mean AS
    SELECT event, location, COUNT(pid) AS total, AVG(proportion) AS mean
    FROM uta_racelog_proportion
    GROUP BY event, location;

-- Race Time Proportion's Standard Deviation of each middle location ---------------------------
DROP VIEW IF EXISTS uta_racelog_std;
CREATE VIEW uta_racelog_std AS
    SELECT lm.event AS event, lm.location AS location, lm.total AS total, lm.mean AS mean, SQRT(SUM(sq)/total) AS std
    FROM uta_racelog_mean AS lm
    LEFT JOIN
     (SELECT P.event, P.location, pid, proportion, mean, (proportion - mean) * (proportion - mean) AS sq
      FROM uta_racelog_proportion AS P
      JOIN uta_racelog_mean AS M
      WHERE P.event = M.event AND P.location = M.location) AS sq
    ON lm.event = sq.event AND lm.location = sq.location
    GROUP BY lm.event, lm.location;

-- Log Error Detaction by 6 times of stanard deviation -----------------------------------------
DROP VIEW IF EXISTS uta_racelog_error;
CREATE VIEW uta_racelog_error AS
    SELECT pid, P.event, P.location, proportion, mean, std,
      proportion - mean AS ldiff,
      mean - std * 6.0 AS lmin, mean + std * 6.0 AS lmax,
      proportion < (mean - std * 6.0) OR proportion > (mean + std * 6.0) AS oor
    FROM uta_racelog_proportion AS P
    LEFT JOIN uta_racelog_std AS S
    ON P.event = S.event AND P.location = S.location
    WHERE oor = 1 ORDER BY pid, P.event, P.location;

-- Changes between the original log and the repaired dataset -----------------------------------
DROP VIEW IF EXISTS uta_repair_changes;
CREATE VIEW uta_repair_changes AS
    SELECT RL.pid, RL.location,
        RL.splittime AS Ast, RL.splitstamp AS Ass,
        FR.splittime AS Bst, FR.splitstamp AS Bss,
        RL.racetime AS Art, RL.racestamp AS Ars,
        FR.racetime AS Brt, FR.racestamp AS Brs, FR.racestamp - RL.racestamp AS Drs,
        RL.todtime AS Att, RL.todstamp AS Ats,
        FR.todtime AS Btt, FR.todstamp AS Bts
    FROM uta_finalresult AS FR, uta_full_racelog AS RL
    WHERE RL.pid = FR.pid AND RL.location = FR.location AND
        (FR.racestamp <> RL.racestamp OR FR.splitstamp <> RL.splitstamp OR RL.racestamp IS NULL);

-- proportion data based on the final race result ----------------------------------------------
DROP VIEW IF EXISTS uta_final_proportion;
CREATE VIEW uta_final_proportion AS
    SELECT C.event, C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta_finalresult AS P, uta_finalresult AS C, uta_finalresult AS N
      WHERE P.event = C.event AND C.event = N.event AND P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.event, C.location, C.pid;

-- Final Proportion's Mean of each middle location ---------------------------------------------
DROP VIEW IF EXISTS uta_final_mean;
CREATE VIEW uta_final_mean AS
    SELECT event, location, COUNT(pid) AS total, AVG(proportion) AS mean
    FROM uta_final_proportion
    GROUP BY event, location;

-- Final Proportion's Standard Deviation of each middle location -------------------------------
DROP VIEW IF EXISTS uta_final_std;
CREATE VIEW uta_final_std AS
    SELECT lm.event AS event, lm.location AS location, lm.total AS total, lm.mean AS mean, SQRT(SUM(sq)/total) AS std
    FROM uta_final_mean AS lm
    LEFT JOIN
     (SELECT P.event, P.location, pid, proportion, mean, (proportion - mean) * (proportion - mean) AS sq
      FROM uta_final_proportion AS P
      JOIN uta_final_mean AS M
      WHERE P.event = M.event AND P.location = M.location) AS sq
    ON lm.event = sq.event AND lm.location = sq.location
    GROUP BY lm.event, lm.location;


------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------
