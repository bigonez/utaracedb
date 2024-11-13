/*
////////////////////////////////////////////////////////////////////////////////////////////////
//  UTA 100 2024 Race Result Dataset
////////////////////////////////////////////////////////////////////////////////////////////////
*/

------------------------------------------------------------------------------------------------
BEGIN TRANSACTION;
------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS uta100_finalresult
  AS SELECT * FROM uta100_full_racelog;

DROP TABLE IF EXISTS uta100_racelog;

DROP VIEW IF EXISTS uta100_athlete_location;
DROP VIEW IF EXISTS uta100_full_racelog;
DROP VIEW IF EXISTS uta100_missing_racelog;
DROP VIEW IF EXISTS uta100_racelog_proportion;
DROP VIEW IF EXISTS uta100_racelog_mean;
DROP VIEW IF EXISTS uta100_racelog_std;
DROP VIEW IF EXISTS uta100_racelog_error;
DROP VIEW IF EXISTS uta100_repair_changes;

------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------

VACUUM;
