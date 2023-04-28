-- SQL script to create the tables necessary for the project in EDAF75.
-- SQLite3 version.
--
-- Creates the tables customers, tickets, theaters, movies 
--
-- We disable foreign key checks temporarily so we can delete the
-- tables in arbitrary order.

PRAGMA foreign_keys = off;

-- Drop the tables if they already exist.

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  customer_name         TEXT NOT NULL,
  address               TEXT NOT NULL,
  PRIMARY KEY           (customer_name)
);

DROP TABLE IF EXISTS cookies;
CREATE TABLE cookies (
  cookie_name         TEXT NOT NULL,
  PRIMARY KEY         (cookie_name)
);

DROP TABLE IF EXISTS recipes;
CREATE TABLE recipes (
  ingredient_amount     INT NOT NULL,
  cookie_name           TEXT NOT NULL,
  ingredient_name       TEXT NOT NULL,
  FOREIGN KEY           (cookie_name) REFERENCES cookies(cookie_name) ON DELETE CASCADE,
  FOREIGN KEY           (ingredient_name) REFERENCES ingredients(ingredient_name) ON DELETE CASCADE
);

DROP TABLE IF EXISTS ingredients;
CREATE TABLE ingredients (
  ingredient_name             TEXT NOT NULL,
  unit                        TEXT NOT NULL,
  stored_ingredient_amount    INT CHECK (stored_ingredient_amount >= 0),
  last_delivery_date          DATETIME,
  last_delivery_amount        INT,
  PRIMARY KEY                 (ingredient_name)
);

DROP TABLE IF EXISTS pallets;
CREATE TABLE pallets (
  pallet_id             TEXT DEFAULT (lower(hex(randomblob(16)))),
  cookie_name           TEXT NOT NULL,
  production_date       DATETIME,
  delivered_date        DATETIME,
  location              TEXT,
  blocked               BOOLEAN,
  PRIMARY KEY           (pallet_id),
  FOREIGN KEY           (cookie_name) REFERENCES cookies(cookie_name) ON DELETE CASCADE
);

DROP TABLE IF EXISTS requests;
CREATE TABLE requests (
  request_id        TEXT DEFAULT (lower(hex(randomblob(16)))),
  delivery_date     DATETIME NOT NULL,
  PRIMARY KEY       (request_id)
);

DROP TABLE IF EXISTS requestedCookies;
CREATE TABLE requestedCookies (
  cookie_amount        INT NOT NULL,
  request_id           TEXT NOT NULL,
  cookie_name          TEXT NOT NULL,
  FOREIGN KEY          (request_id) REFERENCES requests(request_id) ON DELETE CASCADE,
  FOREIGN KEY          (cookie_name) REFERENCES cookies(cookie_name) ON DELETE CASCADE
);


