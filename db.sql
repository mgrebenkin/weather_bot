--
-- File generated with SQLiteStudio v3.3.3 on Сб июля 23 06:15:26 2022
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: subscribers
DROP TABLE IF EXISTS subscribers;
CREATE TABLE subscribers (user_id INTEGER UNIQUE PRIMARY KEY, user_name STRING, sending_time TIME DEFAULT ('20:00'));

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
