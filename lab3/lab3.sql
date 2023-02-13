-- SQL script to create the tables necessary for lab 2 in EDAF75.
-- MySQL version.
--
-- Creates the tables customers, tickets, theaters, movies and
-- populates them with (simulated) data.
--
-- We disable foreign key checks temporarily so we can delete the
-- tables in arbitrary order, and so insertion is faster.

PRAGMA foreign_keys = off;

-- Drop the tables if they already exist.

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  full_name     TEXT NOT NULL,
  username      TEXT NOT NULL,
  password      TEXT NOT NULL,
  PRIMARY KEY   (username)
);

DROP TABLE IF EXISTS tickets;
CREATE TABLE tickets (
  ticket_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
  performance_id    INTEGER NOT NULL,
  username          TEXT NOT NULL,
  PRIMARY KEY       (ticket_id),
  FOREIGN KEY       (performance_id) REFERENCES performances(performance_id) ON DELETE CASCADE,
  FOREIGN KEY       (username) REFERENCES customers(username) ON DELETE CASCADE
);

DROP TABLE IF EXISTS performances;
CREATE TABLE performances (
  performance_id                INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time                    TIME NOT NULL,
  performance_date              DATE NOT NULL,
  theater_name                  TEXT NOT NULL,
  imdb_key                      TEXT NOT NULL,
  FOREIGN KEY                   (theater_name) REFERENCES theaters(theater_name) ON DELETE CASCADE,
  FOREIGN KEY                   (imdb_key) REFERENCES movies(imdb_key) ON DELETE CASCADE
);

DROP TABLE IF EXISTS theaters;
CREATE TABLE theaters (
  theater_name    TEXT NOT NULL,
  capacity        INT NOT NULL,
  PRIMARY KEY     (theater_name)
);

DROP TABLE IF EXISTS movies;
CREATE TABLE movies (
  movie_name        TEXT NOT NULL,
  imdb_key          TEXT NOT NULL,
  running_time      INT,
  production_year   INT NOT NULL,
  PRIMARY KEY       (imdb_key)
);

-- We will do a lot of inserts, so we start a transaction to make it faster.

BEGIN TRANSACTION;

-- Populate the customers table.

INSERT OR REPLACE
INTO   customers(full_name, username, password)
VALUES ('Filip Lennhager','fi1234le','abc123'),
       ('Jonathan Do','jo1234do','123abc'),
       ('Felix Rödén','fe1234rö','lösenord');

-- Populate the tickets table.

INSERT OR REPLACE
INTO       tickets (performance_id, username)
VALUES  (1,'fi1234le'),
        (2,'fe1234rö'),
        (3,'jo1234do');

-- Populate the theaters table.

INSERT OR REPLACE
INTO   theaters(theater_name, capacity)
VALUES ('Lund', 100),
       ('Malmö', 200),
       ('Helsingborg', 175);

-- Populate the movies table.

INSERT OR REPLACE
INTO   movies(movie_name, imdb_key, running_time, production_year)
VALUES ('Alien', 'tt0078748', 117, 1979),
       ('Pulp Fiction', 'tt0110912', 154, 1994),
       ('Interstellar', 'tt0816692', 169, 2014);

-- Populate the performances table.

INSERT OR REPLACE
INTO   performances(start_time, performance_date, theater_name, imdb_key)
VALUES  ('12:00','2023-02-23','Lund', 'tt0078748'),
        ('15:00','2023-02-23','Lund', 'tt0110912'),
        ('18:00','2023-02-23','Lund', 'tt0816692'),
        ('19:30','2023-02-24','Malmö', 'tt0816692'),
        ('19:30','2023-02-24','Helsingborg', 'tt0816692'),
        ('19:30','2023-02-24','Lund', 'tt0816692');

-- Commit the transaction.


END TRANSACTION;

-- And re-enable foreign key checks.

PRAGMA foreign_key = on;

--Powershell promt, enter in terminal:
--Get-Content lab3.sql | & sqlite3 movies.sqlite