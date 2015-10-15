-- Table definitions for the catalog project.
--
-- Author: Alec Tietjens
-- Date: 10/14/2015

DROP DATABASE IF EXISTS catalog;

CREATE DATABASE catalog;

\c catalog;

CREATE TABLE category (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE item (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
    description TEXT NULL,
    image BYTEA NULL,
    category_id INT NOT NULL,
	FOREIGN KEY(category_id) REFERENCES category(id)
);