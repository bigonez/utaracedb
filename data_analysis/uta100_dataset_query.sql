-- Form the 3D surface dataset

SELECT pid, odometer, racestamp, racetime FROM uta100_racelog AS RR
LEFT JOIN uta100_location AS L
ON RR.location = L.id
WHERE pid <= 834 ORDER BY RR.id

-- or

SELECT pid, odometer, RR.racestamp AS racestamp, RR.racetime AS racetime FROM uta100_racelog AS RR
LEFT JOIN uta100_location AS L ON RR.location = L.id
LEFT JOIN uta100_athlete AS A ON RR.pid = A.id
WHERE status = 1 ORDER BY RR.pid, RR.location

-- final

SELECT pid, location, odometer, RR.racestamp AS racestamp FROM uta100_racelog AS RR
LEFT JOIN uta100_location AS L ON RR.location = L.id
LEFT JOIN uta100_athlete AS A ON RR.pid = A.id
WHERE status = 1 ORDER BY RR.pid, RR.location


-- missing location stat

SELECT pid, COUNT(pid) AS logs
FROM (
	SELECT pid, location, odometer, RR.racestamp AS racestamp FROM uta100_racelog AS RR
	LEFT JOIN uta100_location AS L ON RR.location = L.id
	LEFT JOIN uta100_athlete AS A ON RR.pid = A.id
	WHERE status = 1 ORDER BY RR.pid, RR.location
) GROUP BY pid HAVING logs < 20


-- find the missing location

SELECT L.id AS lid, odometer, name, pid, racetime, racestamp  FROM uta100_location AS L
LEFT JOIN (SELECT * FROM uta100_racelog WHERE pid=1) AS RR
ON lid = location

SELECT L.id AS lid, odometer, name, pid, racetime, racestamp  FROM uta100_location AS L
LEFT JOIN (SELECT * FROM uta100_racelog WHERE pid=1) AS RR
ON lid = location
WHERE pid IS NULL


-- create the combination of athlete & location
DROP VIEW IF EXISTS uta100_athlete_location;
CREATE VIEW uta100_athlete_location AS
    SELECT A.id AS pid, bib, L.id AS location, L.name AS cpname, odometer
    FROM uta100_location AS L
    JOIN uta100_athlete AS A
    WHERE A.status = 1
    ORDER BY pid, location;

-- discover the missing race result
DROP VIEW IF EXISTS uta100_missing_racelog;
CREATE VIEW uta100_missing_racelog AS
    SELECT AL.*, racetime, racestamp FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_racelog AS RR
    USING (pid, location)
    WHERE RR.id IS NULL
    ORDER BY AL.pid, AL.location;

-- form the race result with full location
DROP VIEW IF EXISTS uta100_full_racelog;
CREATE VIEW uta100_full_racelog AS
    SELECT AL.*, RR.splittime, splitstamp, racetime, racestamp, tpos, cpos, gpos, speed, pace, todtime, todstamp
    FROM uta100_athlete_location AS AL
    LEFT JOIN uta100_racelog AS RR
    USING (pid, location)
    ORDER BY AL.pid, AL.location;

-- calculate the timestamp proportion on three continous locations (no null) for each athlete
--	it will be used to estimate the mission timestamp of location
SELECT C.location, C.pid,
	C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
	(C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS stampPercent
FROM uta100_full_racelog AS P, uta100_full_racelog AS C, uta100_full_racelog AS N
WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
	AND cpStamp NOT NULL AND npStamp NOT NULL
ORDER BY C.location, C.pid;

-- estimate the average proportion on each location
SELECT location, COUNT(pid) AS total, AVG(stampPercent) AS avgpercent
FROM (SELECT C.location, C.pid,
    C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
    (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS stampPercent
  FROM uta100_full_racelog AS P, uta100_full_racelog AS C, uta100_full_racelog AS N
  WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
  AND cpStamp NOT NULL AND npStamp NOT NULL
  ORDER BY C.location, C.pid)
GROUP BY location;

DROP VIEW IF EXISTS uta100_racelog_proportion;
CREATE VIEW uta100_racelog_proportion AS
    SELECT C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta100_full_racelog AS P, uta100_full_racelog AS C, uta100_full_racelog AS N
      WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.location, C.pid;

DROP VIEW IF EXISTS uta100_racelog_mean;
CREATE VIEW uta100_racelog_mean AS
    SELECT location, COUNT(pid) AS total, AVG(proportion) AS mean
    FROM uta100_racelog_proportion
    GROUP BY location;

DROP VIEW IF EXISTS uta100_racelog_std;
CREATE VIEW uta100_racelog_std AS
    SELECT lm.location AS location, lm.total AS ltotal, lm.mean AS lmean, SQRT(SUM(sq)/total) AS lstd
    FROM uta100_racelog_mean AS lm
    LEFT JOIN
     (SELECT P.location, pid, proportion, mean, (proportion - mean) * (proportion - mean) AS sq
      FROM uta100_racelog_proportion AS P
      JOIN uta100_racelog_mean AS M
      WHERE P.location = M.location) AS sq
    ON lm.location = sq.location
    GROUP BY lm.location;

-- Error Detaction, if oor = 1, consider an error
DROP VIEW IF EXISTS uta100_racelog_error;
CREATE VIEW uta100_racelog_error AS
    SELECT pid, P.location, proportion, lmean, lstd,
      proportion - lmean AS ldiff,
      lmean - lstd * 3.0 AS lmin, lmean + lstd * 3.0 AS lmax,
      proportion < (lmean - lstd * 6.0) OR proportion > (lmean + lstd * 6.0) AS oor
    FROM uta100_racelog_proportion AS P
    LEFT JOIN uta100_racelog_std AS S
    ON P.location = S.location
    WHERE oor = 1 ORDER BY pid, P.location;

-- general query the race result
SELECT pid, location, odometer, IFNULL(racestamp, -99) AS racestamp FROM uta100_full_racelog

-- list the race result need to be repaired
DROP TABLE IF EXISTS uta100_racelog_est;
CREATE TABLE uta100_racelog_est AS
    SELECT * FROM uta100_full_racelog WHERE racestamp IS NULL;

-- create the table of full combination of athlete X location with the repaired time data
DROP TABLE IF EXISTS uta100_finalresult;
CREATE TABLE IF NOT EXISTS uta100_finalresult AS
    SELECT * FROM uta100_full_racelog;

-- the comparison between the original log and the repaired dataset
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

DROP VIEW IF EXISTS uta100_final_proportion;
CREATE VIEW uta100_final_proportion AS
    SELECT C.location, C.pid,
        C.racestamp - P.racestamp AS cpStamp, N.racestamp - P.racestamp AS npStamp,
        (C.racestamp - P.racestamp) * 1.0 / (N.racestamp - P.racestamp) AS proportion
      FROM uta100_finalresult AS P, uta100_finalresult AS C, uta100_finalresult AS N
      WHERE P.pid = C.pid AND C.pid = N.pid AND P.location = C.location - 1 AND N.location = C.location + 1
      AND cpStamp NOT NULL AND npStamp NOT NULL
      ORDER BY C.location, C.pid;
