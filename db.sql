--
-- File generated with SQLiteStudio v3.3.3 on Вт авг. 2 21:05:01 2022
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: FSMData
DROP TABLE IF EXISTS FSMData;
CREATE TABLE FSMData (chat TEXT, user TEXT PRIMARY KEY UNIQUE, state TEXT, lat REAL, lon REAL, sending_time TEXT);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
