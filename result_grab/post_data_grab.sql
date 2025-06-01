/*
////////////////////////////////////////////////////////////////////////////////////////////////
//  Ultra-Trail Australia 2025 Race Result Dataset
////////////////////////////////////////////////////////////////////////////////////////////////
*/

------------------------------------------------------------------------------------------------
BEGIN TRANSACTION;
------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS uta_finalresult
  AS SELECT * FROM uta_full_racelog;

DROP TABLE IF EXISTS uta_racelog;

DROP VIEW IF EXISTS uta_athlete_location;
DROP VIEW IF EXISTS uta_full_racelog;
DROP VIEW IF EXISTS uta_missing_racelog;
DROP VIEW IF EXISTS uta_racelog_proportion;
DROP VIEW IF EXISTS uta_racelog_mean;
DROP VIEW IF EXISTS uta_racelog_std;
DROP VIEW IF EXISTS uta_racelog_error;
DROP VIEW IF EXISTS uta_repair_changes;

------------------------------------------------------------------------------------------------
END TRANSACTION;
------------------------------------------------------------------------------------------------

VACUUM;
